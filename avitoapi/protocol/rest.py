"""Default REST protocol — path templating, verb routing, JSON encode/decode."""

from __future__ import annotations

import hashlib
import json
from datetime import timedelta
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from ..exceptions import (
    MethodDeclarationError,
    PathResolutionError,
    ResponseDecodingError,
)
from .base import Protocol

if TYPE_CHECKING:
    from ..methods._base import BaseMethod
    from ..sessions._models import PreparedRequest, RawResponse, RequestContext


_IDEMPOTENT_VERBS: frozenset[str] = frozenset({"GET", "HEAD", "OPTIONS"})
_BODYLESS_VERBS: frozenset[str] = frozenset({"GET", "HEAD", "DELETE", "OPTIONS"})


class RestProtocol(Protocol):
    """Conventional REST: ``__http_method__`` + ``__endpoint__`` + field routing.

    Routing rules (overridable per method-class):

    * ``__path_fields__`` — fill ``{name}`` placeholders in the endpoint.
    * ``__query_fields__`` — explicit override; default routes by verb.
    * ``__body_fields__`` — explicit override; default routes by verb.
    * GET / HEAD / DELETE / OPTIONS — non-path fields go to query.
    * POST / PUT / PATCH — non-path fields go to the JSON body.

    Auto-injects ``Idempotency-Key`` for any method-class with
    ``__idempotent_mutation__ = True``. The key is derived from a stable hash
    of the method payload and cached in storage for 24h so retries reuse the same
    value across process restarts.
    """

    @classmethod
    def validate_subclass(cls, method_cls: type[BaseMethod[Any]]) -> None:
        http_method = getattr(method_cls, "__http_method__", None)
        endpoint = getattr(method_cls, "__endpoint__", None)
        if http_method is None or endpoint is None:
            return
        if not isinstance(http_method, str) or http_method.upper() != http_method:
            raise MethodDeclarationError(
                f"{method_cls.__name__}: __http_method__ must be an uppercase string",
            )
        if not endpoint.startswith("/"):
            raise MethodDeclarationError(
                f"{method_cls.__name__}: __endpoint__ must start with '/' (got {endpoint!r})",
            )
        if getattr(method_cls, "__pre_encoded_fields__", frozenset()):
            cls._check_validators_for_pre_encoded(method_cls)

    @staticmethod
    def _check_validators_for_pre_encoded(method_cls: type[BaseMethod[Any]]) -> None:
        decorators = getattr(method_cls, "__pydantic_decorators__", None)
        validators = getattr(decorators, "field_validators", {}) if decorators else {}
        validated = {
            field
            for decorator in validators.values()
            for field in getattr(decorator.info, "fields", ())
        }
        missing = set(method_cls.__pre_encoded_fields__) - validated
        if missing:
            raise MethodDeclarationError(
                f"{method_cls.__name__}: __pre_encoded_fields__={sorted(missing)} "
                "declared but no matching field_validator found.",
            )

    async def build_request(
        self,
        method: BaseMethod[Any],
        ctx: RequestContext,
    ) -> PreparedRequest:
        from ..sessions._models import PreparedRequest
        from ..types import HostKey

        config = ctx.client.config
        host = HostKey(method.__host__)

        http_method = self._get_http_method(method)
        endpoint = self._get_endpoint(method)
        payload = self._dump(method)

        path = self._render_path(method, endpoint, payload)
        query, body = self._route_fields(method, http_method, payload)

        base_url = config.base_url(host)
        url = f"{base_url}{path}"
        prepared = PreparedRequest(
            host=str(host),
            http_method=http_method,
            url=url,
            query=query,
            body=body,
            timeout_s=config.request_timeout_s,
            method_name=type(method).__name__,
        )

        if getattr(method, "__idempotent_mutation__", False):
            prepared.headers["Idempotency-Key"] = await self._idempotency_key(method, ctx)
        return prepared

    def decode_response(
        self,
        method: BaseMethod[Any],
        raw: RawResponse,
    ) -> Any:
        returning = method.__returning__
        if returning is None:
            return None
        if getattr(method, "__binary_response__", False):
            return raw.body
        if not raw.body:
            return None
        try:
            return returning.model_validate_json(raw.body)
        except json.JSONDecodeError as exc:
            raise ResponseDecodingError(
                f"{type(method).__name__}: response body is not valid JSON",
            ) from exc
        except Exception as exc:
            raise ResponseDecodingError(
                f"{type(method).__name__}: response did not match {returning.__name__}",
            ) from exc

    def is_idempotent(self, method: BaseMethod[Any]) -> bool:
        if getattr(method, "__retry_safe__", False):
            return True
        return self._get_http_method(method) in _IDEMPOTENT_VERBS

    @staticmethod
    def _get_http_method(method: BaseMethod[Any]) -> str:
        verb = method.__http_method__
        if verb is None:
            raise MethodDeclarationError(
                f"{type(method).__name__}: missing __http_method__",
            )
        return verb

    @staticmethod
    def _get_endpoint(method: BaseMethod[Any]) -> str:
        endpoint = method.__endpoint__
        if endpoint is None:
            raise MethodDeclarationError(
                f"{type(method).__name__}: missing __endpoint__",
            )
        return endpoint

    @staticmethod
    def _dump(method: BaseMethod[Any]) -> dict[str, Any]:
        data = method.model_dump(mode="json", exclude_none=True, by_alias=False)
        return {k: v for k, v in data.items() if not k.startswith("_")}

    @staticmethod
    def _render_path(
        method: BaseMethod[Any],
        endpoint: str,
        payload: dict[str, Any],
    ) -> str:
        path_fields = method.__path_fields__
        if not path_fields:
            return endpoint
        try:
            rendered = endpoint.format_map({name: payload[name] for name in path_fields})
        except KeyError as exc:
            missing = exc.args[0]
            raise PathResolutionError(
                f"{type(method).__name__}: missing field {missing!r} for path {endpoint!r}",
            ) from exc
        return rendered

    @staticmethod
    def _route_fields(
        method: BaseMethod[Any],
        http_method: str,
        payload: dict[str, Any],
    ) -> tuple[dict[str, Any], Any]:
        remaining = {k: v for k, v in payload.items() if k not in method.__path_fields__}
        if method.__query_fields__ is not None or method.__body_fields__ is not None:
            query = {
                k: v
                for k, v in remaining.items()
                if method.__query_fields__ and k in method.__query_fields__
            }
            body_fields = method.__body_fields__
            body_dict = (
                {k: v for k, v in remaining.items() if body_fields and k in body_fields}
                if body_fields
                else None
            )
            return query, (body_dict if body_dict else None)

        if http_method in _BODYLESS_VERBS:
            return remaining, None
        return {}, (remaining if remaining else None)

    @staticmethod
    async def _idempotency_key(
        method: BaseMethod[Any],
        ctx: RequestContext,
    ) -> str:
        body_hash = hashlib.sha256(
            method.model_dump_json(exclude={"_client"}).encode(),
        ).hexdigest()[:16]
        cache_key = f"{type(method).__name__}:{body_hash}"
        store = ctx.client.storage.namespaced("idempotency")
        cached = await store.get(cache_key)
        if cached:
            return str(cached)
        key = uuid4().hex
        await store.put(cache_key, key, ttl=timedelta(hours=24))
        return key

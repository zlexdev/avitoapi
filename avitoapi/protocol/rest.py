"""Default REST protocol — path templating, verb routing, JSON encode/decode."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import timedelta
from typing import (  # typed-Any: BaseMethod[Any] = heterogeneous method holder (return type erased at protocol layer)
    TYPE_CHECKING,
    Any,
)
from uuid import uuid4

from ..exceptions import (
    MethodDeclarationError,
    PathResolutionError,
    ResponseDecodingError,
)
from ..types import JsonObject
from .base import Protocol

if TYPE_CHECKING:
    from ..methods._base import BaseMethod
    from ..sessions._models import PreparedRequest, RawResponse, RequestContext


_IDEMPOTENT_VERBS: frozenset[str] = frozenset({"GET", "HEAD", "OPTIONS"})
_BODYLESS_VERBS: frozenset[str] = frozenset({"GET", "HEAD", "DELETE", "OPTIONS"})


class RestProtocol(Protocol):
    """Conventional REST: ``__http_method__`` + ``__endpoint__`` + field routing.

    Routing rules:

    * Path fields are derived from ``{name}`` placeholders in ``__endpoint__`` — the
      method-class needs a field per placeholder; no ``__path_fields__`` declaration.
    * Path values are dumped by field name; query/body by alias (so camelCase wire names
      from the spec are honoured), with the path fields excluded.
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
        path_names = self._path_fields(endpoint)

        path = self._render_path(method, endpoint, path_names)
        query, body = self._route_fields(method, http_method, path_names)

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
        if getattr(method, "__binary_response__", False):
            return raw.body
        returning = method.__returning__
        if returning is None:
            return None
        if not raw.body:
            return None
        try:
            return returning.model_validate_json(raw.body)
        except json.JSONDecodeError as exc:
            raise ResponseDecodingError(
                f"{type(method).__name__}: response body is not valid JSON",
            ) from exc
        except Exception as exc:  # noqa: BLE001 — decode boundary: re-raised as ResponseDecodingError
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
    def _path_fields(endpoint: str) -> tuple[str, ...]:
        """Field names filling ``{placeholder}`` segments of the endpoint template."""

        return tuple(re.findall(r"{(\w+)}", endpoint))

    @staticmethod
    def _render_path(
        method: BaseMethod[Any],
        endpoint: str,
        path_names: tuple[str, ...],
    ) -> str:
        if not path_names:
            return endpoint
        # path segments use the python field name (by_alias=False), never the wire alias
        values = method.model_dump(mode="json", by_alias=False, include=set(path_names))
        try:
            return endpoint.format_map(values)
        except KeyError as exc:
            missing = exc.args[0]
            raise PathResolutionError(
                f"{type(method).__name__}: missing field {missing!r} for path {endpoint!r}",
            ) from exc

    @staticmethod
    def _route_fields(
        method: BaseMethod[Any],
        http_method: str,
        path_names: tuple[str, ...],
    ) -> tuple[JsonObject, Any]:
        # query/body use wire aliases; path fields are excluded by field name
        data = method.model_dump(mode="json", exclude_none=True, by_alias=True, exclude=set(path_names))
        remaining = {k: v for k, v in data.items() if not k.startswith("_")}
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

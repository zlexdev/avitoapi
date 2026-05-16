"""OAuth2 client for the Avito Partner API + bearer-token injector middleware."""
from __future__ import annotations

import asyncio
import json
import re
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel, ConfigDict, SecretStr

from ..exceptions import ForbiddenError, TokenIssuanceFailed, http_error_for_status
from ..logging import get_logger
from ..sessions._models import PreparedRequest, RawResponse, RequestContext
from ..sessions.middleware import RequestHandler, RequestMiddleware
from ..types import HostKey

if TYPE_CHECKING:
    from ..config import ClientConfig
    from ..sessions.base import BaseSession
    from ..storage.base import BaseStorage

log = get_logger(__name__)

_TOKEN_PATH = "/token"
_TOKEN_EXPIRED_RE = re.compile(rb"token[_\s-]?expired", re.IGNORECASE)
_REFRESH_LEEWAY = timedelta(seconds=60)


class Token(BaseModel):
    """OAuth2 access token plus absolute expiry."""

    model_config = ConfigDict(strict=True, frozen=True)

    access_token: SecretStr
    token_type: Literal["Bearer"] = "Bearer"
    expires_at: datetime
    refresh_token: SecretStr | None = None
    scope: frozenset[str] = frozenset()

    def is_expired(self, *, leeway: timedelta = _REFRESH_LEEWAY) -> bool:
        return datetime.now(UTC) + leeway >= self.expires_at


class TokenCache:
    """Wraps :class:`BaseStorage` with token-shaped serialisation."""

    def __init__(self, storage: BaseStorage[Any, str]) -> None:
        self._storage = storage.namespaced("oauth")

    async def get(self, key: str) -> Token | None:
        raw = await self._storage.get(key)
        if raw is None:
            return None
        try:
            return Token.model_validate(raw)
        except Exception:
            await self._storage.delete(key)
            return None

    async def put(self, key: str, token: Token) -> None:
        ttl_seconds = (token.expires_at - datetime.now(UTC)).total_seconds()
        ttl = timedelta(seconds=max(1.0, ttl_seconds))
        await self._storage.put(key, self._serialize(token), ttl=ttl)

    @staticmethod
    def _serialize(token: Token) -> dict[str, Any]:
        """``SecretStr`` masks itself in ``model_dump`` — round-trip it explicitly.

        Keep native types (``datetime``, ``str``, ``frozenset``) so
        :meth:`Token.model_validate` succeeds under strict mode.
        """
        return {
            "access_token": token.access_token.get_secret_value(),
            "token_type": token.token_type,
            "expires_at": token.expires_at,
            "refresh_token": (
                token.refresh_token.get_secret_value() if token.refresh_token else None
            ),
            "scope": token.scope,
        }

    async def invalidate(self, key: str) -> None:
        await self._storage.delete(key)


class OAuthClient:
    """Issues + refreshes Avito Partner API bearer tokens.

    Supports both grants from W1:

    * ``client_credentials`` — single-tenant bots (server-to-server).
    * ``authorization_code`` — multi-tenant dashboards. Requires
      ``ClientConfig.redirect_uri`` and a ``state`` round-trip.

    Stores tokens in :class:`TokenCache`. Refresh fires when ≤60 s remain
    on the access token, or eagerly on a 403 ``token_expired`` body.
    """

    def __init__(
        self,
        config: ClientConfig,
        http: BaseSession,
        cache: TokenCache,
    ) -> None:
        self.config = config
        self.http = http
        self.cache = cache

    async def issue_client_credentials(self) -> Token:
        """Exchange (client_id, client_secret) for a bearer token and cache it."""

        payload = {
            "grant_type": "client_credentials",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret.get_secret_value(),
        }
        token = await self._post_token(payload)
        await self.cache.put(self.cache_key_for(), token)
        return token

    async def issue_authorization_code(self, code: str, *, state: str) -> Token:
        """Exchange an authorization code (from the OAuth redirect) for a bearer token."""

        if self.config.redirect_uri is None:
            raise TokenIssuanceFailed(
                "authorization_code grant requires ClientConfig.redirect_uri",
            )
        payload = {
            "grant_type": "authorization_code",
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret.get_secret_value(),
            "code": code,
            "redirect_uri": str(self.config.redirect_uri),
            "state": state,
        }
        token = await self._post_token(payload)
        await self.cache.put(self.cache_key_for(user_id=self.config.user_id), token)
        return token

    def cache_key_for(self, *, user_id: int | None = None) -> str:
        """Stable cache key for the (client_id, user_id?) pair.

        client_credentials → ``oauth:<client_id>``;
        authorization_code → ``oauth:<client_id>:<user_id>``.
        """
        if user_id is None:
            return f"oauth:{self.config.client_id}"
        return f"oauth:{self.config.client_id}:{user_id}"

    async def refresh_if_needed(self, token: Token) -> Token:
        """Refresh when ≤60 s remaining or already expired; else return ``token`` as-is."""

        if not token.is_expired():
            return token
        return await self.issue_client_credentials()

    @staticmethod
    def is_token_expired_403(body: bytes | str | None) -> bool:
        """Match Avito's 403 + ``token_expired`` body heuristic. Case-insensitive."""

        if not body:
            return False
        data = body.encode() if isinstance(body, str) else body
        return bool(_TOKEN_EXPIRED_RE.search(data))

    async def _post_token(self, payload: dict[str, str]) -> Token:
        base = self.config.base_url(HostKey("www"))
        url = f"{base}{_TOKEN_PATH}"
        prepared = self._build_token_request(url, payload)
        raw = await self.http._send(prepared)
        if not (200 <= raw.status < 300):
            error_cls = http_error_for_status(raw.status)
            raise TokenIssuanceFailed(
                f"OAuth token endpoint returned {raw.status}: {raw.body[:200]!r}",
            ) from error_cls(body=raw.body, status=raw.status)
        return self._parse_token(raw)

    def _build_token_request(
        self,
        url: str,
        payload: dict[str, str],
    ) -> PreparedRequest:
        if self.config.oauth_grant_endpoint == "get_query":
            return PreparedRequest(
                host="www",
                http_method="GET",
                url=url,
                headers={
                    "Accept": "application/json",
                    "User-Agent": self.config.user_agent,
                },
                query=dict(payload),
                timeout_s=self.config.request_timeout_s,
            )
        body = "&".join(
            f"{k}={_form_quote(v)}" for k, v in payload.items()
        )
        return PreparedRequest(
            host="www",
            http_method="POST",
            url=url,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "User-Agent": self.config.user_agent,
            },
            body=body,
            timeout_s=self.config.request_timeout_s,
        )

    @staticmethod
    def _parse_token(raw: RawResponse) -> Token:
        try:
            data = json.loads(raw.body)
        except json.JSONDecodeError as exc:
            raise TokenIssuanceFailed(
                f"OAuth token endpoint returned non-JSON: {raw.body[:200]!r}",
            ) from exc
        access = data.get("access_token")
        expires_in = int(data.get("expires_in", 0))
        if not access or expires_in <= 0:
            raise TokenIssuanceFailed(f"OAuth response missing required fields: {data}")
        expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)
        scope = data.get("scope") or ""
        scope_set = frozenset(scope.split()) if isinstance(scope, str) else frozenset()
        refresh = data.get("refresh_token")
        return Token(
            access_token=SecretStr(access),
            expires_at=expires_at,
            refresh_token=SecretStr(refresh) if refresh else None,
            scope=scope_set,
        )


def _form_quote(value: str) -> str:
    from urllib.parse import quote_plus

    return quote_plus(value)


class OAuthInjectorMiddleware(RequestMiddleware):
    """Inject ``Authorization: Bearer <token>`` on every request.

    Refreshes the cached token when ≤60 s remain. On 403 with
    ``token_expired`` body: invalidate, refresh, retry the request once.
    Per-key ``asyncio.Lock`` prevents thundering-herd refresh on cold start.
    """

    def __init__(
        self,
        oauth: OAuthClient,
        cache_key_builder: Callable[[Any], str],
    ) -> None:
        self.oauth = oauth
        self._cache_key_builder = cache_key_builder
        self._locks: dict[str, asyncio.Lock] = {}

    async def __call__(
        self,
        handler: RequestHandler,
        prepared: PreparedRequest,
        ctx: RequestContext,
    ) -> RawResponse:
        cache_key = self._cache_key_builder(ctx.client)
        token = await self._ensure_token(cache_key)
        prepared.headers["Authorization"] = f"Bearer {token.access_token.get_secret_value()}"
        try:
            return await handler(prepared, ctx)
        except ForbiddenError as exc:
            if not OAuthClient.is_token_expired_403(exc.body):
                raise
            log.info("oauth.token_expired_403", cache_key=cache_key)
            await self.oauth.cache.invalidate(cache_key)
            refreshed = await self._ensure_token(cache_key, force=True)
            prepared.headers["Authorization"] = (
                f"Bearer {refreshed.access_token.get_secret_value()}"
            )
            return await handler(prepared, ctx)

    async def _ensure_token(self, cache_key: str, *, force: bool = False) -> Token:
        lock = self._locks.setdefault(cache_key, asyncio.Lock())
        async with lock:
            cached = None if force else await self.oauth.cache.get(cache_key)
            if cached is not None and not cached.is_expired():
                return cached
            return await self.oauth.issue_client_credentials()

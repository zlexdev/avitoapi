"""``BaseSession`` — the funnel every HTTP call goes through."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from uuid import uuid4

from structlog.contextvars import bind_contextvars, clear_contextvars

from ..exceptions import (
    AvitoConnectionError,
    AvitoTimeoutError,
    ErrorContext,
    ProxyAuthError,
    ProxyConnectionError,
    ProxyError,
    ProxyTimeoutError,
    ProxyTLSError,
    SDKError,
    TLSError,
)
from ..logging import get_logger
from ..models._base import _AvitoClientMixin
from ..transport.retry import RetryPolicy
from ._models import PreparedRequest, RawResponse, RequestContext
from .headers_middleware import DefaultHeadersMiddleware
from .middleware import RequestMiddlewareManager
from .retry_middleware import RetryMiddleware

if TYPE_CHECKING:
    from ..client import Client
    from ..config import ClientConfig
    from ..methods._base import BaseMethod
    from ..transport.proxy._base import BaseProxyTransport, Proxy

log = get_logger(__name__)


class BaseSession(ABC):
    """Single algorithm of one HTTP request. Subclasses implement ``_send`` only.

    Owns: per-request middleware chain, protocol-level decode + bound-model
    wiring, lifecycle.  Retry logic lives in :class:`.RetryMiddleware`; default
    header injection in :class:`.DefaultHeadersMiddleware` — both registered
    automatically in the default middleware chain.
    """

    def __init__(
        self,
        *,
        config: ClientConfig,
        proxy_transport: BaseProxyTransport | None = None,
    ) -> None:
        from ..transport.proxy._base import NoProxyTransport

        self.config = config
        self.proxy_transport: BaseProxyTransport = proxy_transport or NoProxyTransport()
        self.request_middlewares = RequestMiddlewareManager()
        self._closed = False
        self._opened = False

        # Default middleware chain — outermost registered first.
        # 1. DefaultHeadersMiddleware: inject headers once per make_request call.
        # 2. RetryMiddleware: full retry loop (transport exceptions + HTTP statuses).
        self.request_middlewares.register(DefaultHeadersMiddleware(config))
        self.request_middlewares.register(RetryMiddleware(RetryPolicy.from_config(config)))

    async def open(self) -> None:
        """Initialise pooled resources. Idempotent."""

        self._opened = True

    async def close(self) -> None:
        """Release resources. Idempotent."""

        self._closed = True

    async def make_request(self, client: Client, method: BaseMethod[object]) -> object:
        """Run a method-class through the funnel and return the typed response."""

        protocol = method.__protocol__()
        ctx = RequestContext(
            client=client,
            method=method,
            breaker_path=method.__breaker_path__ or method.__endpoint__,
            request_id=uuid4().hex[:12],
            account_id=getattr(client, "account_id", None),
        )

        bind_contextvars(request_id=ctx.request_id, account_id=ctx.account_id)
        try:
            prepared = await protocol.build_request(method, ctx)
            raw = await self.request_middlewares.dispatch(self._terminal, prepared, ctx)
            decoded = protocol.decode_response(method, raw)
            if isinstance(decoded, _AvitoClientMixin):
                decoded.as_(client)
            return decoded
        except SDKError as exc:
            if exc.context is None:
                exc.context = self._build_error_context(ctx, prepared=None)
            raise
        finally:
            clear_contextvars()

    async def _terminal(
        self,
        prepared: PreparedRequest,
        ctx: RequestContext,
    ) -> RawResponse:
        """Single-attempt send: acquire proxy, call ``_send``, translate errors."""

        acquire = self.proxy_transport.acquire(
            account_id=ctx.account_id,
            host=prepared.host,
        )
        try:
            async with acquire as proxy:
                ctx.proxy = proxy
                ctx.proxy_acquire = acquire
                if proxy is not None:
                    prepared.proxy = str(proxy.url)
                try:
                    raw = await self._send(prepared)
                except Exception as exc:  # noqa: BLE001 — transport boundary: translate proxy faults, re-raised
                    translated = self._translate_proxy_exception(exc, proxy)
                    if translated is not None:
                        acquire.mark_invalid(translated)
                        raise translated from exc
                    raise
                if raw.status == 407 and proxy is not None:
                    err = ProxyAuthError(
                        "Proxy returned 407 (auth required)",
                        proxy_url=str(proxy.url),
                    )
                    acquire.mark_invalid(err)
                    raise err
                return raw
        finally:
            ctx.proxy = None
            ctx.proxy_acquire = None

    @staticmethod
    def _translate_proxy_exception(exc: BaseException, proxy: Proxy | None) -> ProxyError | None:
        """Promote a generic transport error to a :class:`ProxyError` when a proxy was in use."""

        if proxy is None or isinstance(exc, ProxyError):
            return None
        proxy_url = str(proxy.url)
        if isinstance(exc, AvitoTimeoutError):
            return ProxyTimeoutError(str(exc), proxy_url=proxy_url)
        if isinstance(exc, TLSError):
            return ProxyTLSError(str(exc), proxy_url=proxy_url)
        if isinstance(exc, AvitoConnectionError):
            return ProxyConnectionError(str(exc), proxy_url=proxy_url)
        return None

    @abstractmethod
    async def _send(self, prepared: PreparedRequest) -> RawResponse:
        """Execute the wire request. Translate transport-level failures to ``TransportError``."""

    @staticmethod
    def _build_error_context(
        ctx: RequestContext,
        *,
        prepared: PreparedRequest | None,
    ) -> ErrorContext:
        return ErrorContext(
            method=type(ctx.method).__name__ if ctx.method is not None else None,
            host=prepared.host if prepared else None,
            path=prepared.url if prepared else None,
            attempt=ctx.attempt,
            request_id=ctx.request_id,
            account_id=ctx.account_id,
            breaker_path=ctx.breaker_path,
        )

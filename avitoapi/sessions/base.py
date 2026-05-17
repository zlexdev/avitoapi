"""``BaseSession`` — the funnel every HTTP call goes through."""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from structlog.contextvars import bind_contextvars, clear_contextvars

from ..exceptions import (
    ConnectionError as SDKConnectionError,
)
from ..exceptions import (
    ErrorContext,
    HTTPError,
    ProxyAuthError,
    ProxyConnectionError,
    ProxyError,
    ProxyTimeoutError,
    ProxyTLSError,
    RateLimitedError,
    SDKError,
    TLSError,
    http_error_for_status,
)
from ..exceptions import (
    TimeoutError as SDKTimeoutError,
)
from ..logging import get_logger
from ..models._base import BoundModel
from ..transport.headers import build_default_headers
from ..transport.retry import RetryPolicy
from ._models import PreparedRequest, RawResponse, RequestContext
from .middleware import RequestMiddlewareManager

if TYPE_CHECKING:
    from ..config import ClientConfig
    from ..methods._base import BaseMethod
    from ..utils.proxy._base import BaseProxyTransport

log = get_logger(__name__)


class BaseSession(ABC):
    """Single algorithm of one HTTP request. Subclasses implement ``_send`` only.

    Owns: per-request middleware chain, header defaults, retry loop, status →
    exception mapping, protocol-level decode + bound-model wiring, lifecycle.
    """

    def __init__(
        self,
        *,
        config: ClientConfig,
        proxy_transport: BaseProxyTransport | None = None,
    ) -> None:
        from ..utils.proxy._base import NoProxyTransport

        self.config = config
        self.proxy_transport: BaseProxyTransport = proxy_transport or NoProxyTransport()
        self.retry_policy = RetryPolicy.from_config(config)
        self.request_middlewares = RequestMiddlewareManager()
        self._closed = False
        self._opened = False

    async def open(self) -> None:
        """Initialise pooled resources. Idempotent."""

        self._opened = True

    async def close(self) -> None:
        """Release resources. Idempotent."""

        self._closed = True

    async def make_request(self, client: Any, method: BaseMethod[Any]) -> Any:
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
            self._apply_default_headers(prepared)
            raw = await self.request_middlewares.dispatch(self._terminal, prepared, ctx)
            decoded = protocol.decode_response(method, raw)
            if isinstance(decoded, BoundModel):
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
        last_exc: BaseException | None = None
        for attempt in range(self.retry_policy.max_retries + 1):
            ctx.attempt = attempt + 1
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
                    except Exception as exc:
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
            except Exception as exc:
                last_exc = exc
                if not self._should_retry_exception(exc, prepared, attempt):
                    raise
                await self._sleep_backoff(attempt, retry_after_s=None)
                continue
            finally:
                ctx.proxy = None
                ctx.proxy_acquire = None

            if 200 <= raw.status < 300:
                return raw

            error_cls = http_error_for_status(raw.status)
            retry_after = self._extract_retry_after(raw)
            log.warning(
                "session.http_error",
                status=raw.status,
                attempt=ctx.attempt,
                request_id=ctx.request_id,
                method=ctx.method and type(ctx.method).__name__,
                host=prepared.host,
                path=prepared.url,
            )
            if (
                self.retry_policy.should_retry_status(raw.status)
                and self._method_is_retryable(ctx, prepared)
                and attempt < self.retry_policy.max_retries
            ):
                await self._sleep_backoff(attempt, retry_after_s=retry_after)
                continue

            self._raise_http(error_cls, raw, ctx, prepared, retry_after_s=retry_after)

        if last_exc is not None:
            raise last_exc
        raise HTTPError("Exhausted retries without a response")

    @staticmethod
    def _translate_proxy_exception(exc: BaseException, proxy: Any | None) -> ProxyError | None:
        """Promote a generic transport error to a :class:`ProxyError` when a proxy was in use."""

        if proxy is None or isinstance(exc, ProxyError):
            return None
        proxy_url = str(proxy.url)
        if isinstance(exc, SDKTimeoutError):
            return ProxyTimeoutError(str(exc), proxy_url=proxy_url)
        if isinstance(exc, TLSError):
            return ProxyTLSError(str(exc), proxy_url=proxy_url)
        if isinstance(exc, SDKConnectionError):
            return ProxyConnectionError(str(exc), proxy_url=proxy_url)
        return None

    @abstractmethod
    async def _send(self, prepared: PreparedRequest) -> RawResponse:
        """Execute the wire request. Translate transport-level failures to ``TransportError``."""

    def _apply_default_headers(self, prepared: PreparedRequest) -> None:
        defaults = build_default_headers(self.config)
        for key, value in defaults.items():
            prepared.headers.setdefault(key, value)

    def _method_is_retryable(self, ctx: RequestContext, prepared: PreparedRequest) -> bool:
        if ctx.method is None:
            return prepared.http_method in {"GET", "HEAD", "OPTIONS"}
        protocol = ctx.method.__protocol__()
        return protocol.is_idempotent(ctx.method)

    def _should_retry_exception(
        self,
        exc: BaseException,
        prepared: PreparedRequest,
        attempt: int,
    ) -> bool:
        if attempt >= self.retry_policy.max_retries:
            return False
        # Proxy faults are never the request's fault — rotate and retry regardless of verb.
        if isinstance(exc, ProxyError):
            return True
        return prepared.http_method in {"GET", "HEAD", "OPTIONS"}

    async def _sleep_backoff(self, attempt: int, *, retry_after_s: float | None) -> None:
        delay = self.retry_policy.delay_for(attempt, retry_after_s=retry_after_s)
        if delay > 0:
            await asyncio.sleep(delay)

    @staticmethod
    def _extract_retry_after(raw: RawResponse) -> float | None:
        header = raw.headers.get("retry-after") or raw.headers.get("Retry-After")
        if header is None:
            return None
        try:
            return float(header)
        except ValueError:
            return None

    def _raise_http(
        self,
        error_cls: type[HTTPError],
        raw: RawResponse,
        ctx: RequestContext,
        prepared: PreparedRequest,
        *,
        retry_after_s: float | None,
    ) -> None:
        context = self._build_error_context(ctx, prepared=prepared)
        if error_cls is RateLimitedError:
            raise RateLimitedError(
                retry_after_s=retry_after_s or 0.0,
                body=raw.body,
                context=context,
            )
        raise error_cls(body=raw.body, context=context)

    @staticmethod
    def _build_error_context(
        ctx: RequestContext,
        *,
        prepared: PreparedRequest | None,
    ) -> ErrorContext:
        return ErrorContext(
            method=ctx.method and type(ctx.method).__name__,
            host=prepared.host if prepared else None,
            path=prepared.url if prepared else None,
            attempt=ctx.attempt,
            request_id=ctx.request_id,
            account_id=ctx.account_id,
            breaker_path=ctx.breaker_path,
        )

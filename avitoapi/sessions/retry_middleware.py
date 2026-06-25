"""``RetryMiddleware`` — unified retry for HTTP errors and transport exceptions."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from ..exceptions import (
    ErrorContext,
    HTTPError,
    ProxyError,
    ProxyExhausted,
    RateLimitedError,
    TransportError,
    http_error_for_status,
)
from ..logging import get_logger
from ..transport.retry import RetryPolicy
from .middleware import RequestHandler, RequestMiddleware

if TYPE_CHECKING:
    from ._models import PreparedRequest, RawResponse, RequestContext

log = get_logger(__name__)


class RetryMiddleware(RequestMiddleware):
    """Unified retry for both transport-exception failures and retryable HTTP statuses.

    Covers:

    * Transport exceptions (:class:`.ProxyError`, connection errors on
      idempotent HTTP verbs).
    * HTTP status codes in ``policy.retry_statuses``
      (408, 429, 500, 502, 503, 504 by default).

    ``Retry-After`` response header is honoured for 429 responses.

    Args:
        policy: Backoff window, jitter, max attempts, and retryable status set.
    """

    def __init__(self, policy: RetryPolicy) -> None:
        self._policy = policy

    async def __call__(
        self,
        handler: RequestHandler,
        prepared: PreparedRequest,
        ctx: RequestContext,
    ) -> RawResponse:
        last_exc: BaseException | None = None
        last_raw: RawResponse | None = None

        for attempt in range(self._policy.max_retries + 1):
            ctx.attempt = attempt + 1
            try:
                raw = await handler(prepared, ctx)
            except Exception as exc:  # noqa: BLE001 — retry boundary: any fault is a retry candidate; logged below and re-raised when not retryable
                last_exc = exc
                last_raw = None
                if not self._should_retry_exc(exc, prepared, attempt):
                    raise
                log.warning(
                    "session.retry_exception",
                    attempt=ctx.attempt,
                    of=self._policy.max_retries + 1,
                    error=type(exc).__name__,
                    request_id=ctx.request_id,
                )
                await self._sleep(attempt, retry_after_s=None)
                continue

            last_raw = raw
            last_exc = None

            if 200 <= raw.status < 300:
                return raw

            retry_after = _extract_retry_after(raw)
            log.warning(
                "session.http_error",
                status=raw.status,
                attempt=ctx.attempt,
                request_id=ctx.request_id,
                method=type(ctx.method).__name__ if ctx.method is not None else None,
                host=prepared.host,
                path=prepared.url,
            )
            if (
                self._policy.should_retry_status(raw.status)
                and self._method_is_retryable(ctx, prepared)
                and attempt < self._policy.max_retries
            ):
                await self._sleep(attempt, retry_after_s=retry_after)
                continue
            break

        if last_exc is not None:
            raise last_exc
        if last_raw is not None:
            _raise_http(last_raw, ctx, prepared)
        raise HTTPError("Exhausted retries without a response")

    def _should_retry_exc(
        self,
        exc: BaseException,
        prepared: PreparedRequest,
        attempt: int,
    ) -> bool:
        if attempt >= self._policy.max_retries:
            return False
        # Pool is empty — rotating won't help, fail fast.
        if isinstance(exc, ProxyExhausted):
            return False
        # Proxy faults are never the request's fault — rotate and retry regardless of verb.
        if isinstance(exc, ProxyError):
            return True
        # Other transport faults (connection/timeout) retry only on idempotent verbs.
        # Non-transport errors (e.g. programming bugs) are never retried.
        if isinstance(exc, TransportError):
            return bool(prepared.http_method in {"GET", "HEAD", "OPTIONS"})
        return False

    def _method_is_retryable(
        self,
        ctx: RequestContext,
        prepared: PreparedRequest,
    ) -> bool:
        if ctx.method is None:
            return bool(prepared.http_method in {"GET", "HEAD", "OPTIONS"})
        protocol = ctx.method.__protocol__()
        return bool(protocol.is_idempotent(ctx.method))

    async def _sleep(self, attempt: int, *, retry_after_s: float | None) -> None:
        delay = self._policy.delay_for(attempt, retry_after_s=retry_after_s)
        if delay > 0:
            await asyncio.sleep(delay)


def _extract_retry_after(raw: RawResponse) -> float | None:
    header = raw.headers.get("retry-after") or raw.headers.get("Retry-After")
    if header is None:
        return None
    try:
        return float(header)
    except ValueError:
        return None


def _raise_http(
    raw: RawResponse,
    ctx: RequestContext,
    prepared: PreparedRequest,
) -> None:
    error_cls = http_error_for_status(raw.status)
    context = ErrorContext(
        method=type(ctx.method).__name__ if ctx.method is not None else None,
        host=prepared.host,
        path=prepared.url,
        attempt=ctx.attempt,
        request_id=ctx.request_id,
        account_id=ctx.account_id,
        breaker_path=ctx.breaker_path,
    )
    retry_after = _extract_retry_after(raw)
    if error_cls is RateLimitedError:
        raise RateLimitedError(
            retry_after_s=retry_after or 0.0,
            body=raw.body,
            context=context,
        )
    raise error_cls(body=raw.body, context=context)


__all__ = ["RetryMiddleware"]

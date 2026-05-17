"""Proxy-aware request middlewares.

* :class:`ProxyErrorMiddleware` — late-stage classifier. Any
  :class:`TransportError` that escapes the funnel with a proxy bound to
  :class:`RequestContext` is rewrapped as the specific
  :class:`ProxyError` subclass so handlers (``except ProxyTimeoutError:``)
  stay clean. Also marks the proxy invalid through the acquire context, so
  the rotator's failure tally advances even when the session backend
  doesn't classify the error correctly itself.

* :class:`RetryMiddleware` — outer retry layer that re-runs the handler
  on :class:`ProxyError` / :class:`ProxyBanned`. Each retry triggers a
  fresh proxy acquisition inside the terminal, so the request rotates
  away from the failing proxy automatically. Independent of the session's
  built-in retry loop — stack it for harder guarantees.
"""

from __future__ import annotations

import asyncio
import random
from typing import TYPE_CHECKING

from ..exceptions import (
    ConnectionError as SDKConnectionError,
)
from ..exceptions import (
    ProxyBanned,
    ProxyConnectionError,
    ProxyError,
    ProxyExhausted,
    ProxyTimeoutError,
    ProxyTLSError,
    TLSError,
    TransportError,
)
from ..exceptions import (
    TimeoutError as SDKTimeoutError,
)
from ..logging import get_logger
from .middleware import RequestHandler, RequestMiddleware

if TYPE_CHECKING:
    from ._models import PreparedRequest, RawResponse, RequestContext

log = get_logger(__name__)


class ProxyErrorMiddleware(RequestMiddleware):
    """Rewrap stray transport errors as :class:`ProxyError` when a proxy is bound.

    The session funnel does this for errors thrown by the default backends,
    but custom :class:`BaseSession` subclasses (or third-party transports
    routed through ``prepared.proxy``) may raise generic
    :class:`TransportError` instances. This middleware catches them at the
    chain edge, marks the proxy invalid, and reraises a typed
    :class:`ProxyError` subclass.
    """

    async def __call__(
        self,
        handler: RequestHandler,
        prepared: PreparedRequest,
        ctx: RequestContext,
    ) -> RawResponse:
        try:
            return await handler(prepared, ctx)
        except ProxyError:
            raise
        except TransportError as exc:
            proxy = ctx.proxy
            if proxy is None:
                raise
            translated = _translate(exc, str(proxy.url))
            if ctx.proxy_acquire is not None:
                ctx.proxy_acquire.mark_invalid(translated)
            raise translated from exc


class RetryMiddleware(RequestMiddleware):
    """Outer retry for proxy-attributable failures.

    ``max_retries`` is the number of *extra* attempts after the first call.
    Backoff follows ``min(initial_s * 2**attempt, max_s)`` with jitter.

    By default this only retries :class:`ProxyError` (rotator-driven), but
    callers can broaden ``retry_on`` to include any :class:`TransportError`
    subclass.
    """

    def __init__(
        self,
        *,
        max_retries: int = 3,
        initial_s: float = 0.25,
        max_s: float = 5.0,
        jitter_ratio: float = 0.25,
        retry_on: tuple[type[BaseException], ...] = (ProxyError,),
        give_up_on: tuple[type[BaseException], ...] = (ProxyExhausted,),
    ) -> None:
        self.max_retries = int(max_retries)
        self.initial_s = float(initial_s)
        self.max_s = float(max_s)
        self.jitter_ratio = float(jitter_ratio)
        self.retry_on = retry_on
        self.give_up_on = give_up_on
        self._rng = random.Random()

    async def __call__(
        self,
        handler: RequestHandler,
        prepared: PreparedRequest,
        ctx: RequestContext,
    ) -> RawResponse:
        last_exc: BaseException | None = None
        for attempt in range(self.max_retries + 1):
            try:
                return await handler(prepared, ctx)
            except self.give_up_on:
                raise
            except self.retry_on as exc:
                last_exc = exc
                if attempt >= self.max_retries:
                    raise
                log.warning(
                    "proxy.retry",
                    attempt=attempt + 1,
                    of=self.max_retries + 1,
                    error=type(exc).__name__,
                    detail=str(exc),
                    proxy_url=getattr(exc, "proxy_url", None),
                    request_id=ctx.request_id,
                )
                await asyncio.sleep(self._delay(attempt))
        if last_exc is not None:
            raise last_exc
        raise RuntimeError("RetryMiddleware exited without sending a request")

    def _delay(self, attempt: int) -> float:
        base = min(self.initial_s * (2 ** max(0, attempt)), self.max_s)
        jitter = base * self.jitter_ratio * (self._rng.random() * 2 - 1)
        return max(0.0, base + jitter)


def _translate(exc: TransportError, proxy_url: str) -> ProxyError:
    if isinstance(exc, SDKTimeoutError):
        return ProxyTimeoutError(str(exc), proxy_url=proxy_url)
    if isinstance(exc, TLSError):
        return ProxyTLSError(str(exc), proxy_url=proxy_url)
    if isinstance(exc, SDKConnectionError):
        return ProxyConnectionError(str(exc), proxy_url=proxy_url)
    return ProxyError(str(exc), proxy_url=proxy_url)


__all__ = [
    "ProxyBanned",
    "ProxyErrorMiddleware",
    "RetryMiddleware",
]

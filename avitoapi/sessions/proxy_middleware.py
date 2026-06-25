"""Proxy-aware request middlewares.

:class:`ProxyErrorMiddleware` — late-stage classifier. Any
:class:`TransportError` that escapes the funnel with a proxy bound to
:class:`RequestContext` is rewrapped as the specific :class:`ProxyError`
subclass so handlers (``except ProxyTimeoutError:``) stay clean. Also marks
the proxy invalid through the acquire context, so the rotator's failure tally
advances even when the session backend doesn't classify the error correctly.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..exceptions import (
    AvitoConnectionError,
    AvitoTimeoutError,
    ProxyConnectionError,
    ProxyError,
    ProxyTimeoutError,
    ProxyTLSError,
    TLSError,
    TransportError,
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


def _translate(exc: TransportError, proxy_url: str) -> ProxyError:
    if isinstance(exc, AvitoTimeoutError):
        return ProxyTimeoutError(str(exc), proxy_url=proxy_url)
    if isinstance(exc, TLSError):
        return ProxyTLSError(str(exc), proxy_url=proxy_url)
    if isinstance(exc, AvitoConnectionError):
        return ProxyConnectionError(str(exc), proxy_url=proxy_url)
    return ProxyError(str(exc), proxy_url=proxy_url)


__all__ = ["ProxyErrorMiddleware", "RequestMiddleware"]

"""Session funnel + concrete backends. See ``_MODULE.md``."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..logging import get_logger
from ._models import PreparedRequest, RawResponse, RequestContext
from .base import BaseSession
from .middleware import RequestMiddleware, RequestMiddlewareManager

if TYPE_CHECKING:
    from ..config import ClientConfig
    from ..utils.proxy._base import BaseProxyTransport

log = get_logger(__name__)


def create_default_session(
    config: ClientConfig,
    *,
    proxy_transport: BaseProxyTransport | None = None,
) -> BaseSession:
    """Build the default session. Prefers :class:`CurlSession`; falls back to httpx.

    The fallback only fires when ``curl_cffi`` is unimportable — typically on a
    platform without a libcurl-impersonate wheel. The httpx fallback has no TLS
    impersonation, so Cloudflare-protected hosts may challenge it.
    """

    from ..utils.proxy._base import NoProxyTransport

    transport = proxy_transport or NoProxyTransport()
    try:
        from .curl import CurlSession

        return CurlSession(config=config, proxy_transport=transport)
    except ImportError:
        from .httpx_session import HttpxSession

        log.warning("session.curl_unavailable_falling_back_to_httpx")
        return HttpxSession(config=config, proxy_transport=transport)


__all__ = [
    "BaseSession",
    "PreparedRequest",
    "RawResponse",
    "RequestContext",
    "RequestMiddleware",
    "RequestMiddlewareManager",
    "create_default_session",
]

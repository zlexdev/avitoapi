"""``DefaultHeadersMiddleware`` — inject default request headers into every outbound call."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..transport.headers import build_default_headers
from .middleware import RequestHandler, RequestMiddleware

if TYPE_CHECKING:
    from ..config import ClientConfig
    from ._models import PreparedRequest, RawResponse, RequestContext


class DefaultHeadersMiddleware(RequestMiddleware):
    """Inject default headers (User-Agent, Accept, Accept-Language) onto every request.

    Headers already present on :class:`.PreparedRequest` take precedence — the
    middleware uses ``setdefault`` semantics, so callers can always override.

    Args:
        config: Client config supplying :attr:`.ClientConfig.user_agent`.
    """

    def __init__(self, config: ClientConfig) -> None:
        self._config = config

    async def __call__(
        self,
        handler: RequestHandler,
        prepared: PreparedRequest,
        ctx: RequestContext,
    ) -> RawResponse:
        defaults = build_default_headers(self._config)
        for key, value in defaults.items():
            prepared.headers.setdefault(key, value)
        return await handler(prepared, ctx)


__all__ = ["DefaultHeadersMiddleware"]

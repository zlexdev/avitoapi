"""Request-side middleware ABC + manager. Shared shape between request and dispatch sides."""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._models import PreparedRequest, RawResponse, RequestContext


RequestHandler = Callable[
    ["PreparedRequest", "RequestContext"],
    Awaitable["RawResponse"],
]


class RequestMiddleware(ABC):
    """Wrap one HTTP request — inject headers, sign payloads, log, etc.

    Subclasses implement ``__call__``. The middleware decides whether to call
    ``handler(prepared, ctx)`` (continue down the chain) and how to mutate the
    request / response on either side.
    """

    @abstractmethod
    async def __call__(
        self,
        handler: RequestHandler,
        prepared: PreparedRequest,
        ctx: RequestContext,
    ) -> RawResponse:
        ...


class RequestMiddlewareManager:
    """Chain of :class:`RequestMiddleware`. Earlier registrations wrap later ones."""

    def __init__(self) -> None:
        self._middlewares: list[RequestMiddleware] = []

    def register(self, middleware: RequestMiddleware) -> RequestMiddleware:
        """Append a middleware. Returns the middleware for fluent chaining."""

        self._middlewares.append(middleware)
        return middleware

    def __iter__(self) -> object:
        return iter(self._middlewares)

    def __len__(self) -> int:
        return len(self._middlewares)

    async def dispatch(
        self,
        terminal: RequestHandler,
        prepared: PreparedRequest,
        ctx: RequestContext,
    ) -> RawResponse:
        """Fold the chain over ``terminal`` and execute."""

        handler: RequestHandler = terminal
        for middleware in reversed(self._middlewares):
            handler = _wrap(middleware, handler)
        return await handler(prepared, ctx)


def _wrap(middleware: RequestMiddleware, nxt: RequestHandler) -> RequestHandler:
    async def _call(prepared: PreparedRequest, ctx: RequestContext) -> RawResponse:
        return await middleware(nxt, prepared, ctx)

    return _call

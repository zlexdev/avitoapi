"""``BaseMiddleware`` — outer/inner middleware ABC for event propagation."""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .context import EventContext

NextHandler = Callable[[Any, "EventContext"], Awaitable[Any]]


class BaseMiddleware(ABC):
    """Wrap one event delivery.

    Subclasses implement ``__call__``; they decide whether to call
    ``handler(event, ctx)`` (continue propagation) and how to mutate the
    event / context on either side.

    Two mounting points:

    * ``router.outer_middleware.register(mw)`` — runs once per router visit,
      before predicate evaluation. Use for tracing, auth-bind, FSM context
      construction.
    * ``router.inner_middleware.register(mw)`` — wraps each individual
      handler call. Use for per-handler retry, idempotency, rate limit.
    """

    @abstractmethod
    async def __call__(
        self,
        handler: NextHandler,
        event: Any,
        ctx: EventContext,
    ) -> Any:
        ...


class MiddlewareChain:
    """Ordered list of :class:`BaseMiddleware`. Earlier registrations wrap later ones."""

    __slots__ = ("_items",)

    def __init__(self) -> None:
        self._items: list[BaseMiddleware] = []

    def register(self, middleware: BaseMiddleware) -> BaseMiddleware:
        """Append a middleware. Returns it for fluent chaining."""

        self._items.append(middleware)
        return middleware

    def __call__(self, middleware: BaseMiddleware) -> BaseMiddleware:
        """Decorator form: ``@router.outer_middleware``."""

        return self.register(middleware)

    def __iter__(self):  # noqa: ANN204 — small iterator helper
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def wrap(self, terminal: NextHandler) -> NextHandler:
        """Fold the chain over ``terminal`` and return the composed handler."""

        handler: NextHandler = terminal
        for middleware in reversed(self._items):
            handler = _bind(middleware, handler)
        return handler


def _bind(mw: BaseMiddleware, nxt: NextHandler) -> NextHandler:
    async def _call(event: Any, ctx: EventContext) -> Any:
        return await mw(nxt, event, ctx)
    return _call


__all__ = ["BaseMiddleware", "MiddlewareChain", "NextHandler"]

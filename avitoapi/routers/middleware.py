"""``BaseMiddleware`` — outer/inner middleware ABC for event propagation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable, Iterator
from typing import Generic, TypeVar

from ..events._base import Event

CtxT = TypeVar("CtxT")
ResultT = TypeVar("ResultT")

NextHandler = Callable[[Event, CtxT], Awaitable[ResultT]]


class BaseMiddleware(ABC, Generic[CtxT, ResultT]):
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
        handler: Callable[[Event, CtxT], Awaitable[ResultT]],
        event: Event,
        ctx: CtxT,
    ) -> ResultT: ...


class MiddlewareChain(Generic[CtxT, ResultT]):
    """Ordered list of :class:`BaseMiddleware`. Earlier registrations wrap later ones."""

    __slots__ = ("_items",)

    def __init__(self) -> None:
        self._items: list[BaseMiddleware[CtxT, ResultT]] = []

    def register(self, middleware: BaseMiddleware[CtxT, ResultT]) -> BaseMiddleware[CtxT, ResultT]:
        """Append a middleware. Returns it for fluent chaining."""

        self._items.append(middleware)
        return middleware

    def __call__(self, middleware: BaseMiddleware[CtxT, ResultT]) -> BaseMiddleware[CtxT, ResultT]:
        """Decorator form: ``@router.outer_middleware``."""

        return self.register(middleware)

    def __iter__(self) -> Iterator[BaseMiddleware[CtxT, ResultT]]:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def wrap(
        self,
        terminal: Callable[[Event, CtxT], Awaitable[ResultT]],
    ) -> Callable[[Event, CtxT], Awaitable[ResultT]]:
        """Fold the chain over ``terminal`` and return the composed handler."""

        handler: Callable[[Event, CtxT], Awaitable[ResultT]] = terminal
        for middleware in reversed(self._items):
            handler = _bind(middleware, handler)
        return handler


def _bind(
    mw: BaseMiddleware[CtxT, ResultT],
    nxt: Callable[[Event, CtxT], Awaitable[ResultT]],
) -> Callable[[Event, CtxT], Awaitable[ResultT]]:
    async def _call(event: Event, ctx: CtxT) -> ResultT:
        return await mw(nxt, event, ctx)

    return _call


__all__ = ["BaseMiddleware", "CtxT", "MiddlewareChain", "NextHandler", "ResultT"]

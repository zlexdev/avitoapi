"""``EventObserver`` / ``HandlerManager`` — the decorator surface routers expose.

Aiogram-style usage::

    @router.new_message(F.message.type == "text")
    async def handle_text(event, ctx): ...

The observer can be called with zero or more *predicates* (filters); the
decorated handler is invoked only when every predicate matches the event.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Generic, TypeVar

from ..events._base import Event
from .errors import SkipHandler

Filter = Callable[[Event], bool]
Handler = Callable[..., Awaitable[object]]

EventT_contra = TypeVar("EventT_contra", bound=Event, contravariant=True)


@dataclass(slots=True)
class HandlerSpec:
    """One registered handler with its activation predicates."""

    handler: Handler
    filters: tuple[Filter, ...] = ()

    def matches(self, event: Event) -> bool:
        for predicate in self.filters:
            try:
                if not predicate(event):
                    return False
            except Exception:  # noqa: BLE001 — predicate failure ≠ propagation error
                return False
        return True


@dataclass(slots=True)
class HandlerManager(Generic[EventT_contra]):
    """Named manager that owns handlers for one event route.

    ``event_filter`` is the gate that decides whether the event belongs to
    this manager *at all* (typically an ``isinstance`` check the router
    installs). Per-handler predicates layered on top filter further.
    """

    name: str
    event_filter: Filter | None = None
    handlers: list[HandlerSpec] = field(default_factory=list)

    def register(self, handler: Handler, *filters: Filter) -> Handler:
        """Append a handler. Returns it for decorator chaining."""

        self.handlers.append(HandlerSpec(handler=handler, filters=tuple(filters)))
        return handler

    def __call__(self, *filters: Filter) -> Callable[[Handler], Handler]:
        """Decorator factory: ``@observer(filter1, filter2)``."""

        def _decorator(fn: Handler) -> Handler:
            return self.register(fn, *filters)

        return _decorator

    def applies(self, event: Event) -> bool:
        if self.event_filter is None:
            return True
        try:
            return bool(self.event_filter(event))
        except Exception:  # noqa: BLE001 — bad filter is not a propagation error
            return False

    async def trigger(self, event: EventT_contra, ctx: object) -> bool:
        """Run every matching handler. Returns ``True`` if anything fired.

        A handler raising :class:`~avitoapi.routers.errors.SkipHandler` is
        skipped without counting as fired; :class:`CancelPropagation` bubbles
        up to :meth:`Router.propagate` to halt the whole walk. A handler that
        calls ``ctx.stop_propagation()`` stops further handlers here too.
        """

        fired = False
        for spec in self.handlers:
            if not spec.matches(event):
                continue
            try:
                await spec.handler(event, ctx)
            except SkipHandler:
                continue
            fired = True
            if getattr(ctx, "is_stopped", False):
                break
        return fired


# Alias kept for the public name aiogram users expect.
EventObserver = HandlerManager


__all__ = ["EventObserver", "EventT_contra", "Filter", "Handler", "HandlerManager", "HandlerSpec"]

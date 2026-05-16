"""Messenger router with typed ``EventObserver`` attributes.

Mirrors aiogram's `Router` / `EventObserver` shape. When the optional
``evented`` package is present, both the router and observer come from
it. Without ``evented``, an in-package fallback `EventObserver` ships so
handlers can still be registered and dispatched in tests / lightweight
single-process setups.
"""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, Generic, TypeVar, cast

from ..events.messenger import ChatArchived, MessageRead, NewMessage

E = TypeVar("E")

try:
    import evented as _evented

    _EventedRouter: type = _evented.Router
    _EventedObserver: type = _evented.EventObserver
    _HAS_EVENTED = True
except ImportError:
    _evented = None  # type: ignore[assignment]
    _EventedRouter = None  # type: ignore[assignment]
    _EventedObserver = None  # type: ignore[assignment]
    _HAS_EVENTED = False


Handler = Callable[[Any], Awaitable[Any]]
Filter = Callable[[Any], bool]


class _FallbackEventObserver(Generic[E]):
    """Minimal aiogram-style observer: ``@observer(filter)`` decorator + ``route``.

    Only used when ``evented`` is missing. Supports synchronous filters
    (``f(event) -> bool``) — sufficient for the lightweight test path.
    """

    def __init__(self) -> None:
        self._handlers: list[tuple[Handler, tuple[Filter, ...]]] = []

    def __call__(self, *filters: Filter) -> Callable[[Handler], Handler]:
        """Decorator: ``@observer()`` or ``@observer(filter_a, filter_b)``."""

        def _decorator(handler: Handler) -> Handler:
            self._handlers.append((handler, filters))
            return handler

        return _decorator

    def register(self, handler: Handler, *filters: Filter) -> Handler:
        """Imperative registration — equivalent to ``observer(*filters)(handler)``."""
        self._handlers.append((handler, filters))
        return handler

    @property
    def handlers(self) -> list[tuple[Handler, tuple[Filter, ...]]]:
        """All registered ``(handler, filters)`` pairs."""
        return list(self._handlers)

    async def route(self, event: E) -> list[Any]:
        """Run every handler whose filters all return ``True``. Returns results."""
        results: list[Any] = []
        for handler, filters in self._handlers:
            if all(f(event) for f in filters):
                results.append(await handler(event))
        return results


EventObserver = cast(type, _EventedObserver) if _HAS_EVENTED else _FallbackEventObserver


class _FallbackRouter:
    """Minimal Router stub: holds three typed `EventObserver` attributes."""

    def __init__(self) -> None:
        self.new_message: _FallbackEventObserver[NewMessage] = _FallbackEventObserver()
        self.message_read: _FallbackEventObserver[MessageRead] = _FallbackEventObserver()
        self.chat_archived: _FallbackEventObserver[ChatArchived] = _FallbackEventObserver()


_RouterBase: type = _EventedRouter if _HAS_EVENTED else _FallbackRouter


class MessengerRouter(_RouterBase):  # type: ignore[misc,valid-type]
    """Aiogram-style router for the messenger domain.

    Three typed observer attributes:

    * ``router.new_message`` — :class:`avitoapi.events.NewMessage`
    * ``router.message_read`` — :class:`avitoapi.events.MessageRead`
    * ``router.chat_archived`` — :class:`avitoapi.events.ChatArchived`
    """

    new_message: Any
    message_read: Any
    chat_archived: Any

    def __init__(self) -> None:
        super().__init__()
        if not _HAS_EVENTED:
            self.new_message = _FallbackEventObserver()
            self.message_read = _FallbackEventObserver()
            self.chat_archived = _FallbackEventObserver()

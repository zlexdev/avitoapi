"""``Event`` — root of the typed-event hierarchy.

Subclasses optionally declare an ``event_name`` class-kwarg to register
themselves in :data:`Event.registry` (used by the router for textual
routes and by debug tooling).
"""
from __future__ import annotations

from typing import Any, ClassVar


class Event:
    """Base event class.

    ``event_name`` is the textual route key (``messenger.new_message``,
    ``orders.created``, ...). Subclasses can carry arbitrary kwargs; they
    are assigned to instance attributes by the default ``__init__``.
    """

    __event_name__: ClassVar[str] = ""
    registry: ClassVar[dict[str, type[Event]]] = {}

    def __init_subclass__(cls, *, event_name: str = "", **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if event_name:
            cls.__event_name__ = event_name
            Event.registry[event_name] = cls
        elif not cls.__event_name__:
            cls.__event_name__ = cls.__qualname__

    def __init__(self, **kwargs: Any) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self) -> str:
        attrs = ", ".join(
            f"{k}={v!r}" for k, v in vars(self).items() if not k.startswith("_")
        )
        return f"{type(self).__name__}({attrs})"


__all__ = ["Event"]

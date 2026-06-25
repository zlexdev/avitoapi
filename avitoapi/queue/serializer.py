"""Serializers + ``EventRegistry`` for safe queue payloads.

The queue persists events through a :class:`EventSerializer`. Two
implementations ship:

* :class:`JSONSerializer` (default, recommended) — converts each event
  to ``{type, version, data}`` using a global :class:`EventRegistry`.
  Cross-language, schema-evolvable, safe to deserialise from untrusted
  storage.
* :class:`PickleSerializer` (legacy) — base64 pickle. Kept for in-process
  compatibility with code that doesn't bother registering events. Do not
  feed it untrusted payloads; pickle is RCE-shaped.

The :class:`EventRegistry` maps an event class to a stable string id +
schema version. Events register themselves at class definition by
declaring ``event_name="..."`` (already wired in
:class:`avitoapi.events._base.Event`) or explicitly via
:meth:`EventRegistry.register`.
"""

from __future__ import annotations

import base64
import pickle
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import ClassVar

from ..events._base import Event
from ..logging import get_logger
from ..types import JsonObject, JSONValue

log = get_logger(__name__)


class EventSerializer(ABC):
    """Convert :class:`Event` instances to/from a JSON-friendly form for storage."""

    @abstractmethod
    def dump(self, event: Event) -> JSONValue: ...

    @abstractmethod
    def load(self, payload: JSONValue) -> Event: ...


class EventRegistrationError(ValueError):
    """Raised on conflicting or unknown event registrations."""


Upgrader = Callable[[JsonObject], JsonObject]


class EventRegistry:
    """Process-wide mapping ``event_type → class`` + schema version.

    Events registered via :meth:`register` are discoverable by their
    stable ``type`` string when the queue replays a row. The class name
    on disk and the runtime class name are decoupled — pass ``name=``
    explicitly to keep the wire format stable across renames.

    Schema evolution: register a new version with ``version=`` and an
    ``upgrader`` that transforms an old-version payload dict into the
    current one. The serializer runs upgraders in order.
    """

    _by_name: ClassVar[dict[str, type[Event]]] = {}
    _by_class: ClassVar[dict[type[Event], str]] = {}
    _versions: ClassVar[dict[str, int]] = {}
    _upgraders: ClassVar[dict[tuple[str, int], Upgrader]] = {}

    @classmethod
    def register(
        cls,
        event_class: type[Event],
        *,
        name: str | None = None,
        version: int = 1,
        upgrader: Upgrader | None = None,
    ) -> type[Event]:
        """Register ``event_class`` under ``name`` (defaults to its ``__event_name__``).

        ``upgrader``, when provided, migrates a payload dict stored at
        ``version - 1`` into the current shape — the loader walks the
        chain on read.
        """

        effective = name or event_class.__event_name__ or event_class.__qualname__
        if not effective:
            raise EventRegistrationError(
                f"{event_class.__name__} has no event_name and none was supplied",
            )
        existing = cls._by_name.get(effective)
        if existing is not None and existing is not event_class:
            raise EventRegistrationError(
                f"event type {effective!r} already registered to {existing.__name__}",
            )
        cls._by_name[effective] = event_class
        cls._by_class[event_class] = effective
        cls._versions[effective] = version
        if upgrader is not None and version > 1:
            cls._upgraders[(effective, version - 1)] = upgrader
        return event_class

    @classmethod
    def name_for(cls, event_class: type[Event]) -> str:
        """Return the registered string id for ``event_class``."""

        existing = cls._by_class.get(event_class)
        if existing is not None:
            return existing
        # auto-register on first sight using the class's event_name
        return cls.register(event_class).__event_name__ or event_class.__qualname__

    @classmethod
    def get(cls, name: str) -> type[Event] | None:
        """Lookup the class registered under ``name``. ``None`` when absent."""

        return cls._by_name.get(name)

    @classmethod
    def version_of(cls, name: str) -> int:
        return cls._versions.get(name, 1)

    @classmethod
    def upgrade(cls, name: str, data: JsonObject, from_version: int) -> JsonObject:
        """Walk the upgrader chain from ``from_version`` up to the current version."""

        current = cls._versions.get(name, 1)
        while from_version < current:
            upgrader = cls._upgraders.get((name, from_version))
            if upgrader is None:
                raise EventRegistrationError(
                    f"no upgrader registered for {name!r} v{from_version} → v{from_version + 1}",
                )
            data = upgrader(data)
            from_version += 1
        return data

    @classmethod
    def clear(cls) -> None:
        """Reset the registry. Intended for tests only."""

        cls._by_name.clear()
        cls._by_class.clear()
        cls._versions.clear()
        cls._upgraders.clear()


def _event_to_dict(event: Event) -> JsonObject:
    """Best-effort attribute snapshot for a generic :class:`Event`.

    Uses ``vars(event)`` so any subclass that just stashes kwargs on
    ``self`` (the default :class:`Event.__init__` behaviour) round-trips
    cleanly. Private attributes (``_*``) are dropped.
    """

    return {k: v for k, v in vars(event).items() if not k.startswith("_")}


class JSONSerializer(EventSerializer):
    """Default serializer — ``{type, version, data}`` JSON-friendly dict.

    On dump: looks the event class up in :class:`EventRegistry`, emits a
    payload ``{"type": <name>, "version": <int>, "data": <fields>}``.
    On load: looks the class up by ``type``, applies any pending
    upgraders, instantiates with ``**data``. Subclass-friendly: events
    whose ``__init__`` accepts arbitrary kwargs round-trip without
    further config.
    """

    def __init__(self, *, registry: type[EventRegistry] = EventRegistry) -> None:
        self._registry = registry
        _auto_register_known_events()

    def dump(self, event: Event) -> JsonObject:
        type_name = self._registry.name_for(type(event))
        version = self._registry.version_of(type_name)
        return {
            "type": type_name,
            "version": version,
            "data": _event_to_dict(event),
        }

    def load(self, payload: JSONValue) -> Event:
        if not isinstance(payload, dict):
            raise ValueError(
                f"JSONSerializer expected dict payload, got {type(payload).__name__}",
            )
        type_name = payload.get("type")
        if not isinstance(type_name, str) or not type_name:
            raise ValueError("payload missing string 'type' field")
        cls = self._registry.get(type_name)
        if cls is None:
            raise EventRegistrationError(
                f"unknown event type {type_name!r} — register the class via "
                "EventRegistry.register or define it with event_name=...",
            )
        data = payload.get("data") or {}
        if not isinstance(data, dict):
            raise ValueError("payload 'data' must be an object")
        version = int(payload.get("version") or 1)  # type: ignore[arg-type]  # JSONValue narrowed at runtime
        current = self._registry.version_of(type_name)
        if version < current:
            data = self._registry.upgrade(type_name, dict(data), from_version=version)
        return cls(**data)


class PickleSerializer(EventSerializer):
    """Legacy serializer — base64-pickle. **Unsafe with untrusted input.**

    Kept for code that uses events whose ``__init__`` is non-trivial
    (positional args, validation, etc.) and can't be reconstructed from
    a plain kwargs dict. Pickle deserialisation can execute arbitrary
    code; do not use against shared / network-reachable storage.
    """

    def dump(self, event: Event) -> str:
        return base64.b64encode(pickle.dumps(event)).decode("ascii")

    def load(self, payload: JSONValue) -> Event:
        if not isinstance(payload, str):
            raise ValueError(
                f"PickleSerializer expected str payload, got {type(payload).__name__}",
            )
        # Legacy path, opt-in only. Docstring warns against untrusted input.
        loaded: Event = pickle.loads(  # noqa: S301
            base64.b64decode(payload.encode("ascii")),
        )  # nosec B301
        return loaded


def _auto_register_known_events() -> None:
    """Best-effort: register every :class:`Event` subclass that declared an ``event_name``.

    Called lazily by :class:`JSONSerializer` so callers don't need to
    import every event module manually. Iterating ``Event.registry``
    catches everything that hooked ``__init_subclass__``.
    """

    for name, cls in list(Event.registry.items()):
        if name not in EventRegistry._by_name:
            EventRegistry.register(cls, name=name)


__all__ = [
    "EventRegistrationError",
    "EventRegistry",
    "EventSerializer",
    "JSONSerializer",
    "PickleSerializer",
    "Upgrader",
]

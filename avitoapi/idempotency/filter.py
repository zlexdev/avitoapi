"""``DedupFilter`` — event-level adapter over :class:`IdempotencyStore`.

Extracts the dedup key from an :class:`~avitoapi.events.Event` (default:
``event.dedup_key``) so callers dedup by event without knowing the key shape.
Mounted on the dispatch path and reused by the fanout hub.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..events._base import Event
    from .store import IdempotencyStore

KeyOf = Callable[["Event"], str]


def _default_key(event: Event) -> str:
    return event.dedup_key


class DedupFilter:
    """Accept-once over events, keyed by :attr:`Event.dedup_key` (overridable)."""

    def __init__(self, store: IdempotencyStore, *, key_of: KeyOf = _default_key) -> None:
        self._store = store
        self._key_of = key_of

    async def reserve(self, event: Event) -> bool:
        """``True`` if this event is newly claimed, ``False`` if a duplicate."""

        return await self._store.reserve(self._key_of(event))

    async def commit(self, event: Event) -> None:
        await self._store.commit(self._key_of(event))

    async def release(self, event: Event) -> None:
        await self._store.release(self._key_of(event))


__all__ = ["DedupFilter", "KeyOf"]

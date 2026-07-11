"""``IdempotencyStore`` — reserve / commit / release over a :class:`BaseStorage`.

The dispatcher (and the fanout hub) dedup at-least-once delivery with a
three-phase protocol:

* :meth:`reserve` — atomic set-if-absent with a short *in-flight* TTL. ``True``
  means we own this key and should process; ``False`` means someone else
  already has it (in-flight or committed) → skip.
* :meth:`commit` — on success, extend the key to the long *done* TTL so a later
  redelivery is recognised as a duplicate.
* :meth:`release` — on failure, drop the reservation so the event can be
  retried and reprocessed.

Atomicity rides on :meth:`BaseStorage.add`; on Redis/Postgres/Mongo backends
that is a native compare-and-set, so the guarantee holds across processes.
"""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..storage.base import BaseStorage

_INFLIGHT = "inflight"
_DONE = "done"


class IdempotencyStore:
    """Accept-once coordinator keyed by an opaque string.

    ``inflight_ttl`` bounds how long a crashed-mid-processing reservation
    blocks reprocessing; ``done_ttl`` bounds how long a committed key keeps
    deduping redeliveries. Pass a storage backend with native CAS
    (Redis/Postgres/Mongo) for cross-process guarantees; the in-memory backend
    is single-process only.
    """

    def __init__(
        self,
        storage: BaseStorage[object, str],
        *,
        inflight_ttl: timedelta = timedelta(minutes=5),
        done_ttl: timedelta = timedelta(hours=24),
        namespace: str = "idem",
    ) -> None:
        self._storage = storage.namespaced(namespace)
        self._inflight_ttl = inflight_ttl
        self._done_ttl = done_ttl

    async def reserve(self, key: str) -> bool:
        """Atomically claim ``key``. ``True`` if newly claimed, ``False`` if already known."""

        return await self._storage.add(key, _INFLIGHT, ttl=self._inflight_ttl)

    async def commit(self, key: str) -> None:
        """Mark ``key`` done — extend to the long retention TTL so redeliveries dedup."""

        await self._storage.put(key, _DONE, ttl=self._done_ttl)

    async def release(self, key: str) -> None:
        """Drop the reservation so a failed event can be retried and reprocessed."""

        await self._storage.delete(key)

    async def seen(self, key: str) -> bool:
        """Read-only probe — ``True`` if the key is reserved or committed."""

        return await self._storage.exists(key)


__all__ = ["IdempotencyStore"]

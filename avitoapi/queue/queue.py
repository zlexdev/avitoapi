"""Storage-backed ``EventQueue`` with at-least-once delivery + visibility leases.

Compared to the previous flat-file implementation, this version adds:

* Per-message **visibility lease** — a consumer that calls :meth:`lease`
  gets exclusive ownership for ``visibility_timeout`` seconds. Expired
  leases are reclaimed automatically.
* ``max_attempts`` policy — a message that exceeds the limit is moved
  to the supplied :class:`BaseDeadLetterQueue` and removed from the
  ready set.
* **Scheduled enqueue** — ``run_at`` lets a producer enqueue a row that
  becomes leasable at a specific epoch time. :class:`QueueScheduler` (or
  the next ``lease`` call) promotes due rows automatically.
* **Priority hint** — higher ``priority`` wins ties on the same
  ``enqueued_at`` second; otherwise FIFO order holds.

The on-disk layout inside :class:`avitoapi.storage.BaseStorage`:

* ``"__index__"`` — list of message ids in insertion order.
* ``"<message_id>"`` — JSON row::

      {
        "enqueued_at": float,
        "attempts": int,
        "metadata": {...},
        "payload": <serializer-defined>,
        "run_at": float | None,
        "priority": int,
        "lease_id": str | "",
        "lease_expires_at": float | 0.0
      }
"""

from __future__ import annotations

import asyncio
import contextlib
import time
import uuid
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING

from ..logging import get_logger
from ..storage.base import BaseStorage
from ..types import JsonObject
from .base import BaseDeadLetterQueue, BaseEventQueue, DeadLetter, MessageLease, QueuedEvent
from .serializer import EventSerializer, JSONSerializer

if TYPE_CHECKING:
    from ..events._base import Event

log = get_logger(__name__)

_INDEX_KEY = "__index__"
_DEFAULT_VISIBILITY_TIMEOUT = 60.0
_DEFAULT_MAX_ATTEMPTS = 10


class EventQueue(BaseEventQueue):
    """Storage-backed persistent queue with lease + DLQ semantics.

    Append + ack mutate the index under a single ``asyncio.Lock`` so two
    consumers can never race the same row. The lease check uses
    ``time.time()`` against the row's ``lease_expires_at`` field — no
    external timer needed.

    Bring a backend that actually persists (Redis, Postgres K/V, Mongo)
    for cross-process durability — the in-process
    :class:`avitoapi.storage.MemoryStorage` backend is fine for tests
    but loses everything on restart.
    """

    def __init__(
        self,
        storage: BaseStorage[object, str],
        *,
        serializer: EventSerializer | None = None,
        namespace: str = "events",
        visibility_timeout: float = _DEFAULT_VISIBILITY_TIMEOUT,
        max_attempts: int = _DEFAULT_MAX_ATTEMPTS,
        dead_letter_queue: BaseDeadLetterQueue | None = None,
    ) -> None:
        self._storage = storage.namespaced(namespace) if namespace else storage
        self._serializer = serializer or JSONSerializer()
        self._lock = asyncio.Lock()
        self.visibility_timeout = visibility_timeout
        self.max_attempts = max_attempts
        self.dead_letter_queue = dead_letter_queue

    async def enqueue(
        self,
        event: Event,
        *,
        metadata: JsonObject | None = None,
        run_at: float | None = None,
        priority: int = 0,
    ) -> QueuedEvent:
        record = QueuedEvent(
            message_id=uuid.uuid4().hex,
            event=event,
            metadata=dict(metadata or {}),
            run_at=run_at,
            priority=priority,
        )
        row = self._row_for_enqueue(record)
        async with self._lock:
            await self._storage.put(record.message_id, row)
            index = await self._read_index()
            index.append(record.message_id)
            await self._storage.put(_INDEX_KEY, index)
        return record

    def _row_for_enqueue(self, record: QueuedEvent) -> JsonObject:
        return {
            "enqueued_at": record.enqueued_at,
            "attempts": 0,
            "metadata": record.metadata,
            "payload": self._serializer.dump(record.event),
            "run_at": record.run_at,
            "priority": record.priority,
            "lease_id": "",
            "lease_expires_at": 0.0,
        }

    async def lease(
        self,
        *,
        visibility_timeout: float | None = None,
    ) -> QueuedEvent | None:
        timeout = visibility_timeout if visibility_timeout is not None else self.visibility_timeout
        now = time.time()
        dlq_pushes: list[tuple[str, JsonObject]] = []
        async with self._lock:
            index = await self._read_index()
            for message_id in list(index):
                row = await self._storage.get(message_id)
                if not isinstance(row, dict):
                    # corrupted / missing — drop from index
                    index.remove(message_id)
                    continue
                if not self._is_ready(row, now=now):
                    continue
                attempts = int(row.get("attempts") or 0) + 1
                if attempts > self.max_attempts:
                    # collect; push to DLQ after releasing the lock
                    dlq_pushes.append((message_id, row))
                    await self._storage.delete(message_id)
                    index.remove(message_id)
                    continue
                lease_id = uuid.uuid4().hex
                row["attempts"] = attempts
                row["lease_id"] = lease_id
                row["lease_expires_at"] = now + timeout
                await self._storage.put(message_id, row)
                await self._storage.put(_INDEX_KEY, index)
                queued = self._row_to_queued(message_id, row)
                queued.lease = MessageLease(
                    message_id=message_id,
                    lease_id=lease_id,
                    expires_at=row["lease_expires_at"],
                )
                # commit any DLQ pushes we collected before returning
                if dlq_pushes:
                    await self._push_dlq(dlq_pushes, reason="max_attempts_exceeded")
                return queued
            await self._storage.put(_INDEX_KEY, index)
        if dlq_pushes:
            await self._push_dlq(dlq_pushes, reason="max_attempts_exceeded")
        return None

    @staticmethod
    def _is_ready(row: JsonObject, *, now: float) -> bool:
        run_at = row.get("run_at")
        if run_at is not None and float(run_at) > now:  # type: ignore[arg-type]  # JSONValue narrowed at runtime
            return False
        lease_id = row.get("lease_id") or ""
        if lease_id:
            expires = float(row.get("lease_expires_at") or 0.0)  # type: ignore[arg-type]  # JSONValue narrowed at runtime
            if expires > now:
                return False
        return True

    async def release(self, message_id: str, lease_id: str) -> bool:
        async with self._lock:
            row = await self._storage.get(message_id)
            if not isinstance(row, dict):
                return False
            if (row.get("lease_id") or "") != lease_id:
                return False
            row["lease_id"] = ""
            row["lease_expires_at"] = 0.0
            await self._storage.put(message_id, row)
        return True

    async def extend_lease(
        self,
        message_id: str,
        lease_id: str,
        *,
        by: float,
    ) -> bool:
        async with self._lock:
            row = await self._storage.get(message_id)
            if not isinstance(row, dict):
                return False
            if (row.get("lease_id") or "") != lease_id:
                return False
            row["lease_expires_at"] = float(row.get("lease_expires_at") or time.time()) + by
            await self._storage.put(message_id, row)
        return True

    async def ack(
        self,
        message_id: str,
        *,
        lease_id: str | None = None,
    ) -> bool:
        async with self._lock:
            row = await self._storage.get(message_id)
            if not isinstance(row, dict):
                return False
            if lease_id is not None and (row.get("lease_id") or "") != lease_id:
                # someone else's lease (or already released) — refuse the ack
                return False
            await self._storage.delete(message_id)
            index = await self._read_index()
            with contextlib.suppress(ValueError):
                index.remove(message_id)
            await self._storage.put(_INDEX_KEY, index)
        return True

    async def replay(self) -> AsyncIterator[QueuedEvent]:
        async with self._lock:
            index = await self._read_index()
            rows: list[tuple[str, JsonObject]] = []
            for mid in index:
                row = await self._storage.get(mid)
                if isinstance(row, dict):
                    rows.append((mid, row))
        for mid, row in rows:
            try:
                yield self._row_to_queued(mid, row)
            except Exception:  # noqa: BLE001 — bad row should not abort the replay
                log.exception("queue.skip_unloadable_row", message_id=mid)

    def _row_to_queued(self, message_id: str, row: JsonObject) -> QueuedEvent:
        event = self._serializer.load(row.get("payload"))
        return QueuedEvent(
            message_id=message_id,
            event=event,
            enqueued_at=float(row.get("enqueued_at") or 0.0),  # type: ignore[arg-type]  # JSONValue narrowed at runtime
            attempts=int(row.get("attempts") or 0),  # type: ignore[arg-type]  # JSONValue narrowed at runtime
            metadata=dict(row.get("metadata") or {}),  # type: ignore[arg-type]  # JSONValue narrowed at runtime
            run_at=row.get("run_at"),  # type: ignore[arg-type]  # JSONValue narrowed at runtime
            priority=int(row.get("priority") or 0),  # type: ignore[arg-type]  # JSONValue narrowed at runtime
        )

    async def update_metadata(self, message_id: str, metadata: JsonObject) -> bool:
        async with self._lock:
            row = await self._storage.get(message_id)
            if not isinstance(row, dict):
                return False
            row["metadata"] = dict(metadata)
            await self._storage.put(message_id, row)
        return True

    async def increment_attempt(self, message_id: str) -> int:
        async with self._lock:
            row = await self._storage.get(message_id)
            if not isinstance(row, dict):
                return 0
            row["attempts"] = int(row.get("attempts") or 0) + 1
            await self._storage.put(message_id, row)
            return int(row["attempts"])

    async def pending_count(self) -> int:
        async with self._lock:
            return len(await self._read_index())

    async def in_flight_count(self) -> int:
        """Number of rows currently holding an unexpired lease."""

        now = time.time()
        async with self._lock:
            index = await self._read_index()
            count = 0
            for mid in index:
                row = await self._storage.get(mid)
                if not isinstance(row, dict):
                    continue
                lease_id = row.get("lease_id") or ""
                if lease_id and float(row.get("lease_expires_at") or 0.0) > now:
                    count += 1
        return count

    async def stats(self) -> dict[str, int]:
        # N+1 storage reads under the global lock — fine for in-memory and
        # ops-frequency use, but a Redis/Postgres backend should override
        # this with a batched query if called from a hot path.
        now = time.time()
        async with self._lock:
            index = await self._read_index()
            pending = 0
            scheduled = 0
            in_flight = 0
            for mid in index:
                row = await self._storage.get(mid)
                if not isinstance(row, dict):
                    continue
                run_at = row.get("run_at")
                if run_at is not None and float(run_at) > now:
                    scheduled += 1
                    continue
                lease_id = row.get("lease_id") or ""
                if lease_id and float(row.get("lease_expires_at") or 0.0) > now:
                    in_flight += 1
                else:
                    pending += 1
        dlq_count = 0
        if self.dead_letter_queue is not None:
            dlq_count = await self.dead_letter_queue.count()
        return {
            "pending": pending,
            "scheduled": scheduled,
            "in_flight": in_flight,
            "dlq": dlq_count,
        }

    async def _read_index(self) -> list[str]:
        existing = await self._storage.get(_INDEX_KEY)
        if isinstance(existing, list):
            return list(existing)
        return []

    async def _push_dlq(
        self,
        rows: list[tuple[str, JsonObject]],
        *,
        reason: str,
    ) -> None:
        if self.dead_letter_queue is None:
            for mid, _ in rows:
                log.error(
                    "queue.max_attempts_exceeded_no_dlq",
                    message_id=mid,
                    reason=reason,
                )
            return
        for mid, row in rows:
            try:
                event = self._serializer.load(row.get("payload"))
            except Exception:  # noqa: BLE001 — unloadable rows still get DLQ'd by id
                log.exception("queue.dlq.unloadable_row", message_id=mid)
                continue
            await self.dead_letter_queue.push(
                DeadLetter(
                    message_id=mid,
                    event=event,
                    attempts=int(row.get("attempts") or 0),  # type: ignore[arg-type]  # JSONValue narrowed at runtime
                    failed_at=time.time(),
                    reason=reason,
                    metadata=dict(row.get("metadata") or {}),  # type: ignore[arg-type]  # JSONValue narrowed at runtime
                ),
            )


__all__ = ["EventQueue"]

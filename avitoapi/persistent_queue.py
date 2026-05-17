"""Persistent event queue with atomic at-least-once delivery.

Every event entering the :class:`Dispatcher` is first appended to the
queue. The handler receives an :class:`EventContext` carrying
:meth:`atomic_completed` — calling it atomically removes the message
from the queue. Without that call (handler raised, process killed) the
message stays in the queue and is replayed on the next startup.

The queue itself does **not** implement storage — it composes a
:class:`avitoapi.storage.BaseStorage` instance. Bring any backend you
like:

* :class:`avitoapi.storage.MemoryStorage` — process-local (default).
* SQL / Redis / Mongo K/V stores once implemented under
  :mod:`avitoapi.storage`.
"""
from __future__ import annotations

import asyncio
import contextlib
import pickle
import time
import uuid
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .logging import get_logger
from .storage.base import BaseStorage

if TYPE_CHECKING:
    from .events._base import Event

log = get_logger(__name__)

_INDEX_KEY = "__index__"


@dataclass(slots=True)
class QueuedEvent:
    """One persisted event.

    ``message_id`` is a stable identifier the queue assigns at enqueue
    time; :meth:`EventQueue.ack` uses it to atomically delete the row.
    """

    message_id: str
    event: Event
    enqueued_at: float = field(default_factory=time.time)
    attempts: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class EventSerializer(ABC):
    """Convert :class:`Event` instances to/from a JSON-friendly form for storage."""

    @abstractmethod
    def dump(self, event: Event) -> Any: ...

    @abstractmethod
    def load(self, payload: Any) -> Event: ...


class PickleSerializer(EventSerializer):
    """Default serialiser — pickle, base64 in storage for JSON friendliness."""

    def dump(self, event: Event) -> str:
        import base64

        return base64.b64encode(pickle.dumps(event)).decode("ascii")

    def load(self, payload: Any) -> Event:
        import base64

        if not isinstance(payload, str):
            raise ValueError(f"PickleSerializer expected str payload, got {type(payload).__name__}")
        return pickle.loads(base64.b64decode(payload.encode("ascii")))  # noqa: S301


class BaseEventQueue(ABC):
    """Storage backend contract.

    * :meth:`enqueue` is durable before returning.
    * :meth:`ack` is atomic — the row is gone or untouched.
    * :meth:`replay` yields every unacked message at startup.
    * :meth:`update_metadata` lets pipeline runners checkpoint progress.
    """

    @abstractmethod
    async def enqueue(self, event: Event, *, metadata: dict[str, Any] | None = None) -> QueuedEvent: ...

    @abstractmethod
    async def ack(self, message_id: str) -> bool: ...

    @abstractmethod
    def replay(self) -> AsyncIterator[QueuedEvent]: ...

    @abstractmethod
    async def update_metadata(self, message_id: str, metadata: dict[str, Any]) -> bool: ...

    @abstractmethod
    async def pending_count(self) -> int: ...

    async def close(self) -> None:
        """Optional teardown hook. Idempotent."""


class EventQueue(BaseEventQueue):
    """Storage-backed persistent queue.

    Layout inside the supplied :class:`BaseStorage`:

    * ``"__index__"`` — JSON list of ``message_id``s in insertion order.
    * ``"<message_id>"`` — JSON ``{enqueued_at, attempts, metadata, payload}``.

    Append + ack mutate the index under a single ``asyncio.Lock`` so two
    handlers can never race the same message. Bring a backend that
    actually persists (Redis, Postgres K/V, Mongo) for cross-process
    durability — the in-process :class:`avitoapi.storage.MemoryStorage`
    backend is fine for tests but loses everything on restart.
    """

    def __init__(
        self,
        storage: BaseStorage[Any, str],
        *,
        serializer: EventSerializer | None = None,
        namespace: str = "events",
    ) -> None:
        self._storage = storage.namespaced(namespace) if namespace else storage
        self._serializer = serializer or PickleSerializer()
        self._lock = asyncio.Lock()

    async def enqueue(
        self,
        event: Event,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> QueuedEvent:
        record = QueuedEvent(
            message_id=uuid.uuid4().hex,
            event=event,
            metadata=dict(metadata or {}),
        )
        row = {
            "enqueued_at": record.enqueued_at,
            "attempts": 0,
            "metadata": record.metadata,
            "payload": self._serializer.dump(event),
        }
        async with self._lock:
            await self._storage.put(record.message_id, row)
            index = await self._read_index()
            index.append(record.message_id)
            await self._storage.put(_INDEX_KEY, index)
        return record

    async def ack(self, message_id: str) -> bool:
        async with self._lock:
            existing = await self._storage.get(message_id)
            if existing is None:
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
            rows: list[tuple[str, dict[str, Any]]] = []
            for mid in index:
                row = await self._storage.get(mid)
                if isinstance(row, dict):
                    rows.append((mid, row))
        for mid, row in rows:
            try:
                event = self._serializer.load(row.get("payload"))
            except Exception:  # noqa: BLE001 — bad row should not abort the replay
                log.exception("queue.skip_unloadable_row", message_id=mid)
                continue
            yield QueuedEvent(
                message_id=mid,
                event=event,
                enqueued_at=float(row.get("enqueued_at") or 0.0),
                attempts=int(row.get("attempts") or 0),
                metadata=dict(row.get("metadata") or {}),
            )

    async def update_metadata(self, message_id: str, metadata: dict[str, Any]) -> bool:
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

    async def _read_index(self) -> list[str]:
        existing = await self._storage.get(_INDEX_KEY)
        if isinstance(existing, list):
            return list(existing)
        return []


__all__ = [
    "BaseEventQueue",
    "EventQueue",
    "EventSerializer",
    "PickleSerializer",
    "QueuedEvent",
]

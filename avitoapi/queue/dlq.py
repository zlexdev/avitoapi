"""Dead-letter queue implementations."""

from __future__ import annotations

import asyncio
import time

from ..logging import get_logger
from ..storage.base import BaseStorage
from ..types import JsonObject
from .base import BaseDeadLetterQueue, DeadLetter
from .serializer import EventSerializer, JSONSerializer

log = get_logger(__name__)

_INDEX_KEY = "__index__"


class MemoryDeadLetterQueue(BaseDeadLetterQueue):
    """In-process DLQ — keeps letters in a list. Lost on restart."""

    def __init__(self) -> None:
        self._letters: list[DeadLetter] = []
        self._lock = asyncio.Lock()

    async def push(self, letter: DeadLetter) -> None:
        async with self._lock:
            self._letters.append(letter)
        log.warning(
            "queue.dlq.pushed",
            message_id=letter.message_id,
            attempts=letter.attempts,
            reason=letter.reason,
        )

    async def pop_all(self) -> list[DeadLetter]:
        async with self._lock:
            out = list(self._letters)
            self._letters.clear()
            return out

    async def count(self) -> int:
        async with self._lock:
            return len(self._letters)


class StorageDeadLetterQueue(BaseDeadLetterQueue):
    """DLQ persisted through any :class:`BaseStorage`.

    Layout:

    * ``"__index__"`` — list of letter ids in insertion order.
    * ``"<letter_id>"`` — ``{message_id, attempts, failed_at, reason,
      payload, metadata}``.

    Stored event payload uses the same :class:`EventSerializer` shape
    as the main queue (default JSON). Bring a real backend (Redis,
    Postgres) so DLQ survives restarts — :class:`MemoryDeadLetterQueue`
    is fine only for tests.
    """

    def __init__(
        self,
        storage: BaseStorage[object, str],
        *,
        serializer: EventSerializer | None = None,
        namespace: str = "dlq",
    ) -> None:
        self._storage = storage.namespaced(namespace) if namespace else storage
        self._serializer = serializer or JSONSerializer()
        self._lock = asyncio.Lock()

    async def push(self, letter: DeadLetter) -> None:
        row = {
            "message_id": letter.message_id,
            "attempts": letter.attempts,
            "failed_at": letter.failed_at,
            "reason": letter.reason,
            "metadata": letter.metadata,
            "payload": self._serializer.dump(letter.event),
        }
        async with self._lock:
            await self._storage.put(letter.message_id, row)
            index = await self._read_index()
            index.append(letter.message_id)
            await self._storage.put(_INDEX_KEY, index)
        log.warning(
            "queue.dlq.pushed",
            message_id=letter.message_id,
            attempts=letter.attempts,
            reason=letter.reason,
        )

    async def pop_all(self) -> list[DeadLetter]:
        async with self._lock:
            index = await self._read_index()
            rows: list[tuple[str, JsonObject]] = []
            for letter_id in index:
                row = await self._storage.get(letter_id)
                if isinstance(row, dict):
                    rows.append((letter_id, row))
                await self._storage.delete(letter_id)
            await self._storage.put(_INDEX_KEY, [])

        out: list[DeadLetter] = []
        for letter_id, row in rows:
            try:
                event = self._serializer.load(row.get("payload"))
            except Exception:  # noqa: BLE001 — bad row should not abort pop_all
                log.exception("queue.dlq.skip_unloadable_row", message_id=letter_id)
                continue
            out.append(
                DeadLetter(
                    message_id=str(row.get("message_id") or letter_id),
                    event=event,
                    attempts=int(row.get("attempts") or 0),  # type: ignore[arg-type]  # JSONValue narrowed at runtime
                    failed_at=float(row.get("failed_at") or time.time()),  # type: ignore[arg-type]  # JSONValue narrowed at runtime
                    reason=str(row.get("reason") or ""),
                    metadata=dict(row.get("metadata") or {}),  # type: ignore[arg-type]  # JSONValue narrowed at runtime
                ),
            )
        return out

    async def count(self) -> int:
        async with self._lock:
            return len(await self._read_index())

    async def _read_index(self) -> list[str]:
        existing = await self._storage.get(_INDEX_KEY)
        if isinstance(existing, list):
            return list(existing)
        return []


__all__ = ["MemoryDeadLetterQueue", "StorageDeadLetterQueue"]

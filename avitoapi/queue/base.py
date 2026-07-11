"""Base contracts: ``BaseEventQueue``, ``QueuedEvent``, ``MessageLease``, ``BaseDeadLetterQueue``.

The queue and the dead-letter queue are split into separate ABCs so a
deployment can mix backends (e.g. Postgres queue + S3 DLQ). Both sit
on top of :class:`avitoapi.storage.BaseStorage` in the default impls
but the ABCs do not assume any particular storage.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..types import JsonObject

if TYPE_CHECKING:
    from ..events._base import Event


@dataclass(slots=True)
class MessageLease:
    """Active reservation of a queue row.

    A consumer that successfully :meth:`BaseEventQueue.lease` s a message
    gets back a :class:`MessageLease` next to the :class:`QueuedEvent`.
    The lease must be returned via :meth:`BaseEventQueue.ack` (success)
    or :meth:`BaseEventQueue.release` (give up, let someone else retry)
    before :attr:`expires_at`. After expiry the queue treats the row as
    abandoned and re-leases it on the next pull.
    """

    message_id: str
    lease_id: str
    expires_at: float

    def is_expired(self, *, now: float | None = None) -> bool:
        return (now if now is not None else time.time()) >= self.expires_at


@dataclass(slots=True)
class QueuedEvent:
    """One persisted event.

    ``message_id`` is a stable identifier the queue assigns at enqueue
    time. ``run_at`` (when set) defers delivery: queues with scheduling
    support skip rows whose ``run_at`` is in the future. ``priority``
    is a hint — higher priority leases first when supported.
    """

    message_id: str
    event: Event
    enqueued_at: float = field(default_factory=time.time)
    attempts: int = 0
    metadata: JsonObject = field(default_factory=dict)
    run_at: float | None = None
    priority: int = 0
    lease: MessageLease | None = None


class BaseEventQueue(ABC):
    """Storage backend contract.

    * :meth:`enqueue` is durable before returning. Accepts ``run_at`` /
      ``priority`` / ``metadata``.
    * :meth:`lease` atomically reserves the oldest ready message for a
      ``visibility_timeout`` window. Returns ``None`` when nothing is
      ready (empty queue, or every row is leased / scheduled in the
      future).
    * :meth:`release` returns a leased row to the pool without bumping
      its attempt count beyond the lease attempt.
    * :meth:`ack` removes the row. Idempotent; second call returns ``False``.
    * :meth:`replay` iterates every unacked row (no leasing) — used at
      startup to re-deliver leftover state.
    * :meth:`update_metadata` lets handlers checkpoint progress.
    * :meth:`pending_count` reports ready-to-deliver rows (excludes DLQ).

    Backends that don't support a feature (e.g. priority) should
    implement it as a no-op rather than raising.
    """

    @abstractmethod
    async def enqueue(
        self,
        event: Event,
        *,
        metadata: JsonObject | None = None,
        run_at: float | None = None,
        priority: int = 0,
    ) -> QueuedEvent: ...

    @abstractmethod
    async def lease(
        self,
        *,
        visibility_timeout: float | None = None,
    ) -> QueuedEvent | None: ...

    @abstractmethod
    async def release(self, message_id: str, lease_id: str) -> bool: ...

    @abstractmethod
    async def extend_lease(
        self,
        message_id: str,
        lease_id: str,
        *,
        by: float,
    ) -> bool: ...

    @abstractmethod
    async def ack(
        self,
        message_id: str,
        *,
        lease_id: str | None = None,
    ) -> bool: ...

    @abstractmethod
    def replay(self) -> AsyncIterator[QueuedEvent]: ...

    @abstractmethod
    async def update_metadata(
        self,
        message_id: str,
        metadata: JsonObject,
    ) -> bool: ...

    @abstractmethod
    async def increment_attempt(self, message_id: str) -> int: ...

    @abstractmethod
    async def pending_count(self) -> int: ...

    async def close(self) -> None:
        """Optional teardown hook. Idempotent."""


@dataclass(slots=True)
class DeadLetter:
    """One row in the dead-letter queue."""

    message_id: str
    event: Event
    attempts: int
    failed_at: float
    reason: str
    metadata: JsonObject = field(default_factory=dict)


class BaseDeadLetterQueue(ABC):
    """Drop site for messages that exceeded ``max_attempts``.

    The DLQ is read-mostly by ops tools; the queue itself only writes.
    Implementations may persist via :class:`avitoapi.storage.BaseStorage`
    or keep an in-process list for tests.
    """

    @abstractmethod
    async def push(self, letter: DeadLetter) -> None: ...

    @abstractmethod
    async def pop_all(self) -> list[DeadLetter]: ...

    @abstractmethod
    async def count(self) -> int: ...


__all__ = [
    "BaseDeadLetterQueue",
    "BaseEventQueue",
    "DeadLetter",
    "MessageLease",
    "QueuedEvent",
]

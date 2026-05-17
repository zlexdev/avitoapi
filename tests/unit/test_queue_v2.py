"""Unit tests for queue-v2: lease, DLQ, scheduled enqueue, JSONSerializer, worker, partition."""

from __future__ import annotations

import asyncio
import time
from datetime import timedelta

import pytest
from avitoapi import (
    BaseEvent,
    EventQueue,
    EventRegistry,
    JSONSerializer,
    MemoryDeadLetterQueue,
    QueuedEvent,
    QueueWorker,
    enqueue_later,
)
from avitoapi.storage.memory import MemoryStorage


class _Ping(BaseEvent, event_name="test.ping.v2"):
    def __init__(self, *, value: int = 0) -> None:
        super().__init__()
        self.value = value


@pytest.fixture(autouse=True)
def _reset_registry():
    # Keep registry independent between tests so name clashes don't cross over.
    return
    # We don't fully clear because Event.registry already holds the Avito events;
    # JSONSerializer auto-registers them lazily on construction.


# ---------------------------------------------------------------- 3. JSONSerializer + EventRegistry


async def test_json_serializer_roundtrips_event():
    serializer = JSONSerializer()
    payload = serializer.dump(_Ping(value=42))
    assert payload["type"] == "test.ping.v2"
    assert payload["data"] == {"value": 42}
    back = serializer.load(payload)
    assert isinstance(back, _Ping)
    assert back.value == 42


async def test_event_registry_explicit_register_with_alias():
    class _Banana(BaseEvent):
        def __init__(self, *, ripe: bool = True) -> None:
            super().__init__()
            self.ripe = ripe

    EventRegistry.register(_Banana, name="fruit.banana")
    assert EventRegistry.get("fruit.banana") is _Banana


async def test_event_registry_rejects_conflicting_registration():
    class _A(BaseEvent, event_name="dup.collision"):
        pass

    class _B(BaseEvent):
        pass

    EventRegistry.register(_A)
    with pytest.raises(Exception, match="already registered"):
        EventRegistry.register(_B, name="dup.collision")


# ---------------------------------------------------------------- 2. lease + max_attempts + DLQ


async def test_lease_marks_message_in_flight():
    queue = EventQueue(MemoryStorage(), visibility_timeout=10.0)
    await queue.enqueue(_Ping(value=1))
    leased = await queue.lease()
    assert leased is not None
    assert leased.lease is not None
    assert leased.lease.lease_id

    # A second lease must not return the same row — it's in-flight.
    second = await queue.lease()
    assert second is None


async def test_lease_expires_after_visibility_timeout():
    queue = EventQueue(MemoryStorage(), visibility_timeout=0.05)
    await queue.enqueue(_Ping(value=1))
    leased = await queue.lease()
    assert leased is not None
    # Sleep past the timeout — next lease should reclaim.
    await asyncio.sleep(0.08)
    reclaimed = await queue.lease()
    assert reclaimed is not None
    assert reclaimed.message_id == leased.message_id
    assert reclaimed.attempts == 2  # second attempt after re-lease


async def test_release_returns_lease_without_ack():
    queue = EventQueue(MemoryStorage())
    await queue.enqueue(_Ping(value=1))
    leased = await queue.lease()
    assert leased is not None
    assert leased.lease is not None
    assert await queue.release(leased.message_id, leased.lease.lease_id) is True
    # After release, immediate re-lease must succeed.
    re_leased = await queue.lease()
    assert re_leased is not None


async def test_ack_rejects_foreign_lease_id():
    queue = EventQueue(MemoryStorage())
    await queue.enqueue(_Ping(value=1))
    leased = await queue.lease()
    assert leased is not None
    assert await queue.ack(leased.message_id, lease_id="not-mine") is False
    assert await queue.pending_count() == 1


async def test_max_attempts_moves_to_dlq():
    dlq = MemoryDeadLetterQueue()
    queue = EventQueue(
        MemoryStorage(),
        visibility_timeout=0.01,
        max_attempts=2,
        dead_letter_queue=dlq,
    )
    await queue.enqueue(_Ping(value=7))
    # Lease twice without acking — third lease pushes to DLQ.
    a = await queue.lease()
    assert a is not None
    await asyncio.sleep(0.02)
    b = await queue.lease()
    assert b is not None
    await asyncio.sleep(0.02)
    c = await queue.lease()
    assert c is None  # exhausted → moved to DLQ
    letters = await dlq.pop_all()
    assert len(letters) == 1
    assert letters[0].reason == "max_attempts_exceeded"


# ---------------------------------------------------------------- 6. scheduled enqueue + run_at


async def test_run_at_defers_lease_until_due():
    queue = EventQueue(MemoryStorage())
    await queue.enqueue(_Ping(value=1), run_at=time.time() + 0.1)
    assert await queue.lease() is None  # not yet due
    await asyncio.sleep(0.12)
    leased = await queue.lease()
    assert leased is not None


async def test_enqueue_later_helper_uses_delay():
    queue = EventQueue(MemoryStorage())
    await enqueue_later(queue, _Ping(value=5), delay=timedelta(milliseconds=50))
    assert await queue.lease() is None
    await asyncio.sleep(0.07)
    leased = await queue.lease()
    assert leased is not None
    assert isinstance(leased.event, _Ping)


# ---------------------------------------------------------------- stats


async def test_stats_buckets_pending_scheduled_in_flight():
    queue = EventQueue(MemoryStorage(), visibility_timeout=5.0)
    await queue.enqueue(_Ping(value=1))
    await queue.enqueue(_Ping(value=2), run_at=time.time() + 5)
    leased = await queue.lease()
    assert leased is not None
    stats = await queue.stats()
    assert stats["in_flight"] == 1
    assert stats["scheduled"] == 1
    assert stats["pending"] == 0


# ---------------------------------------------------------------- 11. QueueWorker (concurrency + partition)


async def test_worker_acks_on_handler_success():
    queue = EventQueue(MemoryStorage())
    seen: list[int] = []

    async def _handle(queued: QueuedEvent) -> bool:
        seen.append(queued.event.value)
        return True

    worker = QueueWorker(queue, _handle, concurrency=2, poll_interval=0.01)
    for v in range(5):
        await queue.enqueue(_Ping(value=v))
    await worker.start()
    try:
        await worker.drain(timeout=2.0)
    finally:
        await worker.stop()
    assert sorted(seen) == [0, 1, 2, 3, 4]
    assert await queue.pending_count() == 0


async def test_worker_releases_on_handler_failure():
    queue = EventQueue(MemoryStorage(), visibility_timeout=0.05, max_attempts=10)

    async def _handle(queued: QueuedEvent) -> bool:
        raise RuntimeError("nope")

    worker = QueueWorker(queue, _handle, concurrency=1, poll_interval=0.01)
    await queue.enqueue(_Ping(value=1))
    await worker.start()
    await asyncio.sleep(0.2)
    await worker.stop()
    # Row must still be present (released, not ack'd).
    assert await queue.pending_count() == 1


# ---------------------------------------------------------------- 9. partition_by


async def test_worker_serialises_same_partition_key():
    queue = EventQueue(MemoryStorage())
    in_progress = {"count": 0}
    max_seen = {"val": 0}
    lock = asyncio.Lock()

    async def _handle(queued: QueuedEvent) -> bool:
        async with lock:
            in_progress["count"] += 1
            max_seen["val"] = max(max_seen["val"], in_progress["count"])
        await asyncio.sleep(0.02)
        async with lock:
            in_progress["count"] -= 1
        return True

    # All events share the same partition key — must never run concurrently
    # even with concurrency=4.
    worker = QueueWorker(
        queue,
        _handle,
        concurrency=4,
        poll_interval=0.005,
        partition_by=lambda ev: "same-key",
    )
    for _ in range(6):
        await queue.enqueue(_Ping(value=1))
    await worker.start()
    try:
        await worker.drain(timeout=3.0)
    finally:
        await worker.stop()
    assert max_seen["val"] == 1


async def test_worker_parallelises_distinct_partitions():
    queue = EventQueue(MemoryStorage())
    in_progress = {"count": 0}
    max_seen = {"val": 0}
    lock = asyncio.Lock()

    async def _handle(queued: QueuedEvent) -> bool:
        async with lock:
            in_progress["count"] += 1
            max_seen["val"] = max(max_seen["val"], in_progress["count"])
        await asyncio.sleep(0.05)
        async with lock:
            in_progress["count"] -= 1
        return True

    worker = QueueWorker(
        queue,
        _handle,
        concurrency=4,
        poll_interval=0.005,
        partition_by=lambda ev: f"k-{ev.value}",
    )
    for v in range(4):
        await queue.enqueue(_Ping(value=v))
    await worker.start()
    try:
        await worker.drain(timeout=3.0)
    finally:
        await worker.stop()
    assert max_seen["val"] >= 2


__all__: list[str] = []

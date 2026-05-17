"""Unit tests for :class:`EventQueue` and the dispatcher ack/replay loop."""

from __future__ import annotations

from avitoapi import (
    BaseEvent,
    CtxQueue,
    Dispatcher,
    EventContext,
    EventQueue,
    HandlerType,
)
from avitoapi.storage.memory import MemoryStorage


class _Pinged(BaseEvent, event_name="test.pinged"):
    def __init__(self, *, value: int = 0) -> None:
        super().__init__()
        self.value = value


async def test_enqueue_persists_under_storage():
    storage = MemoryStorage()
    queue = EventQueue(storage)
    record = await queue.enqueue(_Pinged(value=42))
    assert record.message_id
    assert await queue.pending_count() == 1


async def test_ack_atomically_removes():
    queue = EventQueue(MemoryStorage())
    record = await queue.enqueue(_Pinged(value=1))
    assert await queue.ack(record.message_id) is True
    assert await queue.ack(record.message_id) is False
    assert await queue.pending_count() == 0


async def test_replay_yields_unacked_events_in_order():
    queue = EventQueue(MemoryStorage())
    first = await queue.enqueue(_Pinged(value=1))
    second = await queue.enqueue(_Pinged(value=2))
    third = await queue.enqueue(_Pinged(value=3))
    await queue.ack(second.message_id)

    ids = []
    async for queued in queue.replay():
        ids.append(queued.message_id)
    assert ids == [first.message_id, third.message_id]


async def test_dispatcher_calls_atomic_completed_to_drop_event():
    dispatcher = Dispatcher()
    triggered = []

    async def _handler(event, ctx: EventContext):
        triggered.append((event.value, ctx.queue.message_id, ctx.handler_type))
        await ctx.atomic_completed()

    dispatcher._manager("test.pinged", lambda ev: isinstance(ev, _Pinged)).register(_handler)
    await dispatcher.feed_event(_Pinged(value=7))
    assert triggered
    assert triggered[0][0] == 7
    assert triggered[0][2] is HandlerType.HANDLER
    assert await dispatcher.event_queue.pending_count() == 0


async def test_unacked_event_replayed_after_restart():
    storage = MemoryStorage()
    queue = EventQueue(storage)
    dispatcher = Dispatcher(event_queue=queue)
    seen_first_run = []

    async def _drop(event, ctx: EventContext):
        # Intentionally do NOT call ctx.atomic_completed.
        seen_first_run.append(event.value)

    dispatcher._manager("test.pinged", lambda ev: isinstance(ev, _Pinged)).register(_drop)
    await dispatcher.feed_event(_Pinged(value=99))
    assert seen_first_run == [99]
    assert await queue.pending_count() == 1

    # Simulate a restart — same storage, new dispatcher with a new handler that acks.
    replayed = []

    new_dispatcher = Dispatcher(event_queue=EventQueue(storage))

    async def _ack_now(event, ctx: EventContext):
        replayed.append((event.value, ctx.queue.attempts))
        await ctx.atomic_completed()

    new_dispatcher._manager("test.pinged", lambda ev: isinstance(ev, _Pinged)).register(_ack_now)
    count = await new_dispatcher.replay_pending()
    assert count == 1
    assert replayed
    assert replayed[0][0] == 99
    assert replayed[0][1] >= 1
    assert await new_dispatcher.event_queue.pending_count() == 0


async def test_ctx_queue_persist_metadata_round_trips():
    storage = MemoryStorage()
    queue = EventQueue(storage)
    record = await queue.enqueue(_Pinged(value=1))

    ctx_queue = CtxQueue(
        message_id=record.message_id,
        attempts=0,
        queued_at=record.enqueued_at,
        metadata={"pipeline:foo": {"completed": ["validate"]}},
        _ack=queue.ack,
        _update_metadata=queue.update_metadata,
    )
    assert await ctx_queue.persist_metadata() is True
    # Replay should now carry the metadata back.
    async for queued in queue.replay():
        assert queued.metadata == {"pipeline:foo": {"completed": ["validate"]}}

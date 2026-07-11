"""Dispatch-boundary accept-once: dedup, auto-ack, failure → DLQ + release."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from avitoapi.dispatcher import Dispatcher
from avitoapi.events.orders import OrderCreated


def _order(order_id: str = "o1") -> OrderCreated:
    # Fresh created_at each call — mimics the webhook re-synthesising the timestamp
    # on redelivery. dedup_key must ignore it.
    return OrderCreated(account_id="a", order_id=order_id, created_at=datetime.now(UTC))


async def test_redelivered_event_dispatched_once() -> None:
    d = Dispatcher()
    calls: list[str] = []

    @d.order_created()
    async def _h(ev: OrderCreated, _ctx: object) -> None:
        calls.append(ev.order_id)

    r1 = await d.feed_event(_order())
    r2 = await d.feed_event(_order())  # redelivery, fresh created_at
    pending = await d.event_queue.pending_count()

    assert calls == ["o1"]
    assert r1 is True
    assert r2 is False
    assert pending == 0  # both rows auto-acked


async def test_distinct_events_both_dispatched() -> None:
    d = Dispatcher()
    calls: list[str] = []

    @d.order_created()
    async def _h(ev: OrderCreated, _ctx: object) -> None:
        calls.append(ev.order_id)

    await d.feed_event(_order("o1"))
    await d.feed_event(_order("o2"))
    assert sorted(calls) == ["o1", "o2"]


@pytest.mark.filterwarnings("ignore::UserWarning")  # structlog dev pretty-exc warning on log.exception
async def test_handler_failure_dlqs_releases_and_acks() -> None:
    d = Dispatcher()
    seen: list[str] = []

    @d.order_created()
    async def _boom(ev: OrderCreated, _ctx: object) -> None:
        seen.append(ev.order_id)
        raise RuntimeError("handler blew up")

    # First delivery fails: no exception leaks, DLQ records it, queue row acked.
    result = await d.feed_event(_order())
    dlq_count = await d.dlq.count()
    pending = await d.event_queue.pending_count()

    # Reservation was released → a redelivery is reprocessed (not silently deduped).
    await d.feed_event(_order())

    assert result is False           # failure isolated, no raise into caller
    assert dlq_count == 1
    assert pending == 0              # failed row acked (DLQ is its single home)
    assert seen == ["o1", "o1"]      # released → reprocessed on redelivery

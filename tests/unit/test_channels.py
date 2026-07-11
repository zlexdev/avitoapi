"""Push-channel overflow policies + drain into the dispatcher."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime

import pytest
from avitoapi.channels import ChannelFull, ChannelOverflow, MemoryEventChannel
from avitoapi.dispatcher import Dispatcher
from avitoapi.events.orders import OrderCreated


def _order(order_id: str) -> OrderCreated:
    return OrderCreated(account_id="a", order_id=order_id, created_at=datetime.now(UTC))


async def test_drop_new_rejects_when_full() -> None:
    ch = MemoryEventChannel("c", maxsize=2, overflow=ChannelOverflow.DROP_NEW)
    a = await ch.publish(_order("1"))
    b = await ch.publish(_order("2"))
    c = await ch.publish(_order("3"))  # full → dropped
    assert (a, b, c) == (True, True, False)
    assert ch.qsize() == 2
    await ch.close()


async def test_drop_oldest_evicts_head() -> None:
    ch = MemoryEventChannel("c", maxsize=2, overflow=ChannelOverflow.DROP_OLDEST)
    for i in ("1", "2", "3"):
        await ch.publish(_order(i))
    await ch.close()
    assert [ev.order_id async for ev in ch.stream()] == ["2", "3"]  # "1" evicted


async def test_raise_policy_raises_when_full() -> None:
    ch = MemoryEventChannel("c", maxsize=1, overflow=ChannelOverflow.RAISE)
    await ch.publish(_order("1"))
    with pytest.raises(ChannelFull):
        await ch.publish(_order("2"))
    await ch.close()


async def test_channel_drains_into_dispatcher() -> None:
    d = Dispatcher()
    seen: list[str] = []

    @d.order_created()
    async def _h(ev: OrderCreated, _ctx: object) -> None:
        seen.append(ev.order_id)

    d.channels.register(MemoryEventChannel("poll", maxsize=8))
    d.run_channels()
    await d.publish("poll", _order("1"))
    await d.publish("poll", _order("2"))
    await asyncio.sleep(0.02)  # let the drain worker run
    await d.shutdown()
    assert sorted(seen) == ["1", "2"]


async def test_block_policy_backpressures_then_accepts() -> None:
    ch = MemoryEventChannel("c", maxsize=1, overflow=ChannelOverflow.BLOCK)
    await ch.publish(_order("1"))
    # queue full; publish blocks until a consumer frees a slot.
    pub = asyncio.create_task(ch.publish(_order("2")))
    await asyncio.sleep(0.01)
    assert not pub.done()  # backpressured
    gen = ch.stream()
    _ = await anext(gen)  # consume one → frees a slot
    accepted = await pub
    assert accepted is True
    assert ch.qsize() == 1
    await gen.aclose()  # don't leak the suspended async generator
    await ch.close()

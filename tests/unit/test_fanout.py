"""SourceHub: merge sources into the dispatcher + supervised restart on failure."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from datetime import UTC, datetime

import pytest
from avitoapi.dispatcher import Dispatcher
from avitoapi.events.orders import OrderCreated
from avitoapi.fanout import BaseEventSource, SourceHub, SupervisionPolicy


def _order(order_id: str) -> OrderCreated:
    return OrderCreated(account_id="a", order_id=order_id, created_at=datetime.now(UTC))


class _ListSource(BaseEventSource):
    def __init__(self, name: str, order_ids: list[str]) -> None:
        self.name = name
        self._order_ids = order_ids

    async def stream(self) -> AsyncIterator[OrderCreated]:
        for oid in self._order_ids:
            yield _order(oid)


class _FlakySource(BaseEventSource):
    """Fails once (after emitting one event), then succeeds on restart."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._runs = 0

    async def stream(self) -> AsyncIterator[OrderCreated]:
        self._runs += 1
        if self._runs == 1:
            yield _order("first")
            raise RuntimeError("boom")
        yield _order("second")


async def test_hub_merges_sources_into_dispatcher() -> None:
    d = Dispatcher()
    seen: list[str] = []

    @d.order_created()
    async def _h(ev: OrderCreated, _ctx: object) -> None:
        seen.append(ev.order_id)

    hub = SourceHub(dispatcher=d)
    hub.add_source(_ListSource("s1", ["1", "2"]))
    hub.add_source(_ListSource("s2", ["3"]))
    await hub.start()
    await asyncio.sleep(0.05)
    await hub.stop()
    await d.shutdown()
    assert sorted(seen) == ["1", "2", "3"]


@pytest.mark.filterwarnings("ignore::UserWarning")
async def test_failed_source_is_restarted() -> None:
    d = Dispatcher()
    seen: list[str] = []

    @d.order_created()
    async def _h(ev: OrderCreated, _ctx: object) -> None:
        seen.append(ev.order_id)

    hub = SourceHub(
        dispatcher=d,
        supervision=SupervisionPolicy(base_delay=0.001, jitter=False, max_restarts=3),
    )
    hub.add_source(_FlakySource("flaky"))
    await hub.start()
    await asyncio.sleep(0.05)
    restarts = hub.health().total_restarts
    await hub.stop()
    await d.shutdown()

    assert sorted(seen) == ["first", "second"]  # pre-crash + post-restart event delivered
    assert restarts >= 1

"""Contract tests for the pull-based :class:`~avitoapi.polling.PollingRunner` feed."""

from __future__ import annotations

import asyncio

import pytest
from avitoapi import PollBatch, PollingRunner
from avitoapi.events._base import Event
from avitoapi.events.lifecycle import PollError
from avitoapi.storage.memory import MemoryStorage


class _RecordingDispatcher:
    """Captures every event fed to it — stands in for the real Dispatcher."""

    def __init__(self) -> None:
        self.events: list[Event] = []

    async def feed_event(self, event: Event) -> bool:
        self.events.append(event)
        return True


class _FakePoller(PollingRunner):
    def __init__(self, dispatcher: object, storage: MemoryStorage, batches: list[PollBatch]) -> None:
        super().__init__(
            dispatcher,  # type: ignore[arg-type]  — duck-typed sink for the test
            account_id="acc1",
            poller="test",
            storage=storage,
            interval_s=0.01,
            backoff_initial_s=0.01,
            backoff_max_s=0.02,
        )
        self._batches = list(batches)
        self.seen_cursors: list[str | None] = []

    async def poll(self, cursor: str | None) -> PollBatch:
        self.seen_cursors.append(cursor)
        return self._batches.pop(0) if self._batches else PollBatch(events=[], cursor=cursor)


async def test_tick_emits_batch_and_persists_cursor() -> None:
    dp = _RecordingDispatcher()
    storage = MemoryStorage()
    e1, e2 = Event(), Event()
    poller = _FakePoller(dp, storage, [PollBatch(events=[e1, e2], cursor="c1")])

    emitted = await poller.tick()

    assert emitted == 2
    assert dp.events == [e1, e2]
    assert await storage.get(poller.cursor_key) == "c1"


async def test_tick_resumes_from_persisted_cursor() -> None:
    dp = _RecordingDispatcher()
    storage = MemoryStorage()
    await storage.put("feed:cursor:acc1:test", "saved")
    poller = _FakePoller(dp, storage, [PollBatch(events=[], cursor=None)])

    await poller.tick()

    assert poller.seen_cursors == ["saved"]  # loaded the persisted cursor, not None


async def test_start_runs_until_stop() -> None:
    dp = _RecordingDispatcher()
    poller = _FakePoller(dp, MemoryStorage(), [PollBatch(events=[Event()], cursor="c1")])

    task = asyncio.create_task(poller.start())
    await asyncio.sleep(0.05)
    await poller.stop()
    await asyncio.wait_for(task, timeout=1.0)

    assert len(dp.events) >= 1


@pytest.mark.filterwarnings("ignore::UserWarning")  # structlog dev exc-formatter warns under -W error
async def test_start_emits_pollerror_and_survives_a_failed_poll() -> None:
    dp = _RecordingDispatcher()

    class _Boom(PollingRunner):
        def __init__(self) -> None:
            super().__init__(dp, account_id="a", poller="boom", storage=MemoryStorage(), interval_s=0.01, backoff_initial_s=0.01, backoff_max_s=0.02)  # type: ignore[arg-type]
            self.calls = 0

        async def poll(self, cursor: str | None) -> PollBatch:
            self.calls += 1
            raise RuntimeError("nope")

    poller = _Boom()
    task = asyncio.create_task(poller.start())
    await asyncio.sleep(0.05)
    await poller.stop()
    await asyncio.wait_for(task, timeout=1.0)

    assert poller.calls >= 1  # kept trying, one failure didn't kill the loop
    assert any(isinstance(e, PollError) for e in dp.events)


def test_update_cadence_rejects_non_positive() -> None:
    poller = _FakePoller(_RecordingDispatcher(), MemoryStorage(), [])
    poller.update_cadence(2.0)
    with pytest.raises(ValueError, match="positive"):
        poller.update_cadence(0)


def test_construction_rejects_non_positive_intervals() -> None:
    class _P(PollingRunner):
        async def poll(self, cursor: str | None) -> PollBatch:
            return PollBatch()

    with pytest.raises(ValueError, match="positive"):
        _P(_RecordingDispatcher(), account_id="a", poller="p", storage=MemoryStorage(), interval_s=0)  # type: ignore[arg-type]

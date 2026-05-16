"""Unit tests for :class:`WebhookFastReturnMiddleware`."""
from __future__ import annotations

import asyncio
import time

from avitoapi.web.middlewares.fast_return import (
    WebhookFastReturnMiddleware,
    _FallbackTaskTracker,
)


async def test_schedule_returns_immediately():
    """``schedule(coro)`` must return without awaiting the coroutine."""
    fr = WebhookFastReturnMiddleware()
    done = asyncio.Event()

    async def slow() -> None:
        await asyncio.sleep(0.1)
        done.set()

    start = time.monotonic()
    task = fr.schedule(slow())
    elapsed = time.monotonic() - start
    assert elapsed < 0.05, f"schedule blocked for {elapsed:.3f}s"
    assert not done.is_set()
    await task
    assert done.is_set()


async def test_schedule_keeps_strong_ref():
    """Tasks must not be GC'd mid-flight even if caller drops the ref."""
    fr = WebhookFastReturnMiddleware()
    finished: list[int] = []

    async def work(i: int) -> None:
        await asyncio.sleep(0.01)
        finished.append(i)

    for i in range(10):
        fr.schedule(work(i))
    await asyncio.sleep(0.1)
    assert sorted(finished) == list(range(10))


async def test_fallback_tracker_shutdown_waits():
    tracker = _FallbackTaskTracker()
    done = asyncio.Event()

    async def slow() -> None:
        await asyncio.sleep(0.05)
        done.set()

    tracker.spawn(slow())
    await tracker.shutdown(timeout=1.0)
    assert done.is_set()


async def test_external_tracker_used_when_supplied():
    calls: list[object] = []

    class _Tracker:
        def spawn(self, coro):
            calls.append(coro)
            return asyncio.create_task(coro)

    fr = WebhookFastReturnMiddleware(task_tracker=_Tracker())

    async def noop():
        return None

    task = fr.schedule(noop())
    await task
    assert len(calls) == 1

"""``QueueScheduler`` — wake a callback when the next scheduled row is due.

The :class:`~avitoapi.queue.queue.EventQueue` already honours ``run_at``
inside :meth:`~avitoapi.queue.queue.EventQueue.lease`, so a scheduler is
only required when consumers don't poll on a tight interval. The
scheduler reads the next due timestamp from the queue's index and
sleeps until then, then invokes the supplied callback so the worker
pulls fresh rows.
"""

from __future__ import annotations

import asyncio
import contextlib
import time
from collections.abc import Awaitable, Callable
from datetime import timedelta
from typing import TYPE_CHECKING, Any

from ..logging import get_logger

if TYPE_CHECKING:
    from ..events._base import Event
    from .base import QueuedEvent
    from .queue import EventQueue

log = get_logger(__name__)


class QueueScheduler:
    """Background loop that fires ``on_due`` when scheduled rows become ready.

    Wake-up strategy: peek the queue's storage index for the smallest
    ``run_at`` in the future. ``asyncio.sleep`` until then (capped at
    ``max_sleep``). When the timer fires, call ``on_due()``. Consumers
    typically use ``on_due`` to nudge their :class:`QueueWorker` (a
    simple ``asyncio.Event.set()``).
    """

    def __init__(
        self,
        queue: EventQueue,
        on_due: Callable[[], Awaitable[None] | None],
        *,
        max_sleep: float = 30.0,
        idle_sleep: float = 5.0,
    ) -> None:
        self._queue = queue
        self._on_due = on_due
        self.max_sleep = max_sleep
        self.idle_sleep = idle_sleep
        self._task: asyncio.Task[None] | None = None
        self._wake = asyncio.Event()
        self._stopped = False

    async def start(self) -> None:
        """Start the background loop. Idempotent."""

        if self._task is not None and not self._task.done():
            return
        self._stopped = False
        self._task = asyncio.create_task(self._run(), name="queue-scheduler")

    async def stop(self) -> None:
        """Cancel the loop and await its completion."""

        self._stopped = True
        self._wake.set()
        task = self._task
        if task is not None and not task.done():
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError, Exception):  # noqa: BLE001 — shutdown silence
                await task
        self._task = None

    def notify(self) -> None:
        """Force the scheduler to re-evaluate immediately.

        Producers can call this after an :meth:`EventQueue.enqueue` with
        ``run_at`` set so the scheduler doesn't sleep through an
        early-due row.
        """

        self._wake.set()

    async def _run(self) -> None:
        while not self._stopped:
            sleep_for = await self._compute_sleep()
            self._wake.clear()
            with contextlib.suppress(TimeoutError):
                await asyncio.wait_for(self._wake.wait(), timeout=sleep_for)
            if self._stopped:
                return
            try:
                outcome = self._on_due()
                if asyncio.iscoroutine(outcome):
                    await outcome
            except Exception:  # noqa: BLE001 — callback errors must not kill the loop
                log.exception("queue.scheduler.callback_failed")

    async def _compute_sleep(self) -> float:
        """Look at the index, find the soonest ``run_at`` strictly in the future."""

        now = time.time()
        next_due: float | None = None
        # The scheduler peeks the queue's storage directly via its public
        # methods — no lock contention with active consumers.
        async for queued in self._queue.replay():
            if queued.run_at is None:
                continue
            if queued.run_at > now and (next_due is None or queued.run_at < next_due):
                next_due = queued.run_at
        if next_due is None:
            return min(self.idle_sleep, self.max_sleep)
        return max(0.0, min(self.max_sleep, next_due - now))


def in_seconds(td: timedelta | float | int) -> float:
    """Coerce a duration to seconds. Convenience for ``enqueue_later`` callers."""

    if isinstance(td, timedelta):
        return td.total_seconds()
    return float(td)


async def enqueue_later(
    queue: EventQueue,
    event: Event,
    *,
    delay: timedelta | float,
    metadata: dict[str, Any] | None = None,
    priority: int = 0,
) -> QueuedEvent:
    """Convenience wrapper around :meth:`EventQueue.enqueue` with relative delay."""

    return await queue.enqueue(
        event,
        metadata=metadata,
        run_at=time.time() + in_seconds(delay),
        priority=priority,
    )


__all__ = ["QueueScheduler", "enqueue_later", "in_seconds"]

"""``QueueWorker`` — concurrent consumer pool driving a dispatcher.

The worker continuously :meth:`leases <EventQueue.lease>` rows from the
queue and hands them to a callable (typically
``Dispatcher._dispatch_queued``). It honours an optional
``partition_by`` extractor so events with the same partition key run
serially while different keys run in parallel.

Lifecycle::

    worker = QueueWorker(queue, handler, concurrency=8)
    await worker.start()
    ...
    await worker.stop()
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

from ..logging import get_logger

if TYPE_CHECKING:
    from ..events._base import Event
    from .base import BaseEventQueue, QueuedEvent

log = get_logger(__name__)

WorkerHandler = Callable[["QueuedEvent"], Awaitable[bool]]
PartitionExtractor = Callable[["Event"], str | None]


class QueueWorker:
    """Pull rows from a queue and dispatch them via ``handler``.

    ``handler`` returns ``True`` to acknowledge (queue row gets ack'd),
    ``False`` to release the lease (row becomes available for the next
    consumer without bumping attempts). Any raised exception is caught,
    logged, and the lease is released — so the next attempt fires
    naturally.

    ``partition_by`` is consulted before handing the row to ``handler``.
    When set, the worker takes a per-partition :class:`asyncio.Lock`
    around the handler call so two events with the same key never run
    concurrently inside this process. Cross-process serialisation needs
    a distributed lock — out of scope.
    """

    def __init__(
        self,
        queue: BaseEventQueue,
        handler: WorkerHandler,
        *,
        concurrency: int = 1,
        poll_interval: float = 0.5,
        visibility_timeout: float | None = None,
        partition_by: PartitionExtractor | None = None,
        name: str = "queue-worker",
    ) -> None:
        if concurrency < 1:
            raise ValueError("concurrency must be ≥ 1")
        self._queue = queue
        self._handler = handler
        self._concurrency = concurrency
        self._poll_interval = poll_interval
        self._visibility_timeout = visibility_timeout
        self._partition_by = partition_by
        self._name = name
        self._tasks: list[asyncio.Task[None]] = []
        self._stopped = False
        self._partition_locks: dict[str, asyncio.Lock] = {}
        self._partition_lock_guard = asyncio.Lock()

    async def start(self) -> None:
        """Spawn ``concurrency`` worker coroutines. Idempotent."""

        if self._tasks:
            return
        self._stopped = False
        for i in range(self._concurrency):
            task = asyncio.create_task(self._run_loop(), name=f"{self._name}-{i}")
            self._tasks.append(task)
        log.info(
            "queue.worker.started",
            concurrency=self._concurrency,
            poll_interval=self._poll_interval,
        )

    async def stop(self, *, timeout: float = 30.0) -> None:  # noqa: ASYNC109 — wait budget, not deadline
        """Stop polling and await in-flight tasks. Idempotent."""

        self._stopped = True
        tasks, self._tasks = self._tasks, []
        if not tasks:
            return
        for task in tasks:
            task.cancel()
        await asyncio.wait(tasks, timeout=timeout)
        self._partition_locks.clear()
        log.info("queue.worker.stopped")

    async def _run_loop(self) -> None:
        while not self._stopped:
            try:
                queued = await self._queue.lease(
                    visibility_timeout=self._visibility_timeout,
                )
            except asyncio.CancelledError:
                return
            except Exception:  # noqa: BLE001 — never let one bad lease kill the worker
                log.exception("queue.worker.lease_failed")
                await self._sleep(self._poll_interval)
                continue

            if queued is None:
                await self._sleep(self._poll_interval)
                continue

            await self._process(queued)

    async def _sleep(self, seconds: float) -> None:
        try:
            await asyncio.sleep(seconds)
        except asyncio.CancelledError:
            raise

    async def _process(self, queued: QueuedEvent) -> None:
        lease = queued.lease
        lease_id = lease.lease_id if lease is not None else None
        partition_key = self._partition_by(queued.event) if self._partition_by else None

        async def _invoke() -> bool:
            try:
                return await self._handler(queued)
            except Exception:  # noqa: BLE001 — handler failure must not crash worker
                log.exception(
                    "queue.worker.handler_failed",
                    message_id=queued.message_id,
                    attempts=queued.attempts,
                )
                return False

        ok = False
        if partition_key is not None:
            lock = await self._get_partition_lock(partition_key)
            async with lock:
                ok = await _invoke()
        else:
            ok = await _invoke()

        if ok:
            await self._queue.ack(queued.message_id, lease_id=lease_id)
        elif lease_id is not None:
            await self._queue.release(queued.message_id, lease_id)

    async def _get_partition_lock(self, key: str) -> asyncio.Lock:
        # Locks accumulate over the worker's lifetime. Reset via stop()/start()
        # if you serve high-cardinality partition keys for a long time.
        async with self._partition_lock_guard:
            lock = self._partition_locks.get(key)
            if lock is None:
                lock = asyncio.Lock()
                self._partition_locks[key] = lock
            return lock

    @property
    def is_running(self) -> bool:
        return bool(self._tasks) and not self._stopped

    async def drain(self, *, timeout: float = 30.0) -> int:  # noqa: ASYNC109 — wait budget
        """Wait for the queue to empty (best-effort).

        Returns the remaining pending count when the wait budget expires.
        """

        deadline = time.time() + timeout
        while time.time() < deadline:
            pending = await self._queue.pending_count()
            if pending == 0:
                return 0
            await asyncio.sleep(0.1)
        return await self._queue.pending_count()


__all__ = ["PartitionExtractor", "QueueWorker", "WorkerHandler"]

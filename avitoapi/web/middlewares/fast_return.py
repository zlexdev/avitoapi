"""Spawn-and-return middleware — keeps the HTTP reply under Avito's 2s timeout.

Avito's webhook contract retries any delivery that isn't acknowledged with a
``200 OK`` inside 2 seconds. This middleware spawns the actual handler as a
background task so the response can return immediately.

Backed by an in-package task tracker that uses ``asyncio.create_task``
and a strong-ref set so tasks don't get GC'd mid-flight. Pass a custom
``task_tracker`` to override (any object with a ``spawn(coro)`` method).
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Coroutine
from typing import Any  # typed-Any: asyncio Task/Coroutine and middleware generics use Any

from ...routers.middleware import BaseMiddleware, NextHandler


class _FallbackTaskTracker:
    """Minimal task tracker — keeps strong refs so tasks aren't GC'd."""

    def __init__(self) -> None:
        self._tasks: set[asyncio.Task[Any]] = set()

    def spawn(self, coro: Coroutine[Any, Any, Any]) -> asyncio.Task[Any]:
        """Schedule ``coro`` and return the task. Reference held until done."""
        task = asyncio.create_task(coro)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task

    async def shutdown(self, timeout: float = 5.0) -> None:  # noqa: ASYNC109 — timeout is wait budget, not deadline
        """Wait for in-flight tasks. Idempotent."""
        if not self._tasks:
            return
        await asyncio.wait(self._tasks, timeout=timeout)


class WebhookFastReturnMiddleware(BaseMiddleware[Any, Any]):
    """Spawn the handler on the supplied task tracker; return immediately.

    ``task_tracker`` is duck-typed: anything with a ``spawn(coro)`` method
    (returning the spawned task) works. The default :class:`_FallbackTaskTracker`
    covers the common single-process case.
    """

    def __init__(self, task_tracker: Any | None = None) -> None:
        self._tracker = task_tracker or _FallbackTaskTracker()

    @property
    def tracker(self) -> Any:
        """The underlying tracker — exposed for shutdown coordination."""
        return self._tracker

    async def __call__(self, handler: NextHandler[Any, Any], event: Any, ctx: Any) -> Any:
        """Schedule handler as a background task; return 200 immediately."""
        self.schedule(handler(event, ctx))
        return (200, {"ok": True})

    def schedule(
        self,
        coro_or_awaitable: Coroutine[Any, Any, Any] | Awaitable[Any],
    ) -> asyncio.Task[Any]:
        """Hand off to the tracker. Returns the task; caller may ignore it."""
        if asyncio.iscoroutine(coro_or_awaitable):
            return self._tracker.spawn(coro_or_awaitable)

        # Awaitable that isn't a coroutine — wrap so the tracker sees a coroutine.
        async def _wrap() -> Any:
            return await coro_or_awaitable

        return self._tracker.spawn(_wrap())

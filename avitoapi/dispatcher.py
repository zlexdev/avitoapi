"""Multi-account ``Dispatcher`` — aiogram-style: inherits from :class:`Router`.

Sits alongside :class:`Client`, fanning out inbound events. Because
``Dispatcher`` itself is a :class:`Router`, every event observer
(``dispatcher.new_message``, ``dispatcher.order_created``, ...) is
attached directly on the dispatcher — handlers can register without an
intermediate router unless they want plugin-style isolation.

Owns the side-stores aiogram users expect: per-account :class:`Client`
registry, FSM storage, idempotency store, dead-letter queue. All
in-memory by default — pass real backends for multi-process deploys.
"""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from .events._base import Event
from .logging import get_logger
from .persistent_queue import BaseEventQueue, EventQueue, QueuedEvent
from .routers import CtxQueue, EventContext, Router
from .storage.memory import MemoryStorage

if TYPE_CHECKING:
    from .client import Client
    from .storage.base import BaseStorage

log = get_logger(__name__)


class InMemoryIdempotencyStore:
    """Tiny dedup store. Keys live in-process; reset on restart."""

    def __init__(self) -> None:
        self._seen: set[str] = set()
        self._lock = asyncio.Lock()

    async def seen(self, key: str) -> bool:
        async with self._lock:
            if key in self._seen:
                return True
            self._seen.add(key)
            return False

    async def forget(self, key: str) -> None:
        async with self._lock:
            self._seen.discard(key)


class InMemoryDeadLetterQueue:
    """Per-process DLQ. Stores ``(event, exception)`` pairs for inspection."""

    def __init__(self) -> None:
        self._items: list[tuple[Event, BaseException]] = []
        self._lock = asyncio.Lock()

    async def push(self, event: Event, exc: BaseException) -> None:
        async with self._lock:
            self._items.append((event, exc))

    async def pop_all(self) -> list[tuple[Event, BaseException]]:
        async with self._lock:
            out = list(self._items)
            self._items.clear()
            return out

    def __len__(self) -> int:
        return len(self._items)


class Dispatcher(Router):
    """SDK-wide aiogram-style Dispatcher — a :class:`Router` with event entry-points.

    Methods:

    * :meth:`feed_event` — persist the event, fan out through every router,
      and rely on the handler to call :meth:`EventContext.atomic_completed`.
    * :meth:`dispatch` — alias of :meth:`feed_event` for handlers that prefer that name.
    * :meth:`event_entry` — alias used by :class:`avitoapi.web.AvitoWebhookHandler`.
    * :meth:`propagate_event` — propagate against a context you already built.
    * :meth:`replay_pending` — drain unacked events from the queue at startup.

    Side-stores (``accounts``, ``fsm_storage``, ``idempotency_storage``,
    ``dlq``, ``web``, ``event_queue``) are plain attributes so callers can
    swap them at runtime.
    """

    def __init__(
        self,
        *,
        name: str = "dispatcher",
        event_queue: BaseEventQueue | None = None,
    ) -> None:
        super().__init__(name=name)
        self.accounts: dict[str, Client] = {}
        self.fsm_storage: BaseStorage[Any, str] | None = None
        self.idempotency_storage: InMemoryIdempotencyStore | Any = InMemoryIdempotencyStore()
        self.dlq: InMemoryDeadLetterQueue | Any = InMemoryDeadLetterQueue()
        self.web: Any = None
        self.event_queue: BaseEventQueue = event_queue or EventQueue(MemoryStorage())
        self._inflight: set[asyncio.Task[Any]] = set()

    async def feed_event(self, event: Event) -> bool:
        """Persist + propagate one event. Returns ``True`` if anything handled it.

        The event is enqueued before propagation. Handlers must call
        ``await ctx.atomic_completed()`` to drop the event from the queue;
        without that call the event is replayed by :meth:`replay_pending`
        on the next startup.
        """

        queued = await self.event_queue.enqueue(event)
        return await self._dispatch_queued(queued)

    async def dispatch(self, event: Event) -> bool:
        """Alias of :meth:`feed_event` — present so app code can read either name."""

        return await self.feed_event(event)

    async def event_entry(self, event: Event) -> bool:
        """Alias of :meth:`feed_event` — used by the webhook adapter."""

        return await self.feed_event(event)

    async def propagate_event(self, event: Event, ctx: EventContext | None = None) -> bool:
        """Run propagation against an existing :class:`EventContext` (or build one).

        Does NOT persist into the queue — use :meth:`feed_event` for that.
        Useful for tests and for re-firing an already-queued event.
        """

        if ctx is None:
            ctx = EventContext(event=event, dispatcher=self)
        return await self.propagate(event, ctx)

    async def replay_pending(self) -> int:
        """Re-deliver every queued event that was not acked before restart.

        Returns the number of events that were dispatched. Each replay
        increments ``QueuedEvent.attempts`` so handlers can back off on
        repeated retries.
        """

        replayed = 0
        async for queued in self.event_queue.replay():
            queued.attempts += 1
            log.info(
                "dispatcher.replay",
                message_id=queued.message_id,
                event_name=type(queued.event).__name__,
                attempts=queued.attempts,
            )
            await self._dispatch_queued(queued)
            replayed += 1
        return replayed

    async def _dispatch_queued(self, queued: QueuedEvent) -> bool:
        update_meta = getattr(self.event_queue, "update_metadata", None)
        ctx_queue = CtxQueue(
            message_id=queued.message_id,
            attempts=queued.attempts,
            queued_at=queued.enqueued_at,
            metadata=dict(queued.metadata),
            _ack=self.event_queue.ack,
            _update_metadata=update_meta,
        )
        ctx = EventContext(event=queued.event, dispatcher=self, queue=ctx_queue)
        try:
            return await self.propagate(queued.event, ctx)
        except Exception as exc:
            log.exception(
                "dispatcher.handler_failed",
                event=type(queued.event).__name__,
                message_id=queued.message_id,
            )
            await self.dlq.push(queued.event, exc)
            raise

    def spawn(self, coro: Awaitable[Any]) -> asyncio.Task[Any]:
        """Schedule a background task; keep a strong ref so it doesn't get GC'd mid-flight."""

        async def _wrap() -> Any:
            return await coro

        task = asyncio.create_task(_wrap())
        self._inflight.add(task)
        task.add_done_callback(self._inflight.discard)
        return task

    async def shutdown(self, *, timeout: float = 10.0) -> None:  # noqa: ASYNC109 — wait budget, not deadline
        """Await every in-flight background task. Idempotent."""

        if not self._inflight:
            return
        await asyncio.wait(self._inflight, timeout=timeout)
        self._inflight.clear()


def make_dispatcher(
    *,
    accounts: list[Client],
    fsm_storage: BaseStorage[Any, str] | None = None,
    idempotency_storage: Any | None = None,
    dlq: Any | None = None,
    web: Any | None = None,
    log_level: str = "INFO",
) -> Dispatcher:
    """Build a Dispatcher attached to the given :class:`Client` instances.

    Defaults match the in-process shape: in-memory FSM, in-memory idempotency
    store, in-memory DLQ. Pass real backends for multi-process deploys.
    """
    _ = log_level  # accepted for API compatibility — logging is configured via structlog at app entry
    dispatcher = Dispatcher()
    dispatcher.accounts = {acc.account_id or "_anon": acc for acc in accounts}
    if fsm_storage is not None:
        dispatcher.fsm_storage = fsm_storage
    if idempotency_storage is not None:
        dispatcher.idempotency_storage = idempotency_storage
    if dlq is not None:
        dispatcher.dlq = dlq
    if web is not None:
        dispatcher.web = web
    return dispatcher


# Public alias: ``avitoapi.HandlerCallable``-style for users who want to type the callback.
DispatcherCallback = Callable[[Event], Awaitable[Any]]


__all__ = [
    "Dispatcher",
    "DispatcherCallback",
    "InMemoryDeadLetterQueue",
    "InMemoryIdempotencyStore",
    "make_dispatcher",
]

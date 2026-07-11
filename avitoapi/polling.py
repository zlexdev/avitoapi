"""Polling feed — a pull-based event source for domains Avito does not push.

Avito ships real-time webhooks only for the messenger surface; every other domain
(orders, items, reviews, ...) has to be POLLED. A :class:`PollingRunner` drives one
such loop: fetch the next batch from a persisted cursor, emit each item as a typed
:class:`~avitoapi.events._base.Event` into the :class:`~avitoapi.dispatcher.Dispatcher`,
advance + persist the cursor, and back off on failure. It mirrors the ``start()`` /
``stop()`` lifecycle of :class:`~avitoapi.web.servers.BaseWebhookRunner`, so an app can
supervise pollers and webhook runners side by side::

    runners = [webhook_runner, OrdersPoller(dispatcher, client), ItemsPoller(dispatcher, client)]
    async with asyncio.TaskGroup() as tg:
        for r in runners:
            tg.create_task(r.start())

Subclass and implement :meth:`poll` — the only domain-specific step (fetch a page from
the cursor, map rows to events, return the advanced cursor). Everything else — the loop,
cursor persistence, backoff, ``PollError`` emission, graceful stop — is handled here::

    class OrdersPoller(PollingRunner):
        def __init__(self, dispatcher, client):
            super().__init__(dispatcher, account_id=client.account_id, poller="orders", storage=client.storage)
            self._client = client

        async def poll(self, cursor):
            page = await self._client(ListOrders(cursor=cursor))
            events = [OrderStatusChanged(order_id=o.id, status=o.status) for o in page.orders]
            return PollBatch(events=events, cursor=page.next_cursor)

Dedup is delegated: :meth:`poll` should only return rows *after* ``cursor``, and the
Dispatcher's idempotency store drops any event that still slips through twice.
"""

from __future__ import annotations

import asyncio
import contextlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import structlog

from .events.lifecycle import PollError

if TYPE_CHECKING:
    from .dispatcher import Dispatcher
    from .events._base import Event
    from .storage.base import BaseStorage

log = structlog.get_logger(__name__)

_DEFAULT_INTERVAL_S = 5.0
_DEFAULT_BACKOFF_INITIAL_S = 1.0
_DEFAULT_BACKOFF_MAX_S = 60.0


@dataclass(slots=True)
class PollBatch:
    """One poll cycle's result: events to emit + the cursor to resume from.

    ``cursor is None`` (the default) leaves the stored cursor untouched — return it
    only when there is no more to read, so the next cycle re-polls from the same point.
    """

    events: list[Event] = field(default_factory=list)
    cursor: str | None = None


class PollingRunner(ABC):
    """Abstract pull feed: loop + cursor persistence + backoff around a :meth:`poll` step.

    Args:
        dispatcher: the sink every polled event is fed into (``feed_event``).
        account_id: owning account — used in the cursor key and ``PollError``.
        poller: short name of this poller (``"orders"``) — cursor key + ``PollError``.
        storage: where the resume cursor is persisted (survives restarts).
        interval_s: delay between successful cycles.
        backoff_initial_s / backoff_max_s: exponential backoff bounds after a failed cycle.
    """

    def __init__(
        self,
        dispatcher: Dispatcher,
        *,
        account_id: str,
        poller: str,
        storage: BaseStorage[object, str],
        interval_s: float = _DEFAULT_INTERVAL_S,
        backoff_initial_s: float = _DEFAULT_BACKOFF_INITIAL_S,
        backoff_max_s: float = _DEFAULT_BACKOFF_MAX_S,
    ) -> None:
        if interval_s <= 0 or backoff_initial_s <= 0 or backoff_max_s <= 0:
            raise ValueError("polling intervals must be positive")
        self._dispatcher = dispatcher
        self._account_id = account_id
        self._poller = poller
        self._storage = storage
        self._interval = interval_s
        self._backoff_initial = backoff_initial_s
        self._backoff_max = backoff_max_s
        self._stop = asyncio.Event()

    @abstractmethod
    async def poll(self, cursor: str | None) -> PollBatch:
        """Fetch the next batch from ``cursor``; return the events + advanced cursor."""

    async def start(self) -> None:
        """Run the poll loop until :meth:`stop`. Mirrors ``BaseWebhookRunner.start()``."""

        cursor = await self._load_cursor()
        backoff = self._backoff_initial
        log.info("poller.start", poller=self._poller, account_id=self._account_id, cursor=cursor)
        while not self._stop.is_set():
            try:
                batch = await self.poll(cursor)
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001 — loop boundary: one failed poll must not kill the poller
                log.exception("poller.failed", poller=self._poller, account_id=self._account_id)
                await self._safe_emit(
                    PollError(account_id=self._account_id, occurred_at=datetime.now(UTC), poller=self._poller, reason=str(exc)),
                )
                await self._sleep(backoff)
                backoff = min(backoff * 2, self._backoff_max)
                continue
            for event in batch.events:
                await self._safe_emit(event)
            if batch.cursor is not None and batch.cursor != cursor:
                cursor = batch.cursor
                await self._save_cursor(cursor)
            backoff = self._backoff_initial
            await self._sleep(self._interval)
        log.info("poller.stopped", poller=self._poller, account_id=self._account_id)

    async def stop(self) -> None:
        """Signal the loop to finish the current cycle and return. Idempotent."""

        self._stop.set()

    @property
    def cursor_key(self) -> str:
        return f"feed:cursor:{self._account_id}:{self._poller}"

    async def _load_cursor(self) -> str | None:
        raw = await self._storage.get(self.cursor_key)
        return raw if isinstance(raw, str) else None

    async def _save_cursor(self, cursor: str) -> None:
        await self._storage.put(self.cursor_key, cursor)

    async def _safe_emit(self, event: Event) -> None:
        try:
            await self._dispatcher.feed_event(event)
        except Exception:  # noqa: BLE001 — the Dispatcher already DLQs handler failures; never stall the loop
            log.exception("poller.emit_failed", poller=self._poller, event=type(event).__name__)

    async def _sleep(self, seconds: float) -> None:
        """Sleep up to ``seconds``, waking early the moment :meth:`stop` is called."""

        with contextlib.suppress(TimeoutError):
            await asyncio.wait_for(self._stop.wait(), timeout=seconds)


__all__ = ["PollBatch", "PollingRunner"]

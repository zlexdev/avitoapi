"""``EventContext`` — per-event mutable bag passed to every handler."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..events._base import Event


@dataclass(slots=True)
class CtxQueue:
    """Persistent-queue handle exposed on :class:`EventContext`.

    Carries the queue-related state a handler may need:

    * ``message_id`` — id of the row in the persistent queue.
    * ``attempts`` — how many times this event has been (re)delivered.
    * ``queued_at`` — epoch seconds when the event was enqueued.
    * ``metadata`` — free-form persisted bag a handler can checkpoint into.

    :meth:`atomic_completed` calls the bound ack hook so the queue drops
    the row. If the handler exits without acking, the dispatcher will
    replay the event after restart.
    """

    message_id: str = ""
    attempts: int = 0
    queued_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    _ack: Callable[[str], Awaitable[bool]] | None = None
    _update_metadata: Callable[[str, dict[str, Any]], Awaitable[bool]] | None = None
    _acked: bool = False

    async def atomic_completed(self) -> bool:
        """Atomically mark the event done. Idempotent."""

        if self._acked or self._ack is None or not self.message_id:
            return False
        self._acked = True
        return await self._ack(self.message_id)

    async def persist_metadata(self) -> bool:
        """Flush the current :attr:`metadata` dict back to the queue row."""

        if self._update_metadata is None or not self.message_id:
            return False
        return await self._update_metadata(self.message_id, dict(self.metadata))

    @property
    def is_acked(self) -> bool:
        return self._acked

    @property
    def is_bound(self) -> bool:
        """``True`` when this context has an active queue row to ack."""

        return bool(self.message_id) and self._ack is not None


@dataclass(slots=True)
class EventContext:
    """State carried through one event's propagation.

    * ``event`` — the original event instance.
    * ``dispatcher`` — the dispatcher that fired this propagation (may be ``None`` in tests).
    * ``workflow_data`` — free-form bag handlers may read/write
      (e.g. ``ctx.workflow_data['fsm']`` or stash a parsed model).
    * ``handled`` — flips to ``True`` when at least one handler ran for this event.
    * ``queue`` — :class:`CtxQueue` exposing persistent-queue ack + checkpoint helpers.
    """

    event: Event
    dispatcher: Any = None
    workflow_data: dict[str, Any] = field(default_factory=dict)
    handled: bool = False
    queue: CtxQueue = field(default_factory=CtxQueue)
    _stopped: bool = False

    async def atomic_completed(self) -> bool:
        """Convenience shortcut to :meth:`CtxQueue.atomic_completed`."""

        return await self.queue.atomic_completed()

    def stop_propagation(self) -> None:
        """Halt the walk after the current handler — no further handlers or sub-routers run.

        Opt-in: broadcast (every matching handler fires) stays the default.
        Equivalent to raising :class:`~avitoapi.routers.errors.CancelPropagation`.
        """

        self._stopped = True

    @property
    def is_stopped(self) -> bool:
        return self._stopped


__all__ = ["CtxQueue", "EventContext"]

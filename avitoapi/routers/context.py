"""``EventContext`` — per-event mutable bag passed to every handler."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..events._base import Event


def _resolve_stage_name(stage: Any) -> str:
    """Coerce a stage handle (string / class / instance) to its registered name."""

    if isinstance(stage, str):
        return stage
    cls = stage if isinstance(stage, type) else type(stage)
    name = getattr(cls, "__stage_name__", "") or getattr(cls, "name", "")
    if isinstance(name, str) and name:
        return name
    raise ValueError(
        f"Cannot resolve stage name from {stage!r}: pass a string, a "
        "BaseStage subclass, or a BaseStage instance.",
    )


class HandlerType(StrEnum):
    """Origin of the current handler frame, exposed on :class:`EventContext`.

    * :attr:`HANDLER` — plain ``@router.observer`` registration.
    * :attr:`PIPELINE` — invocation came through a :class:`avitoapi.pipeline.Pipeline`.
    """

    HANDLER = "handler"
    PIPELINE = "pipeline"


@dataclass(slots=True)
class CtxQueue:
    """Persistent-queue handle exposed on :class:`EventContext`.

    Carries the queue-related state a handler may need:

    * ``message_id`` — id of the row in the persistent queue.
    * ``attempts`` — how many times this event has been (re)delivered.
    * ``queued_at`` — epoch seconds when the event was enqueued.
    * ``metadata`` — free-form persisted bag (pipeline checkpoints land here).

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
class CtxPipeline:
    """Pipeline namespace on :class:`EventContext`.

    Lives at ``ctx.pipeline`` so handlers can call::

        ctx.pipeline.skip(Charge)
        ctx.pipeline.skip_remaining()

    Outside an active pipeline run the fields are inert and the methods
    are no-ops from the runner's perspective.

    * ``current_pipeline`` — name of the pipeline currently running.
    * ``current_stage`` — name of the stage currently being executed.
    * ``skip(*stages)`` — mark stages as completed without running them.
    * ``skip_remaining()`` — short-circuit the rest of the pipeline.
    """

    current_pipeline: str = ""
    current_stage: str = ""
    _skip_stages: set[str] = field(default_factory=set)
    _skip_remaining: bool = False

    def skip(self, *stages: Any) -> None:
        """Skip stages identified by name (str), :class:`BaseStage` subclass, or instance."""

        for stage in stages:
            self._skip_stages.add(_resolve_stage_name(stage))

    def skip_remaining(self) -> None:
        """Skip every stage after the current one. Pipeline still auto-acks."""

        self._skip_remaining = True

    def clear_skip(self) -> None:
        """Drop pending skip flags. Called by the runner between pipelines."""

        self._skip_stages.clear()
        self._skip_remaining = False

    def is_skipped(self, stage_name: str) -> bool:
        return stage_name in self._skip_stages


@dataclass(slots=True)
class EventContext:
    """State carried through one event's propagation.

    * ``event`` — the original event instance.
    * ``dispatcher`` — the dispatcher that fired this propagation (may be ``None`` in tests).
    * ``workflow_data`` — free-form bag handlers may read/write
      (e.g. ``ctx.workflow_data['fsm']`` or stash a parsed model).
    * ``handled`` — flips to ``True`` when at least one handler ran for this event.
    * ``queue`` — :class:`CtxQueue` exposing persistent-queue ack + checkpoint helpers.
    * ``outputs`` — typed scratch space for declarative stage data flow.
      Stages that declare ``output="key"`` deposit their return value
      under ``ctx.outputs["key"]`` so downstream stages can consume it
      without rummaging through ``workflow_data``.
    """

    event: Event
    dispatcher: Any = None
    workflow_data: dict[str, Any] = field(default_factory=dict)
    handled: bool = False
    queue: CtxQueue = field(default_factory=CtxQueue)
    handler_type: HandlerType = HandlerType.HANDLER
    pipeline: CtxPipeline = field(default_factory=CtxPipeline)
    outputs: dict[str, Any] = field(default_factory=dict)

    async def atomic_completed(self) -> bool:
        """Convenience shortcut to :meth:`CtxQueue.atomic_completed`."""

        return await self.queue.atomic_completed()


__all__ = ["CtxPipeline", "CtxQueue", "EventContext", "HandlerType"]

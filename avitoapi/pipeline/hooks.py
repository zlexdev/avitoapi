"""Lifecycle hooks for :class:`~avitoapi.pipeline.pipeline.Pipeline`.

Each phase of a pipeline run fires an ordered chain of hooks attached
via :class:`PipelineHooks`. Hooks are async callables receiving
``(event, ctx)`` plus a phase-specific extra (e.g. the stage instance,
the raised exception). They MUST NOT raise — hook errors are logged
and swallowed so user observability code can't deadlock the runner.

Public surface is the decorator on :class:`~avitoapi.pipeline.pipeline.Pipeline`::

    pipeline = Pipeline("ship")

    @pipeline.before_run
    async def setup(event, ctx): ...

    @pipeline.on_failure
    async def alert(event, ctx, exc): ...

    @pipeline.on_compensate("charge")
    async def refund_metric(stage, event, ctx): ...
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ..logging import get_logger

if TYPE_CHECKING:
    from ..events._base import Event
    from ..routers.context import EventContext

log = get_logger(__name__)


RunHook = Callable[["Event", "EventContext"], Awaitable[None] | None]
FailureHook = Callable[["Event", "EventContext", BaseException], Awaitable[None] | None]
StageHook = Callable[[Any, "Event", "EventContext"], Awaitable[None] | None]
CompensateHook = Callable[[Any, "Event", "EventContext"], Awaitable[None] | None]


async def _safe_fire_run(
    hooks: list[RunHook],
    *,
    event: Event,
    ctx: EventContext,
    phase: str,
) -> None:
    for hook in hooks:
        try:
            outcome = hook(event, ctx)
            if asyncio.iscoroutine(outcome):
                await outcome
        except Exception:  # noqa: BLE001 — hook errors must not break the pipeline
            log.exception(
                "pipeline.hook_failed", phase=phase, hook=getattr(hook, "__name__", repr(hook))
            )


async def _safe_fire_failure(
    hooks: list[FailureHook],
    *,
    event: Event,
    ctx: EventContext,
    exc: BaseException,
) -> None:
    for hook in hooks:
        try:
            outcome = hook(event, ctx, exc)
            if asyncio.iscoroutine(outcome):
                await outcome
        except Exception:  # noqa: BLE001
            log.exception(
                "pipeline.hook_failed",
                phase="on_failure",
                hook=getattr(hook, "__name__", repr(hook)),
            )


async def _safe_fire_stage(
    hooks: list[StageHook],
    *,
    stage: Any,
    event: Event,
    ctx: EventContext,
    phase: str,
) -> None:
    for hook in hooks:
        try:
            outcome = hook(stage, event, ctx)
            if asyncio.iscoroutine(outcome):
                await outcome
        except Exception:  # noqa: BLE001
            log.exception(
                "pipeline.hook_failed", phase=phase, hook=getattr(hook, "__name__", repr(hook))
            )


@dataclass(slots=True)
class PipelineHooks:
    """Chains of lifecycle callbacks attached to a single pipeline.

    Pipelines instantiate this once at construction; decorators on
    :class:`Pipeline` append to the corresponding list. All chains
    fire in registration order. Failures are caught + logged.
    """

    before_run: list[RunHook] = field(default_factory=list)
    after_run: list[RunHook] = field(default_factory=list)
    on_failure: list[FailureHook] = field(default_factory=list)
    on_stage_start: list[StageHook] = field(default_factory=list)
    on_stage_complete: list[StageHook] = field(default_factory=list)
    on_stage_skipped: list[StageHook] = field(default_factory=list)
    on_stage_failed: list[StageHook] = field(default_factory=list)
    on_compensate_per_stage: dict[str, list[CompensateHook]] = field(default_factory=dict)
    on_compensate: list[CompensateHook] = field(default_factory=list)

    async def fire_before_run(self, event: Event, ctx: EventContext) -> None:
        await _safe_fire_run(self.before_run, event=event, ctx=ctx, phase="before_run")

    async def fire_after_run(self, event: Event, ctx: EventContext) -> None:
        await _safe_fire_run(self.after_run, event=event, ctx=ctx, phase="after_run")

    async def fire_on_failure(
        self,
        event: Event,
        ctx: EventContext,
        exc: BaseException,
    ) -> None:
        await _safe_fire_failure(self.on_failure, event=event, ctx=ctx, exc=exc)

    async def fire_on_stage_start(
        self,
        stage: Any,
        event: Event,
        ctx: EventContext,
    ) -> None:
        await _safe_fire_stage(
            self.on_stage_start,
            stage=stage,
            event=event,
            ctx=ctx,
            phase="on_stage_start",
        )

    async def fire_on_stage_complete(
        self,
        stage: Any,
        event: Event,
        ctx: EventContext,
    ) -> None:
        await _safe_fire_stage(
            self.on_stage_complete,
            stage=stage,
            event=event,
            ctx=ctx,
            phase="on_stage_complete",
        )

    async def fire_on_stage_skipped(
        self,
        stage: Any,
        event: Event,
        ctx: EventContext,
    ) -> None:
        await _safe_fire_stage(
            self.on_stage_skipped,
            stage=stage,
            event=event,
            ctx=ctx,
            phase="on_stage_skipped",
        )

    async def fire_on_stage_failed(
        self,
        stage: Any,
        event: Event,
        ctx: EventContext,
    ) -> None:
        await _safe_fire_stage(
            self.on_stage_failed,
            stage=stage,
            event=event,
            ctx=ctx,
            phase="on_stage_failed",
        )

    async def fire_on_compensate(
        self,
        stage: Any,
        event: Event,
        ctx: EventContext,
        *,
        stage_name: str,
    ) -> None:
        # Per-stage chain first, then global chain.
        per_stage = self.on_compensate_per_stage.get(stage_name, [])
        await _safe_fire_stage(
            list(per_stage),
            stage=stage,
            event=event,
            ctx=ctx,
            phase="on_compensate",
        )
        await _safe_fire_stage(
            list(self.on_compensate),
            stage=stage,
            event=event,
            ctx=ctx,
            phase="on_compensate",
        )


__all__ = [
    "CompensateHook",
    "FailureHook",
    "PipelineHooks",
    "RunHook",
    "StageHook",
]

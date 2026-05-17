"""``PipelineRunner`` — execute one pipeline against one event.

The runner is the working horse: it loads + persists checkpoints,
honours every :class:`Stage` option (retry / timeout / when / output /
compensate / depends_on), fires lifecycle hooks, and drives saga
rollback. The :class:`Pipeline` and :class:`Stage` types are pure
declarations.

Execution model:

1. Build execution layers from ``depends_on`` (topological sort). Each
   layer = stages whose deps are satisfied by previous layers.
2. For each layer, run member stages in parallel via
   :func:`asyncio.gather` (single-stage layers run inline — zero cost).
3. After each stage success, persist the checkpoint.
4. On any stage failure (after retries):

   * ``saga=False`` → raise :class:`PipelineStageError` with the
     original exception chained.
   * ``saga=True`` → walk ``checkpoint.completed`` in reverse, calling
     each stage's ``compensate_fn`` (best-effort; failed compensates
     are recorded but don't block siblings). Then raise.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from ..logging import get_logger
from .pipeline import (
    CheckpointState,
    CompensationFailed,
    Pipeline,
    PipelineCheckpoint,
    PipelineStageError,
    Stage,
)
from .retry import RetryPolicy

if TYPE_CHECKING:
    from ..events._base import Event
    from ..routers.context import EventContext
    from ..routers.middleware import MiddlewareChain

log = get_logger(__name__)


class PipelineRunner:
    """Drives one event through one pipeline with resumable checkpoints.

    Reads the existing checkpoint from ``ctx.queue.metadata``, skips
    every stage already completed (and any the handler marked via
    :meth:`CtxPipeline.skip`), runs the rest, persists the updated
    checkpoint after each stage so a restart picks up where the last
    successful stage left off. After the final stage the runner calls
    :meth:`EventContext.atomic_completed` so the persistent queue can
    drop the event row.

    ``middleware_chain`` wraps **each individual stage call** so
    router-level ``inner_middleware`` runs once per stage. Pass
    ``None`` to skip middleware wrapping — useful for direct unit
    tests of a runner.
    """

    def __init__(
        self,
        pipeline: Pipeline,
        *,
        middleware_chain: MiddlewareChain | None = None,
    ) -> None:
        self.pipeline = pipeline
        self.middleware_chain = middleware_chain

    async def run(self, event: Event, ctx: EventContext) -> bool:
        if not self.pipeline.applies(event):
            return False

        checkpoint = self._load_checkpoint(ctx)
        previous_pipeline = ctx.pipeline.current_pipeline
        previous_stage = ctx.pipeline.current_stage
        ctx.pipeline.clear_skip()
        ctx.pipeline.current_pipeline = self.pipeline.name
        layers = self._build_layers()

        try:
            await self.pipeline.hooks.fire_before_run(event, ctx)
            if checkpoint.state is CheckpointState.COMPENSATING:
                # Restart hit during a compensation walk — resume rollback.
                await self._compensate(event, ctx, checkpoint, original_exc=None)
                checkpoint.state = CheckpointState.COMPENSATED
                await self._persist_checkpoint(ctx, checkpoint)
                return True

            for layer in layers:
                if ctx.pipeline._skip_remaining:
                    for stage in layer:
                        checkpoint.mark(stage.name)
                        await self._persist_checkpoint(ctx, checkpoint)
                    continue
                await self._run_layer(layer, event, ctx, checkpoint)

            checkpoint.state = CheckpointState.DONE
            await self._persist_checkpoint(ctx, checkpoint)
            await self.pipeline.hooks.fire_after_run(event, ctx)
        except PipelineStageError as exc:
            await self.pipeline.hooks.fire_on_failure(event, ctx, exc.__cause__ or exc)
            if self.pipeline.saga:
                checkpoint.state = CheckpointState.COMPENSATING
                await self._persist_checkpoint(ctx, checkpoint)
                await self._compensate(event, ctx, checkpoint, original_exc=exc)
                checkpoint.state = CheckpointState.COMPENSATED
                await self._persist_checkpoint(ctx, checkpoint)
            else:
                checkpoint.state = CheckpointState.FAILED
                await self._persist_checkpoint(ctx, checkpoint)
            raise
        finally:
            ctx.pipeline.clear_skip()
            ctx.pipeline.current_pipeline = previous_pipeline
            ctx.pipeline.current_stage = previous_stage

        if self.pipeline.auto_ack and not ctx.queue.is_acked:
            await ctx.atomic_completed()
        return True

    async def _run_layer(
        self,
        layer: list[Stage],
        event: Event,
        ctx: EventContext,
        checkpoint: PipelineCheckpoint,
    ) -> None:
        runnables: list[Stage] = []
        for stage in layer:
            if checkpoint.is_done(stage.name) or ctx.pipeline.is_skipped(stage.name):
                if ctx.pipeline.is_skipped(stage.name) and not checkpoint.is_done(stage.name):
                    checkpoint.mark(stage.name)
                    await self._persist_checkpoint(ctx, checkpoint)
                    await self.pipeline.hooks.fire_on_stage_skipped(stage, event, ctx)
                continue
            if stage.when is not None:
                try:
                    matched = bool(stage.when(event))
                except Exception:  # noqa: BLE001 — predicate guard, never propagate
                    matched = False
                if not matched:
                    checkpoint.mark(stage.name)
                    await self._persist_checkpoint(ctx, checkpoint)
                    await self.pipeline.hooks.fire_on_stage_skipped(stage, event, ctx)
                    continue
            runnables.append(stage)

        if not runnables:
            return

        if len(runnables) == 1:
            stage = runnables[0]
            await self._execute_stage(stage, event, ctx, checkpoint)
            return

        # Multi-stage layer — run concurrently.
        await asyncio.gather(
            *(self._execute_stage(s, event, ctx, checkpoint) for s in runnables),
            return_exceptions=False,
        )

    async def _execute_stage(
        self,
        stage: Stage,
        event: Event,
        ctx: EventContext,
        checkpoint: PipelineCheckpoint,
    ) -> None:
        ctx.pipeline.current_stage = stage.name
        await self.pipeline.hooks.fire_on_stage_start(stage, event, ctx)
        started = time.monotonic()
        try:
            result = await self._invoke_with_policy(stage, event, ctx)
        except Exception as exc:
            duration_ms = (time.monotonic() - started) * 1000
            log.error(
                "pipeline.stage_failed",
                pipeline_name=self.pipeline.name,
                stage_name=stage.name,
                error=f"{type(exc).__name__}: {exc}",
                duration_ms=round(duration_ms, 2),
            )
            await self.pipeline.hooks.fire_on_stage_failed(stage, event, ctx)
            raise PipelineStageError(
                f"{self.pipeline.name}.{stage.name} failed: {exc}",
            ) from exc

        if stage.output is not None:
            ctx.outputs[stage.output] = result
        checkpoint.mark(stage.name)
        await self._persist_checkpoint(ctx, checkpoint)
        duration_ms = (time.monotonic() - started) * 1000
        log.info(
            "pipeline.stage_completed",
            pipeline_name=self.pipeline.name,
            stage_name=stage.name,
            duration_ms=round(duration_ms, 2),
        )
        await self.pipeline.hooks.fire_on_stage_complete(stage, event, ctx)

    async def _invoke_with_policy(
        self,
        stage: Stage,
        event: Event,
        ctx: EventContext,
    ) -> Any:
        policy: RetryPolicy | None = stage.retry
        attempt = 0
        while True:
            attempt += 1
            try:
                return await self._invoke_once(stage, event, ctx)
            except Exception as exc:
                if policy is None or not policy.should_retry(exc, attempt=attempt):
                    raise
                delay = policy.backoff.delay(attempt)
                log.warning(
                    "pipeline.stage_retry",
                    pipeline_name=self.pipeline.name,
                    stage_name=stage.name,
                    attempt=attempt,
                    max_attempts=policy.max_attempts,
                    delay_s=round(delay, 3),
                    error=f"{type(exc).__name__}: {exc}",
                )
                if delay > 0:
                    await asyncio.sleep(delay)

    async def _invoke_once(
        self,
        stage: Stage,
        event: Event,
        ctx: EventContext,
    ) -> Any:
        async def _terminal(_ev: Event, _ctx: EventContext) -> Any:
            if stage.timeout is not None:
                return await asyncio.wait_for(stage.fn(_ev, _ctx), timeout=stage.timeout)
            return await stage.fn(_ev, _ctx)

        handler = (
            self.middleware_chain.wrap(_terminal)
            if self.middleware_chain is not None
            else _terminal
        )
        return await handler(event, ctx)

    async def _compensate(
        self,
        event: Event,
        ctx: EventContext,
        checkpoint: PipelineCheckpoint,
        *,
        original_exc: BaseException | None,
    ) -> None:
        for stage_name in reversed(list(checkpoint.completed)):
            if checkpoint.is_compensated(stage_name):
                continue
            stage = self.pipeline.get_stage(stage_name)
            if stage is None or stage.compensate_fn is None:
                # No compensator declared — leave the stage out of the
                # compensated list (the test inspecting `compensated`
                # expects only stages that actually rolled back).
                continue

            await self.pipeline.hooks.fire_on_compensate(
                stage,
                event,
                ctx,
                stage_name=stage_name,
            )
            try:
                await stage.compensate_fn(event, ctx)
            except Exception as exc:  # noqa: BLE001 — record + continue per Saga contract
                checkpoint.compensation_errors[stage_name] = f"{type(exc).__name__}: {exc}"
                await self._persist_checkpoint(ctx, checkpoint)
                log.error(
                    "pipeline.compensate_failed",
                    pipeline_name=self.pipeline.name,
                    stage_name=stage_name,
                    error=f"{type(exc).__name__}: {exc}",
                    original_error=(
                        f"{type(original_exc).__name__}: {original_exc}"
                        if original_exc is not None
                        else None
                    ),
                )
                # Best-effort: keep walking. The CompensationFailed
                # symbol is kept in the public surface so ops tooling
                # can pattern-match on it.
                _ = CompensationFailed(
                    f"{self.pipeline.name}.{stage_name} compensate failed: {exc}",
                )
                continue
            checkpoint.mark_compensated(stage_name)
            await self._persist_checkpoint(ctx, checkpoint)

    def _build_layers(self) -> list[list[Stage]]:
        """Group stages by dependency depth.

        Stages with explicit ``depends_on`` form the DAG layout. Stages
        WITHOUT explicit deps implicitly depend on the previous stage
        in registration order — this preserves the sequential semantics
        callers expect from a plain pipeline. Cycles raise ``ValueError``
        — better fail loud than mute-deadlock.
        """

        by_name: dict[str, Stage] = {s.name: s for s in self.pipeline.stages}

        # Validate deps point to known stages.
        for stage in self.pipeline.stages:
            for dep in stage.depends_on:
                if dep not in by_name:
                    raise ValueError(
                        f"stage {stage.name!r} depends on unknown stage {dep!r}",
                    )

        # Resolve implicit "after previous" deps for stages with depends_on=().
        effective_deps: dict[str, tuple[str, ...]] = {}
        previous: str | None = None
        for stage in self.pipeline.stages:
            if stage.depends_on:
                effective_deps[stage.name] = stage.depends_on
            elif previous is not None:
                effective_deps[stage.name] = (previous,)
            else:
                effective_deps[stage.name] = ()
            previous = stage.name

        remaining = {s.name for s in self.pipeline.stages}
        depth_of: dict[str, int] = {}
        progressed = True
        while remaining and progressed:
            progressed = False
            for name in list(remaining):
                deps = effective_deps[name]
                if all(dep in depth_of for dep in deps):
                    depth_of[name] = max((depth_of[d] for d in deps), default=-1) + 1
                    remaining.remove(name)
                    progressed = True
        if remaining:
            raise ValueError(
                f"pipeline {self.pipeline.name!r} has a dependency cycle among: {remaining}",
            )

        # Group by depth, preserving original registration order inside a layer.
        max_depth = max(depth_of.values(), default=-1)
        layers: list[list[Stage]] = [[] for _ in range(max_depth + 1)]
        for stage in self.pipeline.stages:
            layers[depth_of[stage.name]].append(stage)
        return layers

    def _checkpoint_key(self) -> str:
        return f"pipeline:{self.pipeline.name}"

    def _load_checkpoint(self, ctx: EventContext) -> PipelineCheckpoint:
        raw = ctx.queue.metadata.get(self._checkpoint_key())
        if isinstance(raw, PipelineCheckpoint):
            return raw
        if isinstance(raw, dict):
            return PipelineCheckpoint.from_dict(raw, self.pipeline.name)
        return PipelineCheckpoint(pipeline=self.pipeline.name)

    async def _persist_checkpoint(
        self,
        ctx: EventContext,
        checkpoint: PipelineCheckpoint,
    ) -> None:
        ctx.queue.metadata[self._checkpoint_key()] = checkpoint.to_dict()
        await ctx.queue.persist_metadata()


def stages_in_layers(stages: Iterable[Stage]) -> list[list[Stage]]:
    """Public helper that mirrors :meth:`PipelineRunner._build_layers` semantics.

    Useful for tests / docs that want to inspect the layering without
    instantiating a runner.
    """

    pipeline = Pipeline(name="__inspect__")
    for s in stages:
        pipeline.stages.append(s)
    return PipelineRunner(pipeline)._build_layers()


__all__ = ["PipelineRunner", "stages_in_layers"]

"""Multi-stage pipeline handlers with resumable execution + saga rollback.

The mechanics live in :mod:`stagecraft` (framework-agnostic library);
this module is a thin avitoapi shim that:

* re-exports the stagecraft public surface so existing imports
  (``from avitoapi import Pipeline, Stage, …`` etc.) keep working;
* wraps :class:`stagecraft.PipelineRunner` /
  :class:`stagecraft.PipelineRouter` with avitoapi-specific adapters
  so the engine reads/writes :class:`EventContext` correctly;
* accepts ``auto_ack`` as a back-compat alias for stagecraft's
  ``auto_complete``.

A pipeline = ordered list of :class:`Stage`s with optional dependency
arrows (:class:`Stage.depends_on`) forming a DAG. The runner walks
layers; stages on the same layer (no mutual deps) run in parallel.
After each stage returns, its name is checkpointed into the persistent
queue's metadata. On replay, the runner skips every stage already in
the checkpoint and resumes from the next one.

When ``Pipeline(saga=True)``, a stage failure triggers reverse-order
compensation through every completed stage that defines a
``compensate`` method (or ``compensate_fn``). The pipeline's
:class:`PipelineHooks` fire at every phase boundary.

Two registration shapes:

* class-based — subclass :class:`BaseStage` (with class-level options
  ``retry``, ``timeout``, ``when``, ``output``, ``depends_on``).
* decorator-based — ``@pipeline.stage("name", retry=..., timeout=...)``.

Atomic ack happens once the last stage finishes — the avitoapi
completion hook calls :meth:`EventContext.atomic_completed` for you,
so the rest of the event queue contract still holds.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from stagecraft import (
    Backoff,
    BaseStage,
    CheckpointState,
    CompensateHook,
    CompensationFailed,
    ConstantBackoff,
    ExponentialBackoff,
    FailureHook,
    ParallelGroup,
    PartitionFn,
)
from stagecraft import Pipeline as _SCPipeline
from stagecraft import (
    PipelineCheckpoint,
    PipelineHooks,
    PipelineStageError,
    RetryPolicy,
    RunHook,
    Stage,
    StageFn,
    StageHook,
    pipeline_stage,
    stage_name_of,
)

from .router import PipelineRouter
from .runner import PipelineRunner, stages_in_layers

if TYPE_CHECKING:
    from ..events._base import Event
    from ..routers.observer import Filter


def Pipeline(  # noqa: N802 — preserves pre-lift-out class-shaped name
    name: str,
    *,
    event_filter: "Filter | None" = None,
    stages: "list[Stage] | None" = None,
    auto_ack: bool = True,
    auto_complete: bool | None = None,
    saga: bool = False,
    partition_by: "PartitionFn[Event] | None" = None,
    hooks: PipelineHooks | None = None,
) -> _SCPipeline:
    """Construct a :class:`stagecraft.Pipeline` with avitoapi defaults.

    Accepts ``auto_ack`` as a back-compat alias for stagecraft's
    ``auto_complete`` field. Other kwargs forward 1:1.
    """

    return _SCPipeline(
        name=name,
        event_filter=event_filter,
        stages=list(stages) if stages else [],
        auto_complete=auto_complete if auto_complete is not None else auto_ack,
        saga=saga,
        partition_by=partition_by,
        hooks=hooks if hooks is not None else PipelineHooks(),
    )


__all__ = [
    "Backoff",
    "BaseStage",
    "CheckpointState",
    "CompensateHook",
    "CompensationFailed",
    "ConstantBackoff",
    "ExponentialBackoff",
    "FailureHook",
    "ParallelGroup",
    "PartitionFn",
    "Pipeline",
    "PipelineCheckpoint",
    "PipelineHooks",
    "PipelineRouter",
    "PipelineRunner",
    "PipelineStageError",
    "RetryPolicy",
    "RunHook",
    "Stage",
    "StageFn",
    "StageHook",
    "pipeline_stage",
    "stage_name_of",
    "stages_in_layers",
]

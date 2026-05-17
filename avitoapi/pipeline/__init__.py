"""Multi-stage pipeline handlers with resumable execution + saga rollback.

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

Atomic ack happens once the last stage finishes —
:class:`PipelineRunner` calls :meth:`EventContext.atomic_completed` for
you, so the rest of the event queue contract still holds.
"""

from __future__ import annotations

from .groups import ParallelGroup
from .hooks import (
    CompensateHook,
    FailureHook,
    PipelineHooks,
    RunHook,
    StageHook,
)
from .pipeline import (
    BaseStage,
    CheckpointState,
    CompensationFailed,
    PartitionFn,
    Pipeline,
    PipelineCheckpoint,
    PipelineStageError,
    Stage,
    StageFn,
    pipeline_stage,
    stage_name_of,
)
from .retry import Backoff, ConstantBackoff, ExponentialBackoff, RetryPolicy
from .router import PipelineRouter
from .runner import PipelineRunner, stages_in_layers

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

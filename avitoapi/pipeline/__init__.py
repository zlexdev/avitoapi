"""Multi-stage pipeline handlers with resumable execution.

A pipeline = ordered list of :class:`Stage` callables. Each stage runs
inside the dispatcher; after a stage returns, its name is checkpointed
into the persistent queue's metadata. On replay, the dispatcher skips
every stage already in the checkpoint and resumes from the next one.

Two registration shapes:

* class-based — :class:`Pipeline` instances accumulated under a
  :class:`PipelineRouter` (event filter + decorator chain).
* decorator-based — ``@pipeline.stage("name")`` chained on a single
  pipeline definition.

Atomic ack happens once the last stage finishes — :class:`PipelineRunner`
calls :meth:`EventContext.atomic_completed` for you, so the rest of the
event queue contract still holds.
"""
from __future__ import annotations

from .pipeline import (
    BaseStage,
    Pipeline,
    PipelineCheckpoint,
    PipelineRouter,
    PipelineRunner,
    PipelineStageError,
    Stage,
    pipeline_stage,
    stage_name_of,
)

__all__ = [
    "BaseStage",
    "Pipeline",
    "PipelineCheckpoint",
    "PipelineRouter",
    "PipelineRunner",
    "PipelineStageError",
    "Stage",
    "pipeline_stage",
    "stage_name_of",
]

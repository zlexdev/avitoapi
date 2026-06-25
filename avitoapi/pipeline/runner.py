"""Avitoapi-flavoured :class:`PipelineRunner`.

Thin wrapper around :class:`stagecraft.PipelineRunner` that auto-wires
the three avitoapi adapters (checkpoint store / state provider /
completion hook) at run-time so callers don't need to know they
exist. Constructor signature stays the same as before the lift-out:

    PipelineRunner(pipeline, *, middleware_chain=None)
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from stagecraft import PipelineRunner as _SCPipelineRunner
from stagecraft import RunOutcome

from ._adapters import (
    AvitoapiStateProvider,
    MiddlewareChainAdapter,
    QueueMetadataCheckpointStore,
    completion_hook,
)

if TYPE_CHECKING:
    from stagecraft import Pipeline, Stage

    from ..events._base import Event
    from ..routers.context import EventContext
    from ..routers.middleware import MiddlewareChain


class PipelineRunner:
    """Drives one event through one pipeline with resumable checkpoints.

    See :mod:`stagecraft.runner.PipelineRunner` for execution model
    details. This wrapper plugs in the avitoapi-specific adapters so
    callers can still write::

        runner = PipelineRunner(pipeline)
        await runner.run(event, ctx)

    Pass ``middleware_chain`` to wrap each stage call in the
    dispatcher's ``inner_middleware`` chain.
    """

    __slots__ = ("middleware_chain", "pipeline")

    def __init__(
        self,
        pipeline: Pipeline[Event, EventContext],
        *,
        middleware_chain: MiddlewareChain[Any, Any] | None = None,
    ) -> None:
        self.pipeline = pipeline
        self.middleware_chain = middleware_chain

    async def run(self, event: Event, ctx: EventContext) -> RunOutcome:
        inner: _SCPipelineRunner[Event, EventContext] = _SCPipelineRunner(
            self.pipeline,
            checkpoint_store=QueueMetadataCheckpointStore(ctx),
            state_provider=AvitoapiStateProvider(),
            completion_hook=completion_hook,
            middleware=(
                MiddlewareChainAdapter(self.middleware_chain)
                if self.middleware_chain is not None
                else None
            ),
        )
        return await inner.run(event, ctx)


def stages_in_layers(
    stages: Iterable[Stage[Any, Any, Any]],  # typed-Any: stagecraft Stage generic boundary — lib's own signature uses Any here
) -> list[list[Stage[Any, Any, Any]]]:  # typed-Any: stagecraft Stage generic boundary
    """Re-export of :func:`stagecraft.stages_in_layers`.

    Kept as a local symbol so the public ``from avitoapi import …``
    surface stays unchanged.
    """

    from stagecraft import stages_in_layers as _impl

    return _impl(stages)


__all__ = ["PipelineRunner", "stages_in_layers"]

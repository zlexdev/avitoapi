"""``PipelineRouter`` — aiogram-style decorator surface for many pipelines.

Attach to a :class:`Dispatcher` via :meth:`bind` — every event the
dispatcher fans out is also evaluated against every registered
pipeline. A pipeline whose :attr:`Pipeline.event_filter` matches the
event fires; pipelines whose filter does not match are skipped.

Thin wrapper over :class:`stagecraft.PipelineRouter`: same decorator
surface, plus :meth:`bind` for avitoapi's outer-middleware contract.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from stagecraft import PipelineRouter as _SCPipelineRouter

from ..events._base import Event
from ..routers.context import EventContext
from ..routers.middleware import BaseMiddleware
from ._adapters import (
    AvitoapiStateProvider,
    MiddlewareChainAdapter,
    QueueMetadataCheckpointStore,
    completion_hook,
)

if TYPE_CHECKING:
    from stagecraft import Pipeline, StageFn
    from stagecraft import PipelineRunner as _SCPipelineRunner

    from ..dispatcher import Dispatcher
    from ..routers.observer import Filter


class PipelineRouter(_SCPipelineRouter[Event, EventContext]):
    """Collection of named :class:`Pipeline`s mounted on a Dispatcher.

    Example::

        router = PipelineRouter()

        @router.stage("ship-order", "validate")
        async def validate(event, ctx): ...

        @router.stage("ship-order", "charge")
        async def charge(event, ctx): ...

        router.bind(dispatcher)
    """

    def pipeline(  # noqa: D102  # back-compat: accept auto_ack alias
        self,
        name: str,
        *,
        event_filter: Filter | None = None,
        auto_ack: bool = True,
        auto_complete: bool | None = None,
        saga: bool = False,
    ) -> Pipeline[Event, EventContext]:
        return super().pipeline(
            name,
            event_filter=event_filter,
            auto_complete=auto_complete if auto_complete is not None else auto_ack,
            saga=saga,
        )

    def stage(
        self,
        pipeline_name: str,
        stage_name: str,
    ) -> Callable[[StageFn[Event, EventContext, Any]], StageFn[Event, EventContext, Any]]:  # typed-Any: stagecraft ResultT boundary — parent signature uses Any here
        return self.pipeline(pipeline_name).stage(stage_name)

    def bind(self, dispatcher: Dispatcher) -> None:
        """Subscribe to a dispatcher — every event runs through every matching pipeline.

        Pipelines fire AFTER the standard observer chain (so plain
        ``@router.observer`` handlers run first). Each individual stage
        is wrapped in the dispatcher's ``inner_middleware`` chain so
        middlewares run once per stage, not once per pipeline.
        ``ctx.handler_type`` flips to :attr:`HandlerType.PIPELINE` while a
        pipeline runs and restores to its previous value afterwards.
        """

        from ..routers.context import HandlerType  # noqa: PLC0415 — break cycle

        router = self

        class _PipelineMiddleware(BaseMiddleware[EventContext, bool]):
            async def __call__(
                self,
                handler: Callable[[Event, EventContext], Awaitable[bool]],
                event: Event,
                ctx: EventContext,
            ) -> bool:
                result = await handler(event, ctx)
                stage_middleware = (
                    MiddlewareChainAdapter(dispatcher.inner_middleware)
                    if dispatcher.inner_middleware is not None
                    else None
                )
                for pipeline in router.pipelines:
                    if not pipeline.applies(event):
                        continue
                    runner = _build_per_ctx_runner(
                        pipeline,
                        ctx,
                        stage_middleware=stage_middleware,
                    )
                    previous = ctx.handler_type
                    ctx.handler_type = HandlerType.PIPELINE
                    try:
                        await runner.run(event, ctx)
                    finally:
                        ctx.handler_type = previous
                return result

        dispatcher.outer_middleware.register(_PipelineMiddleware())


def _build_per_ctx_runner(
    pipeline: Pipeline[Event, EventContext],
    ctx: EventContext,
    *,
    stage_middleware: MiddlewareChainAdapter | None,
) -> _SCPipelineRunner[Event, EventContext]:
    """Construct a stagecraft.PipelineRunner bound to one ``ctx``."""

    from stagecraft import PipelineRunner as _SCPipelineRunner  # noqa: PLC0415

    return _SCPipelineRunner(
        pipeline,
        checkpoint_store=QueueMetadataCheckpointStore(ctx),
        state_provider=AvitoapiStateProvider(),
        completion_hook=completion_hook,
        middleware=stage_middleware,
    )


__all__ = ["PipelineRouter"]

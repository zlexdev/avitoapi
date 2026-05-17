"""``PipelineRouter`` — aiogram-style decorator surface for many pipelines.

Attach to a :class:`Dispatcher` via :meth:`bind` — every event the
dispatcher fans out is also evaluated against every registered
pipeline. A pipeline whose :attr:`Pipeline.event_filter` matches the
event fires; pipelines whose filter does not match are skipped.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING, Any

from .pipeline import Pipeline, StageFn
from .runner import PipelineRunner

if TYPE_CHECKING:
    from ..routers.observer import Filter


class PipelineRouter:
    """Collection of named :class:`Pipeline`s mounted on a Dispatcher.

    Example::

        router = PipelineRouter()

        @router.stage("ship-order", "validate")
        async def validate(event, ctx): ...

        @router.stage("ship-order", "charge")
        async def charge(event, ctx): ...
    """

    def __init__(self) -> None:
        self._pipelines: dict[str, Pipeline] = {}

    @property
    def pipelines(self) -> Iterable[Pipeline]:
        return self._pipelines.values()

    def pipeline(
        self,
        name: str,
        *,
        event_filter: Filter | None = None,
        auto_ack: bool = True,
        saga: bool = False,
    ) -> Pipeline:
        """Get-or-create a pipeline by name."""

        existing = self._pipelines.get(name)
        if existing is not None:
            return existing
        new = Pipeline(name=name, event_filter=event_filter, auto_ack=auto_ack, saga=saga)
        self._pipelines[name] = new
        return new

    def stage(self, pipeline_name: str, stage_name: str) -> Callable[[StageFn], StageFn]:
        """Decorator scoped by ``pipeline_name`` — creates the pipeline lazily."""

        pipeline = self.pipeline(pipeline_name)
        return pipeline.stage(stage_name)

    def bind(self, dispatcher: Any) -> None:
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

        class _PipelineMiddleware:
            async def __call__(
                self,
                handler: Callable[..., Any],
                event: Any,
                ctx: Any,
            ) -> Any:
                result = await handler(event, ctx)
                for pipeline in router.pipelines:
                    if not pipeline.applies(event):
                        continue
                    runner = PipelineRunner(
                        pipeline,
                        middleware_chain=dispatcher.inner_middleware,
                    )
                    previous = ctx.handler_type
                    ctx.handler_type = HandlerType.PIPELINE
                    try:
                        await runner.run(event, ctx)
                    finally:
                        ctx.handler_type = previous
                return result

        dispatcher.outer_middleware.register(_PipelineMiddleware())


__all__ = ["PipelineRouter"]

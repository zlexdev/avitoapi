"""Pipeline core — :class:`Stage`, :class:`Pipeline`, :class:`PipelineRunner`."""
from __future__ import annotations

import re
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar

from ..exceptions import SDKError
from ..logging import get_logger

if TYPE_CHECKING:
    from ..events._base import Event
    from ..routers.context import EventContext
    from ..routers.middleware import MiddlewareChain
    from ..routers.observer import Filter

log = get_logger(__name__)


StageFn = Callable[["Event", "EventContext"], Awaitable[Any]]
StageLike = "str | type[BaseStage] | BaseStage"


def _to_kebab(class_name: str) -> str:
    """``MyStageClass`` → ``my-stage-class``. Handles all-caps initials reasonably."""

    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1-\2", class_name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", s1).lower()


def stage_name_of(stage: StageLike) -> str:
    """Resolve any stage handle (string / class / instance) to the registered name."""

    if isinstance(stage, str):
        return stage
    cls = stage if isinstance(stage, type) else type(stage)
    name = getattr(cls, "__stage_name__", "")
    if not name:
        raise ValueError(
            f"{cls.__name__} is not a BaseStage subclass — pass a stage class, "
            "instance, or the registered stage name as a string.",
        )
    return name


class PipelineStageError(SDKError):
    """A stage callable raised. The pipeline aborts; queue keeps the event."""

    default_message = "Pipeline stage failed"


@dataclass(slots=True)
class Stage:
    """One named step inside a :class:`Pipeline`.

    ``fn`` receives ``(event, ctx)`` and may mutate ``ctx.workflow_data``
    so later stages observe its output. Returning a non-``None`` value is
    optional; pipelines run for side effects, not return values.
    """

    name: str
    fn: StageFn


@dataclass(slots=True)
class PipelineCheckpoint:
    """Per-event progress record.

    Stored under ``ctx.workflow_data['queue_metadata']['pipeline:<name>']``
    so the queue persists it transparently. ``completed`` lists stage
    names in execution order.
    """

    pipeline: str
    completed: list[str] = field(default_factory=list)

    def is_done(self, stage_name: str) -> bool:
        return stage_name in self.completed

    def mark(self, stage_name: str) -> None:
        if stage_name not in self.completed:
            self.completed.append(stage_name)


@dataclass(slots=True)
class Pipeline:
    """Ordered list of :class:`Stage`s, optionally gated by an event filter.

    Register stages with :meth:`add_stage` or the :meth:`stage` decorator::

        pipeline = Pipeline("ship-order", event_filter=lambda ev: isinstance(ev, OrderCreated))

        @pipeline.stage("validate")
        async def validate(event, ctx): ...

        @pipeline.stage("charge-card")
        async def charge(event, ctx): ...

        @pipeline.stage("dispatch-label")
        async def label(event, ctx): ...
    """

    name: str
    event_filter: Filter | None = None
    stages: list[Stage] = field(default_factory=list)
    auto_ack: bool = True

    def add_stage(self, name: str, fn: StageFn) -> Stage:
        if any(s.name == name for s in self.stages):
            raise ValueError(f"Pipeline {self.name!r} already has stage {name!r}")
        stage = Stage(name=name, fn=fn)
        self.stages.append(stage)
        return stage

    def stage(self, name: str) -> Callable[[StageFn], StageFn]:
        """Decorator: ``@pipeline.stage("step-name")``."""

        def _decorate(fn: StageFn) -> StageFn:
            self.add_stage(name, fn)
            return fn

        return _decorate

    def add_stage_class(self, cls: type[BaseStage]) -> Stage:
        """Register a :class:`BaseStage` subclass. Used by ``__init_subclass__`` —
        callers normally just inherit from a pipeline-bound base class instead.
        """

        instance = cls()
        return self.add_stage(cls.__stage_name__, instance)

    def base_stage(self, name: str = "Stage") -> type[BaseStage]:
        """Return an abstract :class:`BaseStage` bound to this pipeline.

        Subclassing the returned class is the shortcut for inheritance-based
        registration::

            ship = Pipeline("ship-order")
            ShipStage = ship.base_stage()

            class Validate(ShipStage):
                async def __call__(self, event, ctx): ...
        """

        return type(name, (BaseStage,), {}, pipeline=self, abstract=True)

    def applies(self, event: Event) -> bool:
        if self.event_filter is None:
            return True
        try:
            return bool(self.event_filter(event))
        except Exception:  # noqa: BLE001 — filter guard, not propagation error
            return False


def pipeline_stage(pipeline: Pipeline, name: str) -> Callable[[StageFn], StageFn]:
    """Stand-alone decorator form: ``@pipeline_stage(my_pipeline, "step")``."""

    return pipeline.stage(name)


class BaseStage:
    """Inheritance-based stage registration.

    Subclass with the ``pipeline=`` class kwarg (or use
    :meth:`Pipeline.base_stage` once and inherit from the returned base)
    to auto-register the stage into the pipeline at class-definition
    time. Registration order = declaration order, which equals execution
    order at runtime.

    ::

        ship = Pipeline("ship-order")

        class ShipStage(BaseStage, pipeline=ship, abstract=True):
            pass

        class Validate(ShipStage):
            async def __call__(self, event, ctx):
                ...

        class Charge(ShipStage):
            name = "charge-card"      # override the auto-derived name
            async def __call__(self, event, ctx):
                ...

    Class-kwarg options:

    * ``pipeline`` — target :class:`Pipeline`. Inherited by descendants
      unless they override.
    * ``abstract`` — when ``True``, the class is treated as an
      intermediate base and not registered.
    * ``name`` — explicit stage name. Defaults to the class's name
      converted to ``kebab-case``.

    Subclasses can also set a class-level ``name`` attribute as an
    alternative to the keyword override.
    """

    __pipeline__: ClassVar[Pipeline | None] = None
    __stage_name__: ClassVar[str] = ""
    __abstract__: ClassVar[bool] = True

    name: ClassVar[str] = ""

    def __init_subclass__(
        cls,
        *,
        pipeline: Pipeline | None = None,
        name: str | None = None,
        abstract: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init_subclass__(**kwargs)
        if pipeline is not None:
            cls.__pipeline__ = pipeline
        cls.__abstract__ = abstract

        # Resolve effective name: explicit class kwarg → class-level attribute → derived.
        explicit = name or cls.__dict__.get("name") or ""
        cls.__stage_name__ = explicit or _to_kebab(cls.__name__)
        cls.name = cls.__stage_name__

        if abstract or cls.__pipeline__ is None:
            return
        cls.__pipeline__.add_stage_class(cls)

    async def __call__(self, event: Event, ctx: EventContext) -> Any:
        raise NotImplementedError(
            f"{type(self).__name__}.__call__ must be implemented",
        )


class PipelineRunner:
    """Drives one event through one pipeline with resumable checkpoints.

    Reads the existing checkpoint from ``ctx.queue.metadata``, skips every
    stage already completed (and any the handler marked via
    :meth:`CtxPipeline.skip`), runs the rest, persists the updated
    checkpoint after each stage so a restart picks up where the last
    successful stage left off. After the final stage the runner calls
    :meth:`EventContext.atomic_completed` so the persistent queue can
    drop the event row.

    ``middleware_chain`` is wrapped around **each individual stage call**
    so router-level ``inner_middleware`` runs once per stage, not once per
    pipeline. Pass ``None`` (the default) to skip middleware wrapping —
    useful for direct unit tests of a runner.
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
        try:
            for stage in self.pipeline.stages:
                if ctx.pipeline._skip_remaining:
                    checkpoint.mark(stage.name)
                    await self._persist_checkpoint(ctx, checkpoint)
                    continue
                if checkpoint.is_done(stage.name) or ctx.pipeline.is_skipped(stage.name):
                    if (
                        ctx.pipeline.is_skipped(stage.name)
                        and not checkpoint.is_done(stage.name)
                    ):
                        checkpoint.mark(stage.name)
                        await self._persist_checkpoint(ctx, checkpoint)
                    log.debug(
                        "pipeline.skip_stage",
                        pipeline=self.pipeline.name,
                        stage=stage.name,
                        reason=(
                            "completed" if checkpoint.is_done(stage.name) else "skipped"
                        ),
                    )
                    continue

                ctx.pipeline.current_stage = stage.name
                try:
                    await self._invoke_stage(stage, event, ctx)
                except Exception as exc:
                    log.error(
                        "pipeline.stage_failed",
                        pipeline_name=self.pipeline.name,
                        stage_name=stage.name,
                        error=f"{type(exc).__name__}: {exc}",
                    )
                    raise PipelineStageError(
                        f"{self.pipeline.name}.{stage.name} failed: {exc}",
                    ) from exc
                checkpoint.mark(stage.name)
                await self._persist_checkpoint(ctx, checkpoint)
        finally:
            ctx.pipeline.clear_skip()
            ctx.pipeline.current_pipeline = previous_pipeline
            ctx.pipeline.current_stage = previous_stage

        if self.pipeline.auto_ack and not ctx.queue.is_acked:
            await ctx.atomic_completed()
        return True

    async def _invoke_stage(self, stage: Stage, event: Event, ctx: EventContext) -> None:
        async def _terminal(_ev: Event, _ctx: EventContext) -> Any:
            return await stage.fn(_ev, _ctx)

        handler = (
            self.middleware_chain.wrap(_terminal)
            if self.middleware_chain is not None
            else _terminal
        )
        await handler(event, ctx)

    def _checkpoint_key(self) -> str:
        return f"pipeline:{self.pipeline.name}"

    def _load_checkpoint(self, ctx: EventContext) -> PipelineCheckpoint:
        raw = ctx.queue.metadata.get(self._checkpoint_key())
        if isinstance(raw, PipelineCheckpoint):
            return raw
        if isinstance(raw, dict):
            return PipelineCheckpoint(
                pipeline=str(raw.get("pipeline") or self.pipeline.name),
                completed=list(raw.get("completed") or []),
            )
        return PipelineCheckpoint(pipeline=self.pipeline.name)

    async def _persist_checkpoint(
        self,
        ctx: EventContext,
        checkpoint: PipelineCheckpoint,
    ) -> None:
        ctx.queue.metadata[self._checkpoint_key()] = {
            "pipeline": checkpoint.pipeline,
            "completed": list(checkpoint.completed),
        }
        await ctx.queue.persist_metadata()


class PipelineRouter:
    """Aiogram-style decorator surface for many pipelines.

    Attach to a :class:`Dispatcher` via :meth:`bind` — every event the
    dispatcher fans out is also evaluated against every pipeline. A
    pipeline whose :attr:`Pipeline.event_filter` matches the event fires;
    pipelines whose filter does not match are skipped.

    Example::

        router = PipelineRouter()

        @router.pipeline("ship-order", event_filter=F.func(lambda ev: isinstance(ev, OrderCreated)))
        class ShipOrder:
            @staticmethod
            @router.stage("ship-order", "validate")
            async def validate(event, ctx): ...

            @staticmethod
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
    ) -> Pipeline:
        """Get-or-create a pipeline by name."""

        existing = self._pipelines.get(name)
        if existing is not None:
            return existing
        new = Pipeline(name=name, event_filter=event_filter, auto_ack=auto_ack)
        self._pipelines[name] = new
        return new

    def stage(self, pipeline_name: str, stage_name: str) -> Callable[[StageFn], StageFn]:
        """Decorator scoped by ``pipeline_name`` — creates the pipeline lazily.

        ::

            @router.stage("ship-order", "validate")
            async def validate(event, ctx): ...
        """

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
            async def __call__(self, handler, event, ctx):  # noqa: ANN001 — middleware shape
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


__all__ = [
    "BaseStage",
    "Pipeline",
    "PipelineCheckpoint",
    "PipelineRouter",
    "PipelineRunner",
    "PipelineStageError",
    "Stage",
    "StageFn",
    "pipeline_stage",
    "stage_name_of",
]

"""Pipeline core — :class:`Stage`, :class:`Pipeline`, :class:`BaseStage`.

The runner lives next door in :mod:`avitoapi.pipeline.runner`; this
module owns only the declarative pieces — what a stage is, how stages
register into a pipeline, the checkpoint shape that survives restarts.
"""

from __future__ import annotations

import re
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any, ClassVar

from ..exceptions import SDKError
from ..logging import get_logger
from .hooks import (
    CompensateHook,
    FailureHook,
    PipelineHooks,
    RunHook,
    StageHook,
)
from .retry import RetryPolicy

if TYPE_CHECKING:
    from ..events._base import Event
    from ..routers.context import EventContext
    from ..routers.observer import Filter

log = get_logger(__name__)


StageFn = Callable[["Event", "EventContext"], Awaitable[Any]]
PartitionFn = Callable[["Event"], "str | None"]
# stage_name_of accepts anything that has a __stage_name__ attribute, plus a
# bare string. Kept loose intentionally so the public API doesn't force users
# to import BaseStage just to pass a name.
StageLike = Any


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


class CheckpointState(StrEnum):
    """Lifecycle states of a :class:`PipelineCheckpoint`.

    Persisted to the queue row so a restart can resume mid-rollback.
    """

    RUNNING = "running"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"
    DONE = "done"
    FAILED = "failed"


class PipelineStageError(SDKError):
    """A stage callable raised. The pipeline aborts; queue keeps the event."""

    default_message = "Pipeline stage failed"


class CompensationFailed(SDKError):
    """A compensate callable raised while the pipeline was rolling back.

    The pipeline keeps walking the remaining compensates; this exception
    is logged and recorded in :attr:`PipelineCheckpoint.compensation_errors`
    so ops can inspect later.
    """

    default_message = "Stage compensation failed"


@dataclass(slots=True)
class Stage:
    """One named step inside a :class:`Pipeline`.

    Mutable fields beyond ``name`` + ``fn`` are opt-in — the bare
    construction ``Stage(name, fn)`` keeps current behaviour. The
    runner consults each field at run time::

    * ``compensate_fn`` — called in reverse order on saga rollback.
    * ``retry`` — :class:`RetryPolicy` wrapping the call.
    * ``timeout`` — wraps the call in :func:`asyncio.wait_for`.
    * ``when`` — :class:`Filter`-shaped predicate; ``False`` → skip + mark complete.
    * ``output`` — key in ``ctx.outputs`` to write the stage's return value to.
    * ``depends_on`` — tuple of stage names that must complete first;
      stages with disjoint deps in the same layer run concurrently.
    """

    name: str
    fn: StageFn
    compensate_fn: StageFn | None = None
    retry: RetryPolicy | None = None
    timeout: float | None = None
    when: Filter | None = None
    output: str | None = None
    depends_on: tuple[str, ...] = ()


@dataclass(slots=True)
class PipelineCheckpoint:
    """Per-event progress record persisted in ``ctx.queue.metadata``.

    ``completed`` and ``compensated`` are ordered by execution. ``state``
    survives mid-rollback restarts so the runner picks up correctly.
    """

    pipeline: str
    completed: list[str] = field(default_factory=list)
    compensated: list[str] = field(default_factory=list)
    compensation_errors: dict[str, str] = field(default_factory=dict)
    state: CheckpointState = CheckpointState.RUNNING

    def is_done(self, stage_name: str) -> bool:
        return stage_name in self.completed

    def is_compensated(self, stage_name: str) -> bool:
        return stage_name in self.compensated

    def mark(self, stage_name: str) -> None:
        if stage_name not in self.completed:
            self.completed.append(stage_name)

    def mark_compensated(self, stage_name: str) -> None:
        if stage_name not in self.compensated:
            self.compensated.append(stage_name)

    def to_dict(self) -> dict[str, Any]:
        return {
            "pipeline": self.pipeline,
            "completed": list(self.completed),
            "compensated": list(self.compensated),
            "compensation_errors": dict(self.compensation_errors),
            "state": str(self.state),
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any], default_name: str) -> PipelineCheckpoint:
        raw_state = raw.get("state")
        try:
            state = CheckpointState(raw_state) if raw_state else CheckpointState.RUNNING
        except ValueError:
            log.warning(
                "pipeline.checkpoint.unknown_state",
                pipeline=default_name,
                state=raw_state,
                fallback=CheckpointState.RUNNING.value,
            )
            state = CheckpointState.RUNNING
        return cls(
            pipeline=str(raw.get("pipeline") or default_name),
            completed=list(raw.get("completed") or []),
            compensated=list(raw.get("compensated") or []),
            compensation_errors=dict(raw.get("compensation_errors") or {}),
            state=state,
        )


@dataclass(slots=True)
class Pipeline:
    """Ordered list of :class:`Stage`s with optional event filter + lifecycle hooks.

    ``saga=True`` opts the pipeline into automatic compensation — on
    any stage failure, the runner walks ``checkpoint.completed`` in
    reverse and calls each stage's ``compensate_fn``. The original
    exception is preserved as the cause of the raised
    :class:`PipelineStageError`.

    ``partition_by`` lets a :class:`avitoapi.queue.QueueWorker`
    serialise this pipeline by event-derived key (e.g. ``account_id``).
    The pipeline itself is partition-agnostic; the worker does the
    locking.
    """

    name: str
    event_filter: Filter | None = None
    stages: list[Stage] = field(default_factory=list)
    auto_ack: bool = True
    saga: bool = False
    partition_by: PartitionFn | None = None
    hooks: PipelineHooks = field(default_factory=PipelineHooks)

    def add_stage(
        self,
        name: str,
        fn: StageFn,
        *,
        compensate_fn: StageFn | None = None,
        retry: RetryPolicy | None = None,
        timeout: float | None = None,
        when: Filter | None = None,
        output: str | None = None,
        depends_on: Iterable[str] = (),
    ) -> Stage:
        if any(s.name == name for s in self.stages):
            raise ValueError(f"Pipeline {self.name!r} already has stage {name!r}")
        stage = Stage(
            name=name,
            fn=fn,
            compensate_fn=compensate_fn,
            retry=retry,
            timeout=timeout,
            when=when,
            output=output,
            depends_on=tuple(depends_on),
        )
        self.stages.append(stage)
        return stage

    def stage(
        self,
        name: str,
        *,
        compensate_fn: StageFn | None = None,
        retry: RetryPolicy | None = None,
        timeout: float | None = None,
        when: Filter | None = None,
        output: str | None = None,
        depends_on: Iterable[str] = (),
    ) -> Callable[[StageFn], StageFn]:
        """Decorator: ``@pipeline.stage("step-name", retry=..., timeout=...)``."""

        def _decorate(fn: StageFn) -> StageFn:
            self.add_stage(
                name,
                fn,
                compensate_fn=compensate_fn,
                retry=retry,
                timeout=timeout,
                when=when,
                output=output,
                depends_on=depends_on,
            )
            return fn

        return _decorate

    def add_stage_class(self, cls: type[BaseStage]) -> Stage:
        """Register a :class:`BaseStage` subclass — invoked by ``__init_subclass__``."""

        instance = cls()
        return self.add_stage(
            cls.__stage_name__,
            instance,
            compensate_fn=instance.compensate if cls.__has_compensate__ else None,
            retry=cls.__retry__,
            timeout=cls.__timeout__,
            when=cls.__when__,
            output=cls.__output__,
            depends_on=cls.__depends_on__,
        )

    def base_stage(self, name: str = "Stage") -> type[BaseStage]:
        """Return an abstract :class:`BaseStage` bound to this pipeline."""

        return type(name, (BaseStage,), {}, pipeline=self, abstract=True)

    def get_stage(self, name: str) -> Stage | None:
        for stage in self.stages:
            if stage.name == name:
                return stage
        return None

    def applies(self, event: Event) -> bool:
        if self.event_filter is None:
            return True
        try:
            return bool(self.event_filter(event))
        except Exception:  # noqa: BLE001 — filter guard, not propagation error
            return False

    def before_run(self, fn: RunHook) -> RunHook:
        """``@pipeline.before_run`` — fired once before stage iteration."""

        self.hooks.before_run.append(fn)
        return fn

    def after_run(self, fn: RunHook) -> RunHook:
        """``@pipeline.after_run`` — fired once after successful completion."""

        self.hooks.after_run.append(fn)
        return fn

    def on_failure(self, fn: FailureHook) -> FailureHook:
        """``@pipeline.on_failure`` — fired with ``(event, ctx, exc)`` before compensate."""

        self.hooks.on_failure.append(fn)
        return fn

    def on_stage_start(self, fn: StageHook) -> StageHook:
        self.hooks.on_stage_start.append(fn)
        return fn

    def on_stage_complete(self, fn: StageHook) -> StageHook:
        self.hooks.on_stage_complete.append(fn)
        return fn

    def on_stage_skipped(self, fn: StageHook) -> StageHook:
        self.hooks.on_stage_skipped.append(fn)
        return fn

    def on_stage_failed(self, fn: StageHook) -> StageHook:
        self.hooks.on_stage_failed.append(fn)
        return fn

    def on_compensate(
        self,
        stage_name: str | None = None,
    ) -> Callable[[CompensateHook], CompensateHook]:
        """``@pipeline.on_compensate("charge")`` — per-stage compensate observer.

        Without a stage name, the hook fires for every compensation call.
        """

        def _decorate(fn: CompensateHook) -> CompensateHook:
            if stage_name is None:
                self.hooks.on_compensate.append(fn)
            else:
                bucket = self.hooks.on_compensate_per_stage.setdefault(stage_name, [])
                bucket.append(fn)
            return fn

        return _decorate


def pipeline_stage(pipeline: Pipeline, name: str) -> Callable[[StageFn], StageFn]:
    """Stand-alone decorator form: ``@pipeline_stage(my_pipeline, "step")``."""

    return pipeline.stage(name)


class BaseStage:
    """Inheritance-based stage registration with first-class options.

    Subclass with a ``pipeline=`` class kwarg (or inherit from a base
    returned by :meth:`Pipeline.base_stage`). Class-level attributes
    map onto :class:`Stage` fields::

        class Charge(ShipStage):
            name = "charge-card"
            retry = RetryPolicy(max_attempts=5, backoff=ExponentialBackoff())
            timeout = 5.0
            when = F.func(lambda ev: ev.method == "card")
            output = "charge_id"
            depends_on = ("validate",)

            async def __call__(self, event, ctx) -> str:
                charge_id = await charge_card(event.order_id)
                return charge_id              # → ctx.outputs["charge_id"]

            async def compensate(self, event, ctx) -> None:
                await refund(ctx.outputs["charge_id"])

    Compensate is auto-wired when the subclass defines a coroutine
    method named ``compensate``. ``abstract=True`` on the base class
    prevents registration.
    """

    __pipeline__: ClassVar[Pipeline | None] = None
    __stage_name__: ClassVar[str] = ""
    __abstract__: ClassVar[bool] = True
    __has_compensate__: ClassVar[bool] = False
    __retry__: ClassVar[RetryPolicy | None] = None
    __timeout__: ClassVar[float | None] = None
    __when__: ClassVar[Filter | None] = None
    __output__: ClassVar[str | None] = None
    __depends_on__: ClassVar[tuple[str, ...]] = ()

    name: ClassVar[str] = ""
    retry: ClassVar[RetryPolicy | None] = None
    timeout: ClassVar[float | None] = None
    when: ClassVar[Filter | None] = None
    output: ClassVar[str | None] = None
    depends_on: ClassVar[tuple[str, ...]] = ()

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

        explicit = name or cls.__dict__.get("name") or ""
        cls.__stage_name__ = explicit or _to_kebab(cls.__name__)
        cls.name = cls.__stage_name__

        # Materialise stage options from class-level attributes.
        cls.__retry__ = cls.__dict__.get("retry", cls.__retry__)
        cls.__timeout__ = cls.__dict__.get("timeout", cls.__timeout__)
        cls.__when__ = cls.__dict__.get("when", cls.__when__)
        cls.__output__ = cls.__dict__.get("output", cls.__output__)
        depends = cls.__dict__.get("depends_on", cls.__depends_on__)
        cls.__depends_on__ = tuple(depends)

        own_compensate = "compensate" in cls.__dict__
        cls.__has_compensate__ = own_compensate or cls.__has_compensate__

        if abstract or cls.__pipeline__ is None:
            return
        cls.__pipeline__.add_stage_class(cls)

    async def __call__(self, event: Event, ctx: EventContext) -> Any:
        raise NotImplementedError(
            f"{type(self).__name__}.__call__ must be implemented",
        )

    async def compensate(self, event: Event, ctx: EventContext) -> None:
        """Override to undo the stage's effects in saga rollback."""


__all__ = [
    "BaseStage",
    "CompensationFailed",
    "PartitionFn",
    "Pipeline",
    "PipelineCheckpoint",
    "PipelineStageError",
    "Stage",
    "StageFn",
    "pipeline_stage",
    "stage_name_of",
]

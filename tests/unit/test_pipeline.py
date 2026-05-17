"""Unit tests for the pipeline subsystem (resumable stages + auto ack)."""

from __future__ import annotations

import pytest
from avitoapi import (
    BaseEvent,
    BaseMiddleware,
    Dispatcher,
    EventContext,
    EventQueue,
    HandlerType,
    Pipeline,
    PipelineRouter,
    PipelineRunner,
    PipelineStageError,
)
from avitoapi.routers.middleware import MiddlewareChain
from avitoapi.storage.memory import MemoryStorage


class _OrderPlaced(BaseEvent, event_name="orders.placed"):
    def __init__(self, *, order_id: str) -> None:
        super().__init__()
        self.order_id = order_id


async def test_pipeline_runs_each_stage_in_order():
    pipeline = Pipeline(name="ship")
    fired: list[str] = []

    @pipeline.stage("validate")
    async def _validate(event, ctx: EventContext):
        fired.append("validate")

    @pipeline.stage("charge")
    async def _charge(event, ctx: EventContext):
        fired.append("charge")

    @pipeline.stage("dispatch")
    async def _dispatch(event, ctx: EventContext):
        fired.append("dispatch")

    runner = PipelineRunner(pipeline)
    ctx = EventContext(event=_OrderPlaced(order_id="o-1"))
    await runner.run(_OrderPlaced(order_id="o-1"), ctx)
    assert fired == ["validate", "charge", "dispatch"]


async def test_pipeline_skips_completed_stages_on_replay():
    pipeline = Pipeline(name="ship", auto_ack=False)
    fired: list[str] = []

    @pipeline.stage("validate")
    async def _validate(event, ctx: EventContext):
        fired.append("validate")

    @pipeline.stage("charge")
    async def _charge(event, ctx: EventContext):
        fired.append("charge")

    @pipeline.stage("dispatch")
    async def _dispatch(event, ctx: EventContext):
        fired.append("dispatch")

    runner = PipelineRunner(pipeline)
    ctx = EventContext(event=_OrderPlaced(order_id="o-1"))
    # Pretend the first stage already ran before a restart.
    ctx.queue.metadata["pipeline:ship"] = {"pipeline": "ship", "completed": ["validate"]}
    await runner.run(_OrderPlaced(order_id="o-1"), ctx)
    assert fired == ["charge", "dispatch"]


async def test_pipeline_aborts_on_stage_failure_and_keeps_event():
    pipeline = Pipeline(name="ship")
    fired: list[str] = []

    @pipeline.stage("validate")
    async def _validate(event, ctx: EventContext):
        fired.append("validate")

    @pipeline.stage("boom")
    async def _boom(event, ctx: EventContext):
        raise RuntimeError("boom")

    runner = PipelineRunner(pipeline)
    ctx = EventContext(event=_OrderPlaced(order_id="o-1"))
    with pytest.raises(PipelineStageError):
        await runner.run(_OrderPlaced(order_id="o-1"), ctx)
    # validate should still be marked complete so replay resumes from boom
    completed = ctx.queue.metadata["pipeline:ship"]["completed"]
    assert completed == ["validate"]


async def test_pipeline_router_binds_to_dispatcher_and_sets_handler_type():
    dispatcher = Dispatcher(event_queue=EventQueue(MemoryStorage()))
    router = PipelineRouter()
    seen_types: list[HandlerType] = []

    @router.stage("ship", "validate")
    async def _validate(event, ctx: EventContext):
        seen_types.append(ctx.handler_type)

    router.bind(dispatcher)
    await dispatcher.feed_event(_OrderPlaced(order_id="o-9"))
    assert seen_types == [HandlerType.PIPELINE]
    # auto_ack drained the queue.
    assert await dispatcher.event_queue.pending_count() == 0


async def test_pipeline_skip_named_stages_via_ctx():
    pipeline = Pipeline(name="ship")
    fired: list[str] = []

    @pipeline.stage("validate")
    async def _validate(event, ctx: EventContext):
        fired.append("validate")
        ctx.pipeline.skip("charge")

    @pipeline.stage("charge")
    async def _charge(event, ctx: EventContext):
        fired.append("charge")

    @pipeline.stage("dispatch")
    async def _dispatch(event, ctx: EventContext):
        fired.append("dispatch")

    runner = PipelineRunner(pipeline)
    ctx = EventContext(event=_OrderPlaced(order_id="o-1"))
    await runner.run(_OrderPlaced(order_id="o-1"), ctx)
    assert fired == ["validate", "dispatch"]
    # Skipped stage must be persisted as complete so replay does not re-run it.
    assert "charge" in ctx.queue.metadata["pipeline:ship"]["completed"]


async def test_pipeline_skip_remaining_short_circuits():
    pipeline = Pipeline(name="ship")
    fired: list[str] = []

    @pipeline.stage("validate")
    async def _validate(event, ctx: EventContext):
        fired.append("validate")
        ctx.pipeline.skip_remaining()

    @pipeline.stage("charge")
    async def _charge(event, ctx: EventContext):
        fired.append("charge")

    @pipeline.stage("dispatch")
    async def _dispatch(event, ctx: EventContext):
        fired.append("dispatch")

    runner = PipelineRunner(pipeline)
    ctx = EventContext(event=_OrderPlaced(order_id="o-1"))
    await runner.run(_OrderPlaced(order_id="o-1"), ctx)
    assert fired == ["validate"]
    completed = ctx.queue.metadata["pipeline:ship"]["completed"]
    assert completed == ["validate", "charge", "dispatch"]


async def test_base_stage_subclassing_registers_in_declaration_order():
    ship = Pipeline(name="ship")
    ShipStage = ship.base_stage()
    fired: list[str] = []

    class Validate(ShipStage):
        async def __call__(self, event, ctx: EventContext):
            fired.append("validate")

    class Charge(ShipStage):
        name = "charge-card"

        async def __call__(self, event, ctx: EventContext):
            fired.append("charge")

    class Dispatch(ShipStage):
        async def __call__(self, event, ctx: EventContext):
            fired.append("dispatch")

    assert [s.name for s in ship.stages] == ["validate", "charge-card", "dispatch"]

    runner = PipelineRunner(ship)
    ctx = EventContext(event=_OrderPlaced(order_id="o-1"))
    await runner.run(_OrderPlaced(order_id="o-1"), ctx)
    assert fired == ["validate", "charge", "dispatch"]


async def test_skip_accepts_stage_class_references():
    ship = Pipeline(name="ship")
    ShipStage = ship.base_stage()
    fired: list[str] = []

    class Validate(ShipStage):
        async def __call__(self, event, ctx: EventContext):
            fired.append("validate")
            ctx.pipeline.skip(Charge)  # class, not string

    class Charge(ShipStage):
        async def __call__(self, event, ctx: EventContext):
            fired.append("charge")

    class Dispatch(ShipStage):
        async def __call__(self, event, ctx: EventContext):
            fired.append("dispatch")

    runner = PipelineRunner(ship)
    ctx = EventContext(event=_OrderPlaced(order_id="o-1"))
    await runner.run(_OrderPlaced(order_id="o-1"), ctx)
    assert fired == ["validate", "dispatch"]


async def test_middlewares_wrap_each_stage_individually():
    pipeline = Pipeline(name="ship")
    fired: list[str] = []

    @pipeline.stage("a")
    async def _a(event, ctx: EventContext):
        fired.append("a")

    @pipeline.stage("b")
    async def _b(event, ctx: EventContext):
        fired.append("b")

    @pipeline.stage("c")
    async def _c(event, ctx: EventContext):
        fired.append("c")

    calls: list[str] = []

    class Trace(BaseMiddleware):
        async def __call__(self, handler, event, ctx):
            calls.append(f"in:{ctx.pipeline.current_stage}")
            try:
                return await handler(event, ctx)
            finally:
                calls.append(f"out:{ctx.pipeline.current_stage}")

    chain = MiddlewareChain()
    chain.register(Trace())
    runner = PipelineRunner(pipeline, middleware_chain=chain)
    await runner.run(_OrderPlaced(order_id="o-1"), EventContext(event=_OrderPlaced(order_id="o-1")))

    # Each stage produced one in/out pair (middleware wrapped each stage individually).
    assert fired == ["a", "b", "c"]
    assert calls == ["in:a", "out:a", "in:b", "out:b", "in:c", "out:c"]


async def test_dispatcher_inner_middleware_runs_per_pipeline_stage():
    dispatcher = Dispatcher(event_queue=EventQueue(MemoryStorage()))
    router = PipelineRouter()
    counter: list[str] = []

    class Trace(BaseMiddleware):
        async def __call__(self, handler, event, ctx):
            counter.append(ctx.pipeline.current_stage)
            return await handler(event, ctx)

    dispatcher.inner_middleware.register(Trace())

    @router.stage("ship", "validate")
    async def _validate(event, ctx: EventContext): ...

    @router.stage("ship", "charge")
    async def _charge(event, ctx: EventContext): ...

    router.bind(dispatcher)
    await dispatcher.feed_event(_OrderPlaced(order_id="o-1"))
    # Trace middleware fires once per stage.
    assert counter == ["validate", "charge"]


async def test_pipeline_does_not_apply_when_filter_rejects():
    pipeline = Pipeline(
        name="vip-only",
        event_filter=lambda ev: getattr(ev, "order_id", "").startswith("VIP-"),
    )
    fired = []

    @pipeline.stage("notify")
    async def _notify(event, ctx: EventContext):
        fired.append(event.order_id)

    runner = PipelineRunner(pipeline)
    await runner.run(_OrderPlaced(order_id="o-1"), EventContext(event=_OrderPlaced(order_id="o-1")))
    await runner.run(
        _OrderPlaced(order_id="VIP-7"),
        EventContext(event=_OrderPlaced(order_id="VIP-7")),
    )
    assert fired == ["VIP-7"]

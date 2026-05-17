"""Unit tests for pipeline-saga-v2: retry, timeout, when, output, compensate, DAG, hooks, ParallelGroup."""

from __future__ import annotations

import asyncio

import pytest
from avitoapi import (
    BaseEvent,
    ConstantBackoff,
    EventContext,
    ExponentialBackoff,
    ParallelGroup,
    Pipeline,
    PipelineRunner,
    PipelineStageError,
    RetryPolicy,
)


class _OrderPlaced(BaseEvent, event_name="orders.placed.v2"):
    def __init__(self, *, order_id: str = "o-1", method: str = "card") -> None:
        super().__init__()
        self.order_id = order_id
        self.method = method


# ---------------------------------------------------------------- 1. saga / compensate


async def test_saga_compensates_completed_stages_in_reverse_order():
    pipeline = Pipeline(name="ship", saga=True)
    fired: list[str] = []

    @pipeline.stage("validate")
    async def _validate(event, ctx):
        fired.append("validate")

    async def _undo_charge(event, ctx):
        fired.append("undo:charge")

    pipeline.add_stage("charge", _make_recorder("charge", fired), compensate_fn=_undo_charge)

    async def _undo_label(event, ctx):
        fired.append("undo:label")

    pipeline.add_stage("label", _make_recorder("label", fired), compensate_fn=_undo_label)

    @pipeline.stage("ship")
    async def _ship(event, ctx):
        fired.append("ship")
        raise RuntimeError("carrier-down")

    runner = PipelineRunner(pipeline)
    ctx = EventContext(event=_OrderPlaced())
    with pytest.raises(PipelineStageError):
        await runner.run(_OrderPlaced(), ctx)

    assert fired == ["validate", "charge", "label", "ship", "undo:label", "undo:charge"]
    checkpoint = ctx.queue.metadata["pipeline:ship"]
    assert checkpoint["state"] == "compensated"
    assert checkpoint["compensated"] == ["label", "charge"]


async def test_saga_resumes_compensation_after_restart():
    pipeline = Pipeline(name="ship", saga=True)
    fired: list[str] = []

    async def _undo_validate(event, ctx):
        fired.append("undo:validate")

    pipeline.add_stage("validate", _make_recorder("validate", fired), compensate_fn=_undo_validate)

    async def _undo_charge(event, ctx):
        fired.append("undo:charge")

    pipeline.add_stage("charge", _make_recorder("charge", fired), compensate_fn=_undo_charge)

    runner = PipelineRunner(pipeline)
    ctx = EventContext(event=_OrderPlaced())
    # Simulate restart hit mid-compensation.
    ctx.queue.metadata["pipeline:ship"] = {
        "pipeline": "ship",
        "completed": ["validate", "charge"],
        "compensated": ["charge"],
        "state": "compensating",
    }
    await runner.run(_OrderPlaced(), ctx)
    assert fired == ["undo:validate"]
    assert ctx.queue.metadata["pipeline:ship"]["state"] == "compensated"


async def test_saga_records_compensation_errors_and_continues():
    pipeline = Pipeline(name="ship", saga=True)

    async def _undo_a(event, ctx):
        raise RuntimeError("undo failed")

    pipeline.add_stage("a", _make_noop(), compensate_fn=_undo_a)
    pipeline.add_stage("b", _make_failer("boom"))

    runner = PipelineRunner(pipeline)
    ctx = EventContext(event=_OrderPlaced())
    with pytest.raises(PipelineStageError):
        await runner.run(_OrderPlaced(), ctx)
    cp = ctx.queue.metadata["pipeline:ship"]
    assert "a" in cp["compensation_errors"]
    assert cp["state"] == "compensated"


# ---------------------------------------------------------------- 4. retry


async def test_stage_retry_succeeds_on_third_attempt():
    pipeline = Pipeline(name="retry")
    attempts = {"n": 0}

    async def _flaky(event, ctx):
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise RuntimeError("transient")

    pipeline.add_stage(
        "flaky",
        _flaky,
        retry=RetryPolicy(max_attempts=5, backoff=ConstantBackoff(0.0)),
    )
    runner = PipelineRunner(pipeline)
    ctx = EventContext(event=_OrderPlaced())
    await runner.run(_OrderPlaced(), ctx)
    assert attempts["n"] == 3


async def test_stage_retry_gives_up_after_max_attempts():
    pipeline = Pipeline(name="retry")

    async def _always_fails(event, ctx):
        raise RuntimeError("dead")

    pipeline.add_stage(
        "dead",
        _always_fails,
        retry=RetryPolicy(max_attempts=2, backoff=ConstantBackoff(0.0)),
    )
    runner = PipelineRunner(pipeline)
    ctx = EventContext(event=_OrderPlaced())
    with pytest.raises(PipelineStageError):
        await runner.run(_OrderPlaced(), ctx)


async def test_stage_retry_filters_by_retry_on():
    pipeline = Pipeline(name="retry")
    attempts = {"n": 0}

    async def _fails_unretryable(event, ctx):
        attempts["n"] += 1
        raise ValueError("not retryable")

    pipeline.add_stage(
        "v",
        _fails_unretryable,
        retry=RetryPolicy(
            max_attempts=5,
            backoff=ConstantBackoff(0.0),
            retry_on=(RuntimeError,),
        ),
    )
    runner = PipelineRunner(pipeline)
    ctx = EventContext(event=_OrderPlaced())
    with pytest.raises(PipelineStageError):
        await runner.run(_OrderPlaced(), ctx)
    assert attempts["n"] == 1


# ---------------------------------------------------------------- 5. timeout


async def test_stage_timeout_aborts_slow_call():
    pipeline = Pipeline(name="t")

    async def _slow(event, ctx):
        await asyncio.sleep(1.0)

    pipeline.add_stage("slow", _slow, timeout=0.05)
    runner = PipelineRunner(pipeline)
    ctx = EventContext(event=_OrderPlaced())
    with pytest.raises(PipelineStageError):
        await runner.run(_OrderPlaced(), ctx)


# ---------------------------------------------------------------- 8. when filter


async def test_stage_when_skips_unmatched_event():
    pipeline = Pipeline(name="branch")
    fired: list[str] = []

    pipeline.add_stage(
        "card",
        _make_recorder("card", fired),
        when=lambda ev: ev.method == "card",
    )
    pipeline.add_stage(
        "wallet",
        _make_recorder("wallet", fired),
        when=lambda ev: ev.method == "wallet",
    )
    runner = PipelineRunner(pipeline)
    ctx = EventContext(event=_OrderPlaced(method="wallet"))
    await runner.run(_OrderPlaced(method="wallet"), ctx)
    assert fired == ["wallet"]
    # Both stages must be marked done — replay should not retry them.
    completed = ctx.queue.metadata["pipeline:branch"]["completed"]
    assert "card" in completed
    assert "wallet" in completed


# ---------------------------------------------------------------- 10. output binding


async def test_stage_output_is_stored_in_ctx_outputs():
    pipeline = Pipeline(name="bind")

    async def _produce(event, ctx) -> dict[str, str]:
        return {"order_id": event.order_id}

    pipeline.add_stage("produce", _produce, output="order")

    async def _consume(event, ctx) -> None:
        assert ctx.outputs["order"] == {"order_id": event.order_id}

    pipeline.add_stage("consume", _consume)
    runner = PipelineRunner(pipeline)
    ctx = EventContext(event=_OrderPlaced(order_id="abc"))
    await runner.run(_OrderPlaced(order_id="abc"), ctx)


# ---------------------------------------------------------------- 7. DAG / depends_on / parallel layer


async def test_depends_on_runs_parallel_siblings_in_one_layer():
    pipeline = Pipeline(name="dag")
    events: list[str] = []

    async def _a(event, ctx):
        events.append("a:start")
        await asyncio.sleep(0.02)
        events.append("a:end")

    async def _b(event, ctx):
        events.append("b:start")
        await asyncio.sleep(0.02)
        events.append("b:end")

    pipeline.add_stage("validate", _make_noop())
    pipeline.add_stage("a", _a, depends_on=("validate",))
    pipeline.add_stage("b", _b, depends_on=("validate",))
    pipeline.add_stage("join", _make_noop(), depends_on=("a", "b"))

    runner = PipelineRunner(pipeline)
    ctx = EventContext(event=_OrderPlaced())
    await runner.run(_OrderPlaced(), ctx)
    # a and b must have overlapped — their starts both come before either end.
    starts = [i for i, e in enumerate(events) if e.endswith(":start")]
    ends = [i for i, e in enumerate(events) if e.endswith(":end")]
    assert max(starts) < min(ends)


async def test_depends_on_cycle_raises():
    pipeline = Pipeline(name="cycle")
    pipeline.add_stage("a", _make_noop(), depends_on=("b",))
    pipeline.add_stage("b", _make_noop(), depends_on=("a",))
    runner = PipelineRunner(pipeline)
    with pytest.raises(ValueError, match="cycle"):
        await runner.run(_OrderPlaced(), EventContext(event=_OrderPlaced()))


# ---------------------------------------------------------------- ParallelGroup


async def test_parallel_group_runs_members_concurrently():
    pipeline = Pipeline(name="pg")
    events: list[str] = []

    async def _a(event, ctx):
        events.append("a:start")
        await asyncio.sleep(0.02)
        events.append("a:end")

    async def _b(event, ctx):
        events.append("b:start")
        await asyncio.sleep(0.02)
        events.append("b:end")

    group = ParallelGroup(name="notify")
    group.add("a", _a)
    group.add("b", _b)
    pipeline.stages.append(group.as_stage())

    runner = PipelineRunner(pipeline)
    ctx = EventContext(event=_OrderPlaced())
    await runner.run(_OrderPlaced(), ctx)
    starts = [i for i, e in enumerate(events) if e.endswith(":start")]
    ends = [i for i, e in enumerate(events) if e.endswith(":end")]
    assert max(starts) < min(ends)


# ---------------------------------------------------------------- 12. lifecycle hooks


async def test_lifecycle_hooks_fire_in_order():
    pipeline = Pipeline(name="lh")
    trace: list[str] = []

    @pipeline.before_run
    async def _before(event, ctx):
        trace.append("before")

    @pipeline.on_stage_start
    async def _start(stage, event, ctx):
        trace.append(f"start:{stage.name}")

    @pipeline.on_stage_complete
    async def _done(stage, event, ctx):
        trace.append(f"done:{stage.name}")

    @pipeline.after_run
    async def _after(event, ctx):
        trace.append("after")

    pipeline.add_stage("a", _make_noop())
    pipeline.add_stage("b", _make_noop())

    runner = PipelineRunner(pipeline)
    ctx = EventContext(event=_OrderPlaced())
    await runner.run(_OrderPlaced(), ctx)
    assert trace == ["before", "start:a", "done:a", "start:b", "done:b", "after"]


async def test_on_failure_fires_with_original_exc():
    pipeline = Pipeline(name="fail-hook")
    captured: list[BaseException] = []

    @pipeline.on_failure
    async def _on_fail(event, ctx, exc):
        captured.append(exc)

    pipeline.add_stage("boom", _make_failer("kaboom"))

    runner = PipelineRunner(pipeline)
    with pytest.raises(PipelineStageError):
        await runner.run(_OrderPlaced(), EventContext(event=_OrderPlaced()))
    assert captured
    assert isinstance(captured[0], RuntimeError)
    assert "kaboom" in str(captured[0])


async def test_on_compensate_per_stage_fires():
    pipeline = Pipeline(name="comp-hook", saga=True)
    seen: list[str] = []

    async def _undo(event, ctx):
        pass

    pipeline.add_stage("setup", _make_noop(), compensate_fn=_undo)
    pipeline.add_stage("boom", _make_failer("kaboom"))

    @pipeline.on_compensate("setup")
    async def _compensated_setup(stage, event, ctx):
        seen.append("setup-undone")

    runner = PipelineRunner(pipeline)
    with pytest.raises(PipelineStageError):
        await runner.run(_OrderPlaced(), EventContext(event=_OrderPlaced()))
    assert seen == ["setup-undone"]


# ---------------------------------------------------------------- exponential backoff


async def test_exponential_backoff_grows_within_cap():
    bo = ExponentialBackoff(base=0.01, multiplier=2.0, max_delay=0.05, jitter=False)
    assert bo.delay(1) == pytest.approx(0.01)
    assert bo.delay(2) == pytest.approx(0.02)
    assert bo.delay(3) == pytest.approx(0.04)
    assert bo.delay(10) == pytest.approx(0.05)  # capped


# ---------------------------------------------------------------- helpers


def _make_recorder(name: str, sink: list[str]):
    async def _stage(event, ctx):
        sink.append(name)

    return _stage


def _make_noop():
    async def _stage(event, ctx):
        pass

    return _stage


def _make_failer(message: str):
    async def _stage(event, ctx):
        raise RuntimeError(message)

    return _stage


__all__: list[str] = []

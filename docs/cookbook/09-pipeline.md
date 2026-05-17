# Pipelines — resumable multi-stage handlers

A pipeline is an ordered list of named stages. After each stage
completes, its name is checkpointed into the queue row's metadata. If
the process dies between stages, the next replay skips completed
stages and resumes from the next one.

Compared to a single fat handler, pipelines give you:

* free atomic checkpoints (one row in the queue, one metadata flush
  per stage),
* declarative retry / timeout / conditional execution per stage,
* declarative output binding (`ctx.outputs`),
* DAG composition with auto-parallelisation,
* optional saga rollback (see [10-pipeline-saga.md](10-pipeline-saga.md)),
* full lifecycle hooks.

This page covers the basics. See [10-pipeline-saga.md](10-pipeline-saga.md)
for compensation, [11-pipeline-dag.md](11-pipeline-dag.md) for
`depends_on` / `ParallelGroup`.

---

## Declarative stages — `@pipeline.stage`

```python
from avitoapi import Pipeline, PipelineRouter

router = PipelineRouter()

@router.stage("ship-order", "validate")
async def validate(event, ctx):
    ctx.workflow_data["validated"] = await checks.run(event)

@router.stage("ship-order", "charge")
async def charge(event, ctx):
    await payments.capture(event.order_id)

@router.stage("ship-order", "dispatch")
async def dispatch(event, ctx):
    await warehouse.dispatch(event.order_id)

router.bind(dispatcher)
```

`PipelineRouter` is a registry — `router.bind(dispatcher)` installs an
outer middleware that runs every matching pipeline on every event.

---

## Class-based stages — `BaseStage`

For pipelines that share configuration (retries, timeouts, outputs),
the class shape is cleaner:

```python
from avitoapi import BaseStage, Pipeline, RetryPolicy, ExponentialBackoff

pipeline = Pipeline(name="ship-order")
ShipStage = pipeline.base_stage("ShipStage")     # abstract base bound to pipeline

class Validate(ShipStage):
    name = "validate"
    timeout = 5.0

    async def __call__(self, event, ctx):
        ctx.workflow_data["validated"] = await checks.run(event)

class Charge(ShipStage):
    name = "charge"
    retry = RetryPolicy(max_attempts=5, backoff=ExponentialBackoff(base=0.5, max_delay=10))
    timeout = 10.0
    output = "charge_id"

    async def __call__(self, event, ctx) -> str:
        return await payments.capture(event.order_id)

class Dispatch(ShipStage):
    name = "dispatch"
    depends_on = ("charge",)

    async def __call__(self, event, ctx):
        await warehouse.dispatch(event.order_id, charge_id=ctx.outputs["charge_id"])
```

Subclassing the bound base auto-registers the stage in `pipeline`. The
class attributes (`retry`, `timeout`, `when`, `output`, `depends_on`)
map onto `Stage` fields — read [pipeline/pipeline.py](../../avitoapi/pipeline/pipeline.py)
for the full schema.

---

## Retry per stage

`RetryPolicy` wraps the call — transient failures don't burn the
queue's `max_attempts` budget, only the stage's own.

```python
from avitoapi import RetryPolicy, ConstantBackoff, ExponentialBackoff

@pipeline.stage(
    "charge",
    retry=RetryPolicy(
        max_attempts=5,
        backoff=ExponentialBackoff(base=0.5, multiplier=2.0, max_delay=15.0),
        retry_on=(TimeoutError, ConnectionError, payments.TransientError),
        give_up_on=(payments.InsufficientFunds,),    # never retry — hard fail
    ),
)
async def charge(event, ctx):
    await payments.capture(event.order_id)
```

* `retry_on` — exception types that count as retryable. Anything else
  aborts the stage immediately.
* `give_up_on` — exception types that bypass retry even if they match
  `retry_on`. Use for explicit "do not retry" signals.

`ConstantBackoff(delay_s=2.0, jitter_pct=0.2)` is the simpler shape.
`ExponentialBackoff` uses decorrelated jitter from AWS's playbook to
defuse thundering herd.

---

## Timeout per stage

```python
@pipeline.stage("notify-customer", timeout=5.0)
async def notify(event, ctx):
    await sms.send(event.phone, "Your order shipped.")
```

Wraps the call in `asyncio.wait_for`. A `TimeoutError` counts as a
stage failure — if a `RetryPolicy` is attached and `TimeoutError` is in
`retry_on`, the retry loop kicks in. Otherwise the pipeline aborts (or
compensates, if `saga=True`).

---

## Conditional execution — `when`

Same predicate shape as observer filters ([04-filters.md](04-filters.md)).
Stages whose `when` returns `False` are marked complete and skipped —
no execution, no replay.

```python
from avitoapi import F

@pipeline.stage("notify-sms", when=F.preferences.sms == True)
async def sms(event, ctx): ...

@pipeline.stage("notify-email", when=F.preferences.email == True)
async def email(event, ctx): ...
```

`when` is evaluated on the event right before the stage runs. Use it
to fan-out per-channel notifications without separate pipelines.

---

## Output binding — `ctx.outputs`

Stages can stash their return value under a named key for downstream
consumers — no rummaging through `workflow_data`.

```python
@pipeline.stage("validate", output="validation")
async def validate(event, ctx) -> dict:
    return await checks.run(event)

@pipeline.stage("charge", output="charge_id")
async def charge(event, ctx) -> str:
    return await payments.capture(event.order_id, plan=ctx.outputs["validation"]["plan"])

@pipeline.stage("dispatch")
async def dispatch(event, ctx):
    await warehouse.dispatch(event.order_id, charge_id=ctx.outputs["charge_id"])
```

`ctx.outputs` is a plain `dict[str, Any]` populated by the runner. Output
keys are global per pipeline run — pick distinct names.

---

## Skip stages from a handler

Inside a stage you can short-circuit later ones:

```python
@pipeline.stage("preflight")
async def preflight(event, ctx):
    if event.amount == 0:
        ctx.pipeline.skip_remaining()        # drop everything after this stage
        return
    if not event.requires_charge:
        ctx.pipeline.skip("charge")          # skip a specific stage
```

Skipped stages get marked complete in the checkpoint — they don't
re-run on replay.

---

## Filter the whole pipeline

```python
from avitoapi import Pipeline, F
from avitoapi.events import OrderRefunded

pipeline = Pipeline(
    name="refund",
    event_filter=F.func(lambda ev: isinstance(ev, OrderRefunded)),
)

@pipeline.stage("notify-customer")
async def notify(event, ctx): ...

@pipeline.stage("post-back-funds")
async def repay(event, ctx): ...
```

Non-matching events propagate normally — they just don't trigger this
pipeline.

---

## Auto-ack

After the last stage completes, the runner calls
`ctx.atomic_completed()` — the queue drops the row. Disable for manual
ack control:

```python
pipeline = Pipeline(name="charge", auto_ack=False)

# ... stages ...

# In one of the stages:
@pipeline.stage("commit")
async def commit(event, ctx):
    await db.commit()
    await ctx.atomic_completed()        # you own the ack now
```

---

## Lifecycle hooks

```python
@pipeline.before_run
async def setup(event, ctx):
    ctx.workflow_data["start"] = time.monotonic()

@pipeline.after_run
async def teardown(event, ctx):
    elapsed = time.monotonic() - ctx.workflow_data["start"]
    log.info("pipeline.done", name=pipeline.name, elapsed_s=elapsed)

@pipeline.on_failure
async def alert(event, ctx, exc):
    await pagerduty.notify(f"{pipeline.name} failed: {exc}")

@pipeline.on_stage_start
async def stage_start(stage, event, ctx):
    log.info("stage.start", name=stage.name)

@pipeline.on_stage_complete
async def stage_complete(stage, event, ctx):
    log.info("stage.complete", name=stage.name)

@pipeline.on_stage_skipped
async def stage_skipped(stage, event, ctx):
    log.info("stage.skipped", name=stage.name)

@pipeline.on_stage_failed
async def stage_failed(stage, event, ctx):
    log.warning("stage.failed", name=stage.name)
```

Hook exceptions are caught and logged — they never break the pipeline.

---

## Resume semantics

The runner persists a `PipelineCheckpoint` into `ctx.queue.metadata`
after every stage. The checkpoint lives in the queue row, so a process
crash mid-pipeline leaves a recoverable record:

```python
{
  "pipeline:ship-order": {
    "pipeline": "ship-order",
    "completed": ["validate", "charge"],
    "compensated": [],
    "compensation_errors": {},
    "state": "running",                     # | done | failed | compensating | compensated
  }
}
```

On replay, the runner reads this, skips `validate` + `charge`, and
starts from `dispatch`. Atomic at the **stage** boundary — a stage
either completed and is checkpointed, or it didn't and will re-run.

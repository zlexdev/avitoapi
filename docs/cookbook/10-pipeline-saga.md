# Pipelines — saga (compensation rollback)

`Pipeline(..., saga=True)` opts into automatic reverse-order
compensation on stage failure. Each completed stage's `compensate_fn`
is called in reverse registration order; the original exception is
chained onto a `PipelineStageError`.

---

## Why saga

Multi-step mutations rarely have an "all or nothing" transactional
boundary across services. Saga gives you:

* explicit `compensate` per stage (the inverse of the forward action),
* automatic rollback on any forward failure,
* checkpointed compensation — a crash mid-rollback resumes from the
  next uncompensated stage,
* best-effort: a compensate that itself fails is recorded but doesn't
  block siblings.

Without saga, a failure inside `charge` leaves an unfulfilled order in
your DB and a captured payment. With saga, the captured payment is
refunded automatically.

---

## Class-based

```python
from avitoapi import BaseStage, Pipeline, RetryPolicy

pipeline = Pipeline(name="ship-order", saga=True)
ShipStage = pipeline.base_stage("ShipStage")

class Validate(ShipStage):
    name = "validate"

    async def __call__(self, event, ctx):
        ctx.workflow_data["plan"] = await checks.run(event)

    # No compensate — validate has no side effects to undo.

class Charge(ShipStage):
    name = "charge"
    retry = RetryPolicy(max_attempts=3)
    output = "charge_id"

    async def __call__(self, event, ctx) -> str:
        return await payments.capture(event.order_id)

    async def compensate(self, event, ctx):
        await payments.refund(ctx.outputs["charge_id"])

class Reserve(ShipStage):
    name = "reserve-stock"
    output = "reservation_id"

    async def __call__(self, event, ctx) -> str:
        return await warehouse.reserve(event.order_id, qty=event.quantity)

    async def compensate(self, event, ctx):
        await warehouse.release(ctx.outputs["reservation_id"])

class Dispatch(ShipStage):
    name = "dispatch"

    async def __call__(self, event, ctx):
        await carrier.create_label(event.order_id)
```

A subclass that defines `async def compensate` auto-wires it. Stages
without a `compensate` aren't rolled back (validate above) — they're
treated as side-effect-free reads.

---

## Decorator-based

```python
pipeline = Pipeline(name="ship-order", saga=True)

@pipeline.stage("validate")
async def validate(event, ctx): ...

@pipeline.stage(
    "charge",
    compensate_fn=lambda event, ctx: payments.refund(ctx.outputs["charge_id"]),
    output="charge_id",
)
async def charge(event, ctx):
    return await payments.capture(event.order_id)

@pipeline.stage(
    "reserve",
    compensate_fn=lambda event, ctx: warehouse.release(ctx.outputs["reservation_id"]),
    output="reservation_id",
)
async def reserve(event, ctx):
    return await warehouse.reserve(event.order_id, qty=event.quantity)
```

Lambda compensates work for one-liners; pull them into named coroutines
when they grow logic.

---

## Failure walk-through

Suppose `dispatch` fails after `validate`, `charge`, and `reserve`
already completed. The runner:

1. Catches the `PipelineStageError` from `dispatch`.
2. Fires `on_failure` hooks (with the original exception).
3. Sets `checkpoint.state = COMPENSATING` and persists.
4. Walks `checkpoint.completed` in reverse: `reserve` → `charge`
   → `validate`.
5. For each stage with a `compensate_fn`, calls it.
6. Marks the stage compensated in the checkpoint.
7. Sets `checkpoint.state = COMPENSATED` and persists.
8. Re-raises the original `PipelineStageError`.

Validate has no compensate — it's silently skipped (not added to
`compensated`).

---

## Crash mid-rollback

The checkpoint state survives the queue row. If the process dies after
`reserve.compensate()` but before `charge.compensate()`, the next
replay reads `state=COMPENSATING` and resumes:

```python
checkpoint = {
    "completed":   ["validate", "charge", "reserve"],
    "compensated": ["reserve"],                       # already rolled back
    "state":       "compensating",
}
```

Replay picks up at `charge.compensate()` and continues. Saga rollback
is therefore at-least-once on each `compensate_fn` — make them
idempotent (most payment / inventory APIs already are).

---

## Compensate hooks

Observe rollbacks per stage or globally:

```python
@pipeline.on_compensate("charge")
async def charge_refunded(stage, event, ctx):
    await metrics.incr("refunds.applied")

@pipeline.on_compensate()       # global — fires for every compensate call
async def any_rollback(stage, event, ctx):
    log.warning("pipeline.compensate", stage=stage.name, order=event.order_id)
```

Per-stage hooks fire before the global ones.

---

## Compensation failures

If a `compensate` itself raises, the error is logged and recorded in
`checkpoint.compensation_errors[stage_name]`, then the walk continues
with the next stage. The whole `compensation_errors` dict is persisted
into the queue metadata — ops can inspect after the fact:

```python
async def admin_inspect(message_id: str):
    meta = await queue.get_metadata(message_id)
    cp = meta.get("pipeline:ship-order", {})
    if cp.get("compensation_errors"):
        for stage, err in cp["compensation_errors"].items():
            log.error("uncompensated", stage=stage, err=err)
```

A standalone `CompensationFailed` exception is also in the public
surface — useful for pattern-matching in custom ops tooling, but the
runner itself doesn't raise it (it keeps walking by design).

---

## When NOT to saga

* **Pure read pipelines** — no side effects to undo.
* **Idempotent destructive operations** (e.g. setting a status) — replay
  on failure does the right thing, no rollback needed.
* **External steps that can't be reversed** (sending an email,
  emitting an SMS). For these, model the side effect as a *separate
  post-commit stage* so the forward path never undoes it. See pipeline
  pattern in `patterns.md` (PreStage → MainStage → PostCommitStage).

Saga earns its complexity when the forward path captures state across
multiple services (payment + inventory + shipping) and partial state
is worse than retry.

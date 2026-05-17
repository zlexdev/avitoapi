# Pipelines — DAG layout & parallel groups

By default, stages run sequentially in registration order. Two ways to
fan out:

* **`depends_on=(...)`** on each stage — the runner topologically sorts
  and runs stages with disjoint deps in parallel via `asyncio.gather`.
* **`ParallelGroup`** — a single named stage that internally fans out
  sub-callables. Simpler when the fan-out is a one-off "do these two
  side effects together" with no fork/join arrows across the whole
  pipeline.

---

## `depends_on` — explicit DAG

```python
from avitoapi import BaseStage, Pipeline

pipeline = Pipeline(name="ship-order", saga=True)
ShipStage = pipeline.base_stage("ShipStage")

class Validate(ShipStage):
    name = "validate"

    async def __call__(self, event, ctx):
        await checks.run(event)

class Charge(ShipStage):
    name = "charge"
    depends_on = ("validate",)
    output = "charge_id"

    async def __call__(self, event, ctx) -> str:
        return await payments.capture(event.order_id)

class Reserve(ShipStage):
    name = "reserve"
    depends_on = ("validate",)
    output = "reservation_id"

    async def __call__(self, event, ctx) -> str:
        return await warehouse.reserve(event.order_id, qty=event.quantity)

class Dispatch(ShipStage):
    name = "dispatch"
    depends_on = ("charge", "reserve")

    async def __call__(self, event, ctx):
        await carrier.create_label(
            event.order_id,
            charge_id=ctx.outputs["charge_id"],
            reservation_id=ctx.outputs["reservation_id"],
        )
```

Topological layout:

```
                ┌────► Charge ─────┐
   Validate ───┤                   ├──► Dispatch
                └────► Reserve ────┘
```

The runner builds layers — `[Validate]`, `[Charge, Reserve]`,
`[Dispatch]` — and `gather`s each layer. Cycles raise `ValueError` at
build time (better fail loud than mute-deadlock).

### Implicit "after previous"

Stages with `depends_on=()` implicitly depend on the **previous stage
in registration order**. This preserves the obvious sequential
semantics you expect from a plain pipeline — bare `@pipeline.stage(...)`
without deps stays serial. Mix freely:

```python
@pipeline.stage("a")    # depends_on = ()
async def a(...): ...

@pipeline.stage("b")    # implicit depends_on = ("a",)
async def b(...): ...

@pipeline.stage("c", depends_on=("a",))  # explicit — parallel with b
async def c(...): ...

@pipeline.stage("d", depends_on=("b", "c"))   # joins both
async def d(...): ...
```

---

## `ParallelGroup` — fan-out as one stage

When the fan-out is a tactical "fire these two together inside a single
logical stage", `ParallelGroup` is lighter than building DAG arrows:

```python
from avitoapi import ParallelGroup, Pipeline

pipeline = Pipeline(name="ship-order")

@pipeline.stage("validate")
async def validate(event, ctx): ...

notify = ParallelGroup(name="notify-all")
notify.add("sms", lambda e, c: sms.send(e.phone, "Order shipped."), timeout=3.0)
notify.add("email", lambda e, c: email.send(e.email, "Order shipped."))
notify.add("push", lambda e, c: push.send(e.user_id, "Order shipped."))

pipeline.stages.append(notify.as_stage(output="notify_results", depends_on=("validate",)))
```

The group fans out via `asyncio.gather`. Results land under
`ctx.outputs["notify_results"]` as `{"sms": <r>, "email": <r>, "push": <r>}`.

* The group succeeds only if **every** sub-stage succeeds.
* First raised exception cancels siblings and propagates (so saga
  compensation at the group level still works).
* Per-sub-stage compensation **isn't tracked** — the group either ran
  or it didn't. If you need granular rollback per fan-out branch, use
  `depends_on` instead.

---

## When to pick which

| Situation                                                  | Use                       |
|------------------------------------------------------------|---------------------------|
| Fan-out is part of the pipeline's main flow with arrows    | `depends_on`              |
| Need per-branch retry / timeout / saga compensate          | `depends_on`              |
| Need to inspect each branch's state in the checkpoint      | `depends_on`              |
| Tactical "fire two side effects together, treat as one"    | `ParallelGroup.as_stage`  |
| Don't care about per-branch checkpointing or compensation  | `ParallelGroup.as_stage`  |

Rule of thumb: if you'd want to retry one branch without re-running
the others, you want `depends_on`.

---

## Inspecting layers

```python
from avitoapi import stages_in_layers

layers = stages_in_layers(pipeline.stages)
for i, layer in enumerate(layers):
    print(f"layer {i}: {[s.name for s in layer]}")
```

Useful for visualising a pipeline at startup — print the layout into
your logs / docs / health endpoint so on-call can see fan-out at a
glance.

---

## Worker partition-by + DAG

A pipeline with parallel layers still runs per-event — two different
events for the same `chat_id` can race a downstream service. Pair with
`QueueWorker(partition_by=...)` ([08-queue.md](08-queue.md)) to
serialise events per key while still letting the **layers inside one
event** run concurrently:

```python
from avitoapi.queue import QueueWorker

def by_order(event) -> str | None:
    return getattr(event, "order_id", None)

worker = QueueWorker(queue, dispatcher_handler, concurrency=8, partition_by=by_order)
```

Now no two events for the same order interleave, but inside one
event's pipeline, `Charge` and `Reserve` still run in parallel.

# avitoapi.pipeline

Multi-stage pipeline handlers with resumable execution + saga rollback
+ DAG fan-out + retry/timeout/when/output policies + lifecycle hooks.

## Surface

### Core
- `Pipeline(name, *, event_filter=None, stages=[], auto_ack=True,
  saga=False, partition_by=None, hooks=PipelineHooks())`.
- `Stage(name, fn, *, compensate_fn=None, retry=None, timeout=None,
  when=None, output=None, depends_on=())`.
- `BaseStage` — inheritance-based stage registration. Class-level
  `name` / `retry` / `timeout` / `when` / `output` / `depends_on`;
  override `compensate` for saga rollback.
- `PipelineCheckpoint` — `completed`, `compensated`,
  `compensation_errors`, `state`. Persists in `ctx.queue.metadata`.

### Runner + router
- `PipelineRunner(pipeline, *, middleware_chain=None).run(event, ctx) -> bool`.
- `PipelineRouter()` — `@router.stage(pipeline_name, stage_name)` decorator
  surface; `router.bind(dispatcher)` mounts every pipeline on the
  dispatcher's outer middleware chain.

### Stage options
- **`retry: RetryPolicy`** — max attempts + backoff + retry_on filter.
- **`timeout: float`** — `asyncio.wait_for` around the stage call.
- **`when: Filter`** — predicate; `False` → skip + mark complete.
- **`output: str`** — key in `ctx.outputs` to store the stage's return.
- **`depends_on: tuple[str, ...]`** — DAG arrows. Stages sharing deps
  run concurrently inside one layer; stages without `depends_on`
  implicitly depend on the previous stage (sequential default).
- **`compensate_fn` / `BaseStage.compensate`** — saga rollback; called
  in reverse order on failure when `Pipeline(saga=True)`.

### Retry / backoff
- `RetryPolicy(max_attempts=3, backoff=ExponentialBackoff(),
  retry_on=(Exception,), give_up_on=())`.
- `Backoff` ABC + `ConstantBackoff(delay_s, jitter_pct=0.0)`,
  `ExponentialBackoff(base=0.5, multiplier=2.0, max_delay=30.0,
  jitter=True)`.
- `RetryPolicy.NONE` — singleton meaning "do not retry".

### Hooks
- `@pipeline.before_run` / `@pipeline.after_run` — fired once per run.
- `@pipeline.on_failure` — `(event, ctx, exc)` before compensation.
- `@pipeline.on_stage_start` / `on_stage_complete` / `on_stage_skipped`
  / `on_stage_failed` — `(stage, event, ctx)` per stage.
- `@pipeline.on_compensate("stage-name")` — per-stage compensate observer.
- `@pipeline.on_compensate()` — fires for every compensation call.

### Composition
- `ParallelGroup(name, members)` — sugar for fan-out as a single stage:
  members run via `asyncio.gather`. For pipeline-wide DAG fan-out
  prefer explicit `depends_on=`.

## Execution model

```
PipelineRunner.run(event, ctx)
   │
   ├─ load checkpoint from ctx.queue.metadata["pipeline:<name>"]
   ├─ pipeline.hooks.before_run.fire
   │
   │  if checkpoint.state == "compensating":
   │      resume compensate from last unfinished stage
   │      return
   │
   │  layers = _build_layers()   ← topological sort, implicit "after prev"
   │  for layer in layers:
   │      for stage in layer:
   │          if done / skipped / when=False → mark + continue
   │          execute with retry-loop wrapping timeout
   │          if output set → ctx.outputs[output] = result
   │          mark complete + persist checkpoint
   │
   ├─ checkpoint.state = "done" / "failed" / "compensated"
   ├─ hooks.after_run.fire (on success)
   │
   └─ if auto_ack and not ctx.queue.is_acked: atomic_completed()
```

## Saga / compensate

`Pipeline(saga=True)` opts into automatic rollback:

1. On any stage failure, `hooks.on_failure` fires with the original exception.
2. `checkpoint.state` flips to `"compensating"`; persisted.
3. Runner walks `checkpoint.completed` in reverse, calls
   `stage.compensate_fn(event, ctx)` for each, marks in
   `checkpoint.compensated`. Stages without compensators are skipped.
4. Compensation failures are recorded in `checkpoint.compensation_errors`
   — the walk continues, never blocks.
5. After the walk, `checkpoint.state = "compensated"`. The original
   `PipelineStageError` is re-raised with the underlying exception as
   `__cause__`.
6. If the process crashes mid-walk, the next replay sees
   `state == "compensating"` and resumes from `checkpoint.compensated`.

## DAG mode

`Stage(depends_on=("a", "b"))` declares deps. Stages whose deps are
satisfied by previous layers form the next layer. Implicit semantics:
`depends_on=()` is shorthand for "after the previously registered
stage" — preserves sequential behaviour for pipelines that didn't opt
into DAG. Cycles raise `ValueError` at runtime.

Stages in the same layer run via `asyncio.gather`; first failure
cancels siblings, triggers compensation (if saga).

## Files

- `pipeline.py` — `Pipeline`, `Stage`, `BaseStage`, `PipelineCheckpoint`,
  errors.
- `runner.py` — `PipelineRunner` + `stages_in_layers` helper.
- `router.py` — `PipelineRouter`.
- `retry.py` — `RetryPolicy`, `Backoff`, `ConstantBackoff`, `ExponentialBackoff`.
- `hooks.py` — `PipelineHooks` + hook signature aliases.
- `groups.py` — `ParallelGroup`.

## Lift-out discipline

This module imports ONLY:
- `avitoapi.events._base.Event` (minimal base)
- `avitoapi.routers.context` (EventContext, CtxQueue, CtxPipeline, HandlerType)
- `avitoapi.routers.middleware` (MiddlewareChain)
- `avitoapi.routers.observer` (Filter — just a callable)
- `avitoapi.exceptions.SDKError`
- `avitoapi.logging`

No avitoapi-specific events, no client, no methods, no dispatcher.
Lift-out to a standalone library (`zlexdev/saga` or extending
`zlexdev/evented`) is mechanical.

# avitoapi.pipeline

Thin avitoapi shim over **stagecraft** — the generic resumable
pipeline + saga library at `github.com/zlexdev/stagecraft`. The mechanics
(stage registration, runner, hooks, retry, DAG layering, saga
compensation) live in `stagecraft`; this module wires it to avitoapi's
:class:`EventContext` / :class:`MiddlewareChain` / :class:`Dispatcher`
shapes.

## Surface

The public surface is unchanged from before the lift-out — every name
re-exports from `stagecraft`:

### Core
- `Pipeline(name, *, event_filter=None, stages=[], auto_ack=True,
  saga=False, partition_by=None, hooks=PipelineHooks())` — factory
  function (accepts `auto_ack` as alias for stagecraft's
  `auto_complete`). Returns a `stagecraft.Pipeline`.
- `Stage(name, fn, *, compensate_fn=None, retry=None, timeout=None,
  when=None, output=None, depends_on=())`.
- `BaseStage` — inheritance-based stage registration.
- `PipelineCheckpoint` — `completed`, `compensated`,
  `compensation_errors`, `state`. Stored in `ctx.queue.metadata`.

### Runner + router (avitoapi-flavoured)
- `PipelineRunner(pipeline, *, middleware_chain=None).run(event, ctx) -> bool`
  — wraps `stagecraft.PipelineRunner` with the avitoapi adapters.
- `PipelineRouter` — subclass of `stagecraft.PipelineRouter` adding
  `bind(dispatcher)` for the aiogram-style outer-middleware hook.

### Stage options
- **`retry: RetryPolicy`** — max attempts + backoff + retry_on filter.
- **`timeout: float`** — `asyncio.wait_for` around the stage call.
- **`when: Filter`** — predicate; `False` → skip + mark complete.
- **`output: str`** — key in `ctx.outputs` to store the stage's return.
- **`depends_on: tuple[str, ...]`** — DAG arrows.
- **`compensate_fn` / `BaseStage.compensate`** — saga rollback.

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
- `ParallelGroup(name, members)` — fan-out sugar.

## Avitoapi adapters

Three Protocol implementations live in `_adapters.py`:

- `QueueMetadataCheckpointStore(ctx)` — implements
  `stagecraft.CheckpointStore` over `ctx.queue.metadata` +
  `ctx.queue.persist_metadata()`. Bound per-ctx (per `run()` call).
- `AvitoapiStateProvider` — implements `stagecraft.StageStateProvider`;
  returns a view that proxies `ctx.outputs` + `ctx.pipeline.*`.
- `MiddlewareChainAdapter(chain)` — implements
  `stagecraft.StageMiddleware` over avitoapi's `MiddlewareChain.wrap`.
- `completion_hook(ctx)` — module-level callable that calls
  `ctx.atomic_completed()` if the queue row hasn't been acked.

The wrapper `PipelineRunner` instantiates all four per `run()` call so
each event sees its own ctx-bound store. The wrapper `PipelineRouter`
threads them through dispatcher's `outer_middleware`.

## Execution model

```
PipelineRunner.run(event, ctx)
   │
   ├─ inner = stagecraft.PipelineRunner(
   │     pipeline,
   │     checkpoint_store=QueueMetadataCheckpointStore(ctx),
   │     state_provider=AvitoapiStateProvider(),
   │     completion_hook=completion_hook,
   │     middleware=MiddlewareChainAdapter(self.middleware_chain),
   │   )
   └─ return await inner.run(event, ctx)
```

stagecraft's runner then:

1. Loads checkpoint via `checkpoint_store.load("pipeline:<name>")`.
2. Builds execution layers from `depends_on` (topological sort).
3. For each layer: skips done / when=False / explicit-skipped stages,
   runs the rest with retry-wrapped timeout, persists checkpoint
   after each.
4. On stage failure (saga=True): walks `completed` in reverse,
   calls each `compensate_fn`, records errors. Re-raises.
5. On success: fires `completion_hook(ctx)` → `ctx.atomic_completed()`.

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

- `__init__.py` — public surface + `Pipeline(...)` factory (auto_ack alias).
- `_adapters.py` — `QueueMetadataCheckpointStore`, `AvitoapiStateProvider`,
  `MiddlewareChainAdapter`, `completion_hook`.
- `runner.py` — `PipelineRunner` wrapper.
- `router.py` — `PipelineRouter` wrapper + `bind(dispatcher)`.

## Dependency

Listed in `pyproject.toml` / `requirements.txt`:

```text
stagecraft @ git+https://${GH_TOKEN}@github.com/zlexdev/stagecraft.git@v0.1.0
```

For local dev: `pip install -e ../stagecraft` (path install).

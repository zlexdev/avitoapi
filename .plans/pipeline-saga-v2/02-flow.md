# Data flow

## Producer → Queue → Worker → Dispatcher → Pipeline

```
caller            ┌─ EventQueue ─┐                ┌─ QueueWorker ─┐                ┌─ Dispatcher ─┐                ┌─ PipelineRouter ─┐
   │              │  enqueue()    │                │  lease(N)     │                │  feed_event   │                │  outer_middleware │
   │  feed_event ─┼──► put row ───┘                │  loop *N      │                │  fan-out      │                │  iterate pipelines│
   │              │  (with run_at,                 │  ↓                              │  observers   │                │  PipelineRunner    │
   │              │   priority, attempts)          │  partition lock                 │              │                │   for each match    │
   │              │                                 │  ↓                              │              │                │                     │
   │              │                                 │  dispatcher.feed_event(ev, ctx)─►              │                │                     │
   │              │                                 │                                 │              │                │                     │
   └◄─────────────┼─────────────────────────────────┼─────────────────────────────────┼──────────────┼────────────────┘                     │
                  │                                 │                                 │                                                       │
                  │                                 │  on success: ack(lease_id)      │                                                       │
                  │                                 │  on failure: release / retry    │                                                       │
                  │                                 │  on max_attempts: → DLQ         │                                                       │
                  └─────────────────────────────────┘                                 └──────────────────────────────────────────────────────┘
```

## Pipeline run flow (with compensate)

```
PipelineRunner.run(event, ctx)
   │
   ├─ load checkpoint from ctx.queue.metadata["pipeline:<name>"]
   ├─ pipeline.hooks.before_run.fire(event, ctx)
   │
   │  for stage in self._iter_stages(checkpoint):       ← topological + depends_on layers
   │      ├─ if checkpoint.is_done(stage) or ctx.pipeline.is_skipped(stage): skip
   │      ├─ if stage.when and not stage.when(event):   ← conditional gate
   │      │      checkpoint.mark(stage) ; continue
   │      ├─ hooks.on_stage_start.fire(stage)
   │      ├─ try:
   │      │      ┌─ retry-loop (RetryPolicy)
   │      │      │   ┌─ asyncio.wait_for(handler(event, ctx), timeout=stage.timeout)
   │      │      │   │
   │      │      │   ├─ ParallelGroup: gather sub-stages
   │      │      │   └─ result → ctx.outputs[stage.output] (if output_key set)
   │      │      │
   │      │      └─ on retryable exc: backoff + retry
   │      ├─ except: hooks.on_stage_failed.fire(stage, exc)
   │      │          if pipeline.saga: → COMPENSATE
   │      │          else: raise PipelineStageError
   │      │
   │      ├─ checkpoint.mark(stage) ; persist
   │      └─ hooks.on_stage_complete.fire(stage)
   │
   ├─ pipeline.hooks.after_run.fire(event, ctx)
   └─ if auto_ack and not ctx.queue.is_acked: atomic_completed()

COMPENSATE branch:
   │
   ├─ checkpoint.state = "compensating" ; persist
   ├─ hooks.on_failure.fire(event, ctx, exc)
   │
   │  for stage_name in reversed(checkpoint.completed):
   │      if stage_name in checkpoint.compensated: continue
   │      stage = pipeline.get_stage(stage_name)
   │      if stage.compensate_fn is None: skip
   │      ├─ hooks.on_compensate[stage_name].fire(stage, event, ctx)
   │      ├─ try: await stage.compensate_fn(event, ctx)
   │      ├─ except CompensationFailed: log+continue (record in checkpoint.compensation_errors)
   │      └─ checkpoint.compensated.append(stage_name) ; persist
   │
   ├─ checkpoint.state = "compensated" ; persist
   └─ raise PipelineStageError (original exc as __cause__)
```

## DAG ordering

`Stage.depends_on: tuple[str, ...]` declares prerequisites.
`PipelineRunner` does topological sort once per call, groups stages
into "layers" where a layer = stages whose deps are fully satisfied by
prior layers. Stages in one layer run via `asyncio.gather` with
`return_exceptions=False` — first failure cancels siblings, triggers
compensate.

`ParallelGroup` is sugar: a single Stage whose `fn` is a gather of
sub-stage fns. Useful when you don't want to flatten 5 micro-stages
into the top-level pipeline.

## Partition-by

`Pipeline.partition_by: Callable[[Event], str] | None`
`QueueWorker` consults this when leasing — if the event's partition
key has an in-flight lease, the worker leaves it for the lease holder
or moves on. Implementation: per-process `dict[str, asyncio.Lock]` in
the worker; not cross-process.

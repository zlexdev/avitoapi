# pipeline-saga-v2 — 12 production features on pipeline + queue

## Goal

Bring the `avitoapi/pipeline/` + `avitoapi/persistent_queue.py` subsystem
from "MVP-grade" to "production-grade" by adding the 12 missing
orchestration features.

## Scope

1. Saga / compensating stages — backward unwind on failure
2. Visibility-timeout / lease + max-attempts → DLQ on `EventQueue`
3. JSON serializer + `EventRegistry` — replace pickle as default
4. Per-stage retry policy with `Backoff` (separate from queue.attempts)
5. Per-stage timeout (`asyncio.wait_for`)
6. Scheduled / delayed enqueue (`run_at` field + `QueueScheduler`)
7. DAG-mode (`depends_on`) + `ParallelGroup` sugar
8. Conditional stage execution (`when=Filter`)
9. `Pipeline.partition_by` — serial per-key, parallel across keys
10. Stage output binding → `ctx.outputs` namespace
11. `QueueWorker` — async consumer pool with concurrency control
12. Pipeline lifecycle hooks (`before_run`, `after_run`, `on_failure`, `on_compensate`)

## Success criteria

* All 12 features land with unit tests proving the contract.
* `mypy --strict` + `ruff` clean.
* Existing tests in `tests/unit/test_pipeline.py` + `test_persistent_queue.py` continue to pass without code changes.
* No `pickle` in the default path — `JSONSerializer` is the new default; `PickleSerializer` is kept as an opt-in legacy.
* No avitoapi-specific imports inside `avitoapi/pipeline/*` or `avitoapi/persistent_queue.py` (the lift-out boundary).

## Non-goals

* Cross-process distributed locks (partition_by is per-process only).
* Redis / Postgres-native queue backends — `EventQueue` over `BaseStorage` stays the reference impl.
* Migration from existing pickle payloads — fresh enqueues only, no auto-upgrade.
* Web / HTTP surface — unrelated.

## Lift-out discipline (future zlexdev/saga or evented)

Inside `pipeline/` and `persistent_queue.py`, allow imports ONLY from:

* `avitoapi.events._base` (`Event` — minimal base, candidate for the new lib)
* `avitoapi.routers.context` (`EventContext`, `CtxQueue`, `CtxPipeline`, `HandlerType`)
* `avitoapi.routers.middleware` (`MiddlewareChain`)
* `avitoapi.routers.observer` (`Filter` — just a callable type alias)
* `avitoapi.storage.base` (`BaseStorage`)
* `avitoapi.logging` (`get_logger`)
* `avitoapi.exceptions` (`SDKError` — will rename at lift-out)

FORBIDDEN inside these modules:

* `avitoapi.client`, `avitoapi.dispatcher`, `avitoapi.methods`
* `avitoapi.events.messenger` / `orders` / any concrete event class
* anything specific to the Avito wire protocol

This keeps the lift-out mechanical.

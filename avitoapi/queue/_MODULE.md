# avitoapi.queue

Persistent event queue + visibility leases + dead-letter handling +
scheduled enqueue + async consumer pool.

## Surface

### Contracts
- `BaseEventQueue` — ABC: `enqueue` / `lease` / `release` / `extend_lease` /
  `ack` / `replay` / `update_metadata` / `increment_attempt` / `pending_count` / `close`.
- `BaseDeadLetterQueue` — ABC: `push` / `pop_all` / `count`.
- `QueuedEvent` — dataclass: `message_id`, `event`, `enqueued_at`,
  `attempts`, `metadata`, `run_at`, `priority`, `lease: MessageLease | None`.
- `MessageLease` — dataclass: `message_id`, `lease_id`, `expires_at`,
  `is_expired(now=None)`.
- `DeadLetter` — dataclass: `message_id`, `event`, `attempts`,
  `failed_at`, `reason`, `metadata`.

### Implementations
- `EventQueue(storage, *, serializer=JSONSerializer(), namespace="events",
  visibility_timeout=60.0, max_attempts=10, dead_letter_queue=None)`.
- `MemoryDeadLetterQueue()` — in-process, lost on restart.
- `StorageDeadLetterQueue(storage, *, serializer=JSONSerializer(), namespace="dlq")`.
- `QueueScheduler(queue, on_due, *, max_sleep=30, idle_sleep=5)` —
  wake when next `run_at` is due.
- `QueueWorker(queue, handler, *, concurrency=1, poll_interval=0.5,
  visibility_timeout=None, partition_by=None, name="queue-worker")` —
  async consumer pool with per-partition serialisation.

### Serializers + registry
- `EventRegistry` — class-level singleton with `register(cls, name=, version=,
  upgrader=)`, `get(name)`, `name_for(cls)`, `version_of(name)`, `upgrade`.
- `JSONSerializer()` — default. Emits `{type, version, data}` dicts;
  reconstructs events by class name with optional version upgraders.
- `PickleSerializer()` — legacy, **unsafe with untrusted payloads**.

### Helpers
- `enqueue_later(queue, event, *, delay, metadata=None, priority=0)` —
  shortcut for `enqueue(..., run_at=time.time() + delay_s)`.
- `in_seconds(delay)` — coerce `timedelta | float | int` to seconds.

## Lifecycle

```
producer ──► queue.enqueue(event[, run_at, priority])
                  ↓
            ┌─ ready set (run_at ≤ now, no lease) ─┐
            │                                       │
worker  ◄── queue.lease(visibility_timeout=60)
            │  → QueuedEvent with .lease=MessageLease
            ↓
        handler(queued) → True | False | raises
            │
            ├─ True → queue.ack(message_id, lease_id=...)        — row deleted
            ├─ False → queue.release(message_id, lease_id)       — row free again
            └─ raise / lease expires / attempts ≥ max_attempts → DLQ
```

Attempt counter bumps on every successful `lease()`. When it would
exceed `max_attempts`, the row is moved to `dead_letter_queue` (if
configured) and removed from the index.

## Scheduled enqueue

`enqueue(event, run_at=ts)` (or `enqueue_later(..., delay=timedelta(...))`)
defers delivery until `time.time() >= ts`. `lease()` skips rows whose
`run_at` is in the future. `QueueScheduler` is a thin background loop
that fires a callback at the next due timestamp so a worker that's
polling on a long `poll_interval` doesn't miss a row.

## Partition-by

`QueueWorker(..., partition_by=lambda ev: ev.account_id)` takes a
per-partition `asyncio.Lock` around the handler call. Events with the
same key never run concurrently inside this process; events with
different keys parallelise up to `concurrency`. Cross-process
serialisation needs a distributed lock — out of scope.

## Files

- `base.py` — `BaseEventQueue`, `QueuedEvent`, `MessageLease`,
  `BaseDeadLetterQueue`, `DeadLetter`.
- `serializer.py` — `EventRegistry`, `EventSerializer`,
  `JSONSerializer`, `PickleSerializer`.
- `queue.py` — `EventQueue` (lease + max_attempts → DLQ + scheduled).
- `dlq.py` — `MemoryDeadLetterQueue`, `StorageDeadLetterQueue`.
- `scheduler.py` — `QueueScheduler`, `enqueue_later`, `in_seconds`.
- `worker.py` — `QueueWorker`, `WorkerHandler`, `PartitionExtractor`.

## Migrating from `avitoapi.persistent_queue`

`avitoapi.persistent_queue` still re-exports the public surface for
back-compat. New code should import from `avitoapi.queue` directly.

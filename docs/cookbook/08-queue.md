# Persistent event queue

Every event entering `Dispatcher.feed_event` is appended to a
`BaseEventQueue` before propagation. Handlers must call
`await ctx.atomic_completed()` to drop the row — otherwise the next
restart replays it.

---

## Default in-process queue

```python
from avitoapi import Dispatcher, EventQueue
from avitoapi.storage.memory import MemoryStorage

queue = EventQueue(MemoryStorage())
dispatcher = Dispatcher(event_queue=queue)

@dispatcher.new_message()
async def handle(event, ctx):
    await save_to_db(event)
    await ctx.atomic_completed()    # ← drop the row atomically
```

`MemoryStorage` is enough for tests. For production swap in a real
backend so events survive restart:

```python
from avitoapi.storage.redis import RedisStorage

queue = EventQueue(RedisStorage.from_url("redis://localhost:6379"))
dispatcher = Dispatcher(event_queue=queue)
```

Postgres / Mongo backends are also in-tree (`avitoapi.storage.postgres`
/ `.mongo`).

---

## Replay on startup

Drain whatever the previous run didn't ack:

```python
async def on_startup() -> None:
    replayed = await dispatcher.replay_pending()
    log.info("replayed", count=replayed)
```

Each replay increments `QueuedEvent.attempts`; handlers can read
`ctx.queue.attempts` to back off on repeated retries.

---

## `ctx.queue` — the per-event handle

| Attribute               | Meaning                                            |
|-------------------------|----------------------------------------------------|
| `message_id`            | row id in the persistent queue                     |
| `attempts`              | times this event has been (re)delivered            |
| `queued_at`             | epoch seconds when it was enqueued                 |
| `metadata`              | free-form persisted bag for handler checkpoints    |
| `atomic_completed()`    | atomically drop the row (idempotent)               |
| `persist_metadata()`    | flush `metadata` back to the row                   |
| `is_acked`, `is_bound`  | introspection flags                                |

Store auxiliary state in `metadata` if you need it to survive replay.

---

## Lease / visibility timeout

Workers pull rows via `lease` — the queue marks the row as in-flight
for `visibility_timeout` seconds. If the worker dies before acking,
the lease expires and another worker picks it up.

```python
from avitoapi.queue import EventQueue
from avitoapi.storage.memory import MemoryStorage

queue = EventQueue(
    MemoryStorage(),
    visibility_timeout=60.0,     # 60 s budget per delivery
    max_attempts=5,              # → DLQ after 5 failed leases
)
```

`extend_lease(message_id, lease_id, by=30.0)` buys more time for a
long-running handler.

---

## DLQ — dead-letter queue

When `attempts > max_attempts`, the row moves to a
`BaseDeadLetterQueue`. Two implementations ship:

```python
from avitoapi.queue import MemoryDeadLetterQueue, StorageDeadLetterQueue
from avitoapi.storage.redis import RedisStorage

# in-process (tests only — lost on restart)
dlq = MemoryDeadLetterQueue()

# persistent
dlq = StorageDeadLetterQueue(RedisStorage.from_url("redis://..."), namespace="dlq")

queue = EventQueue(RedisStorage.from_url("redis://..."), dead_letter_queue=dlq, max_attempts=5)
```

Pull letters for inspection:

```python
letters = await dlq.pop_all()
for letter in letters:
    log.error(
        "dlq.letter",
        message_id=letter.message_id,
        attempts=letter.attempts,
        reason=letter.reason,
        event_type=type(letter.event).__name__,
    )
```

Without a DLQ, max-attempt exhaustion just logs and drops the row.

---

## Worker pool — `QueueWorker`

A concurrent consumer pool. Drive a dispatcher (or any custom handler)
from the persistent queue with configurable concurrency:

```python
from avitoapi.queue import QueueWorker

async def handler(queued):
    await dispatcher._dispatch_queued(queued)
    return True                  # True = ack, False = release lease

worker = QueueWorker(
    queue,
    handler,
    concurrency=8,
    poll_interval=0.5,
    visibility_timeout=60.0,
)

await worker.start()
# ... eventually:
await worker.stop()
```

Lifecycle:

* `start()` — spawn N coroutines.
* handler raises → log + release the lease (next attempt fires
  naturally; queue counts the attempt).
* handler returns `False` → release the lease (no attempt bump).
* handler returns `True` → ack the row.
* `stop(timeout=30)` — cancel pollers, await in-flight tasks.

### Drain helper

```python
remaining = await worker.drain(timeout=30.0)
if remaining:
    log.warning("queue.not_drained", pending=remaining)
```

---

## Partition-by — per-key serialization

Avoid two events for the same chat/order running concurrently inside
one worker process:

```python
def by_chat(event) -> str | None:
    return getattr(event, "chat_id", None)

worker = QueueWorker(
    queue, handler,
    concurrency=8,
    partition_by=by_chat,
)
```

Events with the same key serialize through an `asyncio.Lock` (in-process
only). Cross-process serialisation needs a distributed lock — out of
scope; bring your own.

---

## Scheduled enqueue — `run_at` + `enqueue_later`

Delay a row's first lease:

```python
from datetime import timedelta
from avitoapi.queue import enqueue_later

await enqueue_later(queue, event, delay=timedelta(minutes=5))
# or with explicit timestamp:
import time
await queue.enqueue(event, run_at=time.time() + 300)
```

A `QueueScheduler` background loop wakes the worker when the next due
row matures (so you don't poll on tight intervals):

```python
from avitoapi.queue import QueueScheduler

scheduler = QueueScheduler(queue, on_due=lambda: log.info("scheduler.tick"))
await scheduler.start()
```

Producers can `scheduler.notify()` after a scheduled `enqueue` so the
loop doesn't sleep through an early-due row.

---

## Stats

```python
stats = await queue.stats()
# {"pending": 12, "scheduled": 3, "in_flight": 4, "dlq": 1}
```

In-flight = rows currently leased; scheduled = rows whose `run_at` is
in the future. Use these to power `/healthz` or alert on backlogs.

---

## JSON vs Pickle serializer

Default: `JSONSerializer` — `{type, version, data}`, safe for untrusted
storage, supports schema evolution via `EventRegistry`.

```python
from avitoapi.queue import EventRegistry, JSONSerializer

# Register a new event with a stable name + version
class OrderPlaced(BaseEvent, event_name="orders.placed"): ...
EventRegistry.register(OrderPlaced, version=2, upgrader=lambda d: {**d, "currency": d.get("currency", "RUB")})

queue = EventQueue(storage, serializer=JSONSerializer())
```

Legacy fallback: `PickleSerializer` — base64-pickle for events that
won't round-trip via kwargs. **Never** feed pickle untrusted storage —
it's RCE-shaped.

---

## Manual control

For testing or custom worker shapes, drive the queue directly:

```python
# enqueue
record = await queue.enqueue(event, metadata={"source": "webhook"})

# lease
queued = await queue.lease(visibility_timeout=30.0)

# extend
await queue.extend_lease(queued.message_id, queued.lease.lease_id, by=30.0)

# ack
await queue.ack(queued.message_id, lease_id=queued.lease.lease_id)

# release (without bumping attempts)
await queue.release(queued.message_id, queued.lease.lease_id)
```

`Dispatcher._dispatch_queued` does all of this for you — direct API
calls are usually for tests or for custom consumer topologies.

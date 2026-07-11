# queue/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

> Persistent event queue with at-least-once delivery + lease semantics.

## __init__.py
```
# Persistent event queue with at-least-once delivery + lease semantics.


```

## base.py
```
# Base contracts: ``BaseEventQueue``, ``QueuedEvent``, ``MessageLease``, ``BaseDeadLetterQueue``.


cls MessageLease: message_id: str, lease_id: str, expires_at: float

cls QueuedEvent: message_id: str, event: Event, enqueued_at: float, attempts: int, metadata: JsonObject, run_at: float | None, priority: int, lease: MessageLease | None

cls BaseEventQueue(ABC)
  async enqueue(event: Event) -> QueuedEvent
  async lease() -> QueuedEvent | None
  async release(message_id: str, lease_id: str) -> bool
  async extend_lease(message_id: str, lease_id: str) -> bool
  async ack(message_id: str) -> bool
  replay() -> AsyncIterator[QueuedEvent]
  async update_metadata(message_id: str, metadata: JsonObject) -> bool
  async increment_attempt(message_id: str) -> int
  async pending_count() -> int
  async close() -> None
    # Optional teardown hook. Idempotent.

cls DeadLetter: message_id: str, event: Event, attempts: int, failed_at: float, reason: str, metadata: JsonObject
  # One row in the dead-letter queue.

cls BaseDeadLetterQueue(ABC)
  async push(letter: DeadLetter) -> None
  async pop_all() -> list[DeadLetter]
  async count() -> int

```

## dlq.py
```
# Dead-letter queue implementations.

_INDEX_KEY = '__index__'

cls MemoryDeadLetterQueue(BaseDeadLetterQueue)
  # In-process DLQ — keeps letters in a list. Lost on restart.
  __init__() -> None
  async push(letter: DeadLetter) -> None
  async pop_all() -> list[DeadLetter]
  async count() -> int

cls StorageDeadLetterQueue(BaseDeadLetterQueue)
  __init__(storage: BaseStorage[object, str) -> None
  async push(letter: DeadLetter) -> None
  async pop_all() -> list[DeadLetter]
  async count() -> int

```

## queue.py
```
# Storage-backed ``EventQueue`` with at-least-once delivery + visibility leases.

_INDEX_KEY = '__index__'
_DEFAULT_VISIBILITY_TIMEOUT = 60.0
_DEFAULT_MAX_ATTEMPTS = 10

cls EventQueue(BaseEventQueue)
  __init__(storage: BaseStorage[object, str) -> None
  async enqueue(event: Event) -> QueuedEvent
  async lease() -> QueuedEvent | None
  async release(message_id: str, lease_id: str) -> bool
  async extend_lease(message_id: str, lease_id: str) -> bool
  async ack(message_id: str) -> bool
  async replay() -> AsyncIterator[QueuedEvent]
  async update_metadata(message_id: str, metadata: JsonObject) -> bool
  async increment_attempt(message_id: str) -> int
  async pending_count() -> int
  async in_flight_count() -> int
    # Number of rows currently holding an unexpired lease.
  async stats() -> dict[str, int]

```

## scheduler.py
```
# ``QueueScheduler`` — wake a callback when the next scheduled row is due.


cls QueueScheduler
  __init__(queue: EventQueue, on_due: Callable[[], Awaitable[None]?) -> None
  async start() -> None
    # Start the background loop. Idempotent.
  async stop() -> None
    # Cancel the loop and await its completion.
  notify() -> None

in_seconds(td: timedelta | float | int) -> float
  # Coerce a duration to seconds. Convenience for ``enqueue_later`` callers.

async enqueue_later(queue: EventQueue, event: Event) -> QueuedEvent
  # Convenience wrapper around :meth:`EventQueue.enqueue` with relative delay.

```

## serializer.py
```
# Serializers + ``EventRegistry`` for safe queue payloads.


cls EventSerializer(ABC)
  # Convert :class:`Event` instances to/from a JSON-friendly form for storage.
  dump(event: Event) -> JSONValue
  load(payload: JSONValue) -> Event

cls EventRegistrationError(ValueError)
  # Raised on conflicting or unknown event registrations.

cls EventRegistry
  register(event_class: type[Event) -> type[Event]
  name_for(event_class: type[Event) -> str
    # Return the registered string id for ``event_class``.
  get(name: str) -> type[Event] | None
    # Lookup the class registered under ``name``. ``None`` when absent.
  version_of(name: str) -> int
  upgrade(name: str, data: JsonObject, from_version: int) -> JsonObject
    # Walk the upgrader chain from ``from_version`` up to the current version.
  clear() -> None
    # Reset the registry. Intended for tests only.

cls JSONSerializer(EventSerializer)
  __init__() -> None
  dump(event: Event) -> JsonObject
  load(payload: JSONValue) -> Event

cls PickleSerializer(EventSerializer)
  dump(event: Event) -> str
  load(payload: JSONValue) -> Event

_event_to_dict(event: Event) -> JsonObject

_auto_register_known_events() -> None

```

## worker.py
```
# ``QueueWorker`` — concurrent consumer pool driving a dispatcher.


cls QueueWorker
  __init__(queue: BaseEventQueue, handler: WorkerHandler) -> None
  async start() -> None
    # Spawn ``concurrency`` worker coroutines. Idempotent.
  async stop() -> None
    # Stop polling and await in-flight tasks. Idempotent.
  is_running() -> bool
  async drain() -> int

```

# idempotency/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

> Accept-once idempotency: :class:`IdempotencyStore` + event-level :class:`DedupFilter`.

## filter.py
```
# ``DedupFilter`` — event-level adapter over :class:`IdempotencyStore`.


cls DedupFilter
  # Accept-once over events, keyed by :attr:`Event.dedup_key` (overridable).
  __init__(store: IdempotencyStore) -> None
  async reserve(event: Event) -> bool
    # ``True`` if this event is newly claimed, ``False`` if a duplicate.
  async commit(event: Event) -> None
  async release(event: Event) -> None

_default_key(event: Event) -> str

```

## store.py
```
# ``IdempotencyStore`` — reserve / commit / release over a :class:`BaseStorage`.

_INFLIGHT = 'inflight'
_DONE = 'done'

cls IdempotencyStore
  __init__(storage: BaseStorage[object, str) -> None
  async reserve(key: str) -> bool
    # Atomically claim ``key``. ``True`` if newly claimed, ``False`` if already known.
  async commit(key: str) -> None
    # Mark ``key`` done — extend to the long retention TTL so redeliveries dedup.
  async release(key: str) -> None
    # Drop the reservation so a failed event can be retried and reprocessed.
  async seen(key: str) -> bool
    # Read-only probe — ``True`` if the key is reserved or committed.

```

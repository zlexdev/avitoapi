# storage/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

> Generic K/V storage layer. See ``_MODULE.md`` for the contract.

## __init__.py
```
# Generic K/V storage layer. See ``_MODULE.md`` for the contract.


```

## base.py
```
# Generic async key/value storage contract used everywhere (tokens, FSM, idempotency).


cls BaseStorage(ABC, Generic[TDoc, TId])
  async get(key: str) -> TDoc | None
    # Return the JSON-decoded value or ``None`` if absent or expired.
  async put(key: str, value: TDoc) -> None
    # Store the value, JSON-encoding it. ``ttl=None`` means persist indefinitely.
  async delete(key: str) -> None
    # Remove the key. No-op when absent.
  async exists(key: str) -> bool
    # Cheap probe — defaults to ``get(...) is not None`` for backends without EXISTS.
  async add(key: str, value: TDoc) -> bool
  async health() -> bool
    # Round-trip a sentinel key. Override for backends with a cheaper liveness probe.
  async close() -> None
    # Release resources. Idempotent.
  namespaced(namespace: str) -> BaseStorage[TDoc, TId]

```

## memory.py
```
# In-process :class:`BaseStorage` backed by a dict. Default for tests and single-process apps.


cls _Entry: value: object, expires_at: float | None

cls MemoryStorage(BaseStorage[object, str])
  __init__() -> None
  async get(key: str) -> object | None
  async put(key: str, value: object) -> None
  async add(key: str, value: object) -> bool
    # Atomic set-if-absent under the shared lock (all namespaced views share it).
  async delete(key: str) -> None
  namespaced(namespace: str) -> MemoryStorage

```

## mongo.py
```
# ``MongoStorage`` — :class:`BaseStorage` over ``motor.motor_asyncio`` (lazy import).


cls MongoStorage(BaseStorage[object, str])
  __init__(client: AsyncIOMotorClient[dict[str, Any]]? = None) -> None
  async get(key: str) -> object | None
  async put(key: str, value: object) -> None
  async add(key: str, value: object) -> bool
  async delete(key: str) -> None
  async close() -> None
  namespaced(namespace: str) -> MongoStorage

```

## postgres.py
```
# ``PostgresStorage`` — :class:`BaseStorage` over ``asyncpg`` (lazy import).

_IDENT_RE = re.compile('[A-Za-z_][A-Za-z0-9_]*')
_TABLE_DDL = …

cls PostgresStorage(BaseStorage[object, str])
  __init__(pool: Pool? = None) -> None
  async get(key: str) -> object | None
  async put(key: str, value: object) -> None
  async add(key: str, value: object) -> bool
  async delete(key: str) -> None
  async exists(key: str) -> bool
  async health() -> bool
  async close() -> None
  namespaced(namespace: str) -> PostgresStorage

```

## redis.py
```
# ``RedisStorage`` — :class:`BaseStorage` over ``redis.asyncio`` (lazy import).


cls RedisStorage(BaseStorage[object, str])
  __init__(client: Redis? = None) -> None
  async get(key: str) -> object | None
  async put(key: str, value: object) -> None
  async add(key: str, value: object) -> bool
    # Atomic set-if-absent via native ``SET ... NX`` — cross-process safe.
  async delete(key: str) -> None
  async exists(key: str) -> bool
  async close() -> None
  namespaced(namespace: str) -> RedisStorage

```

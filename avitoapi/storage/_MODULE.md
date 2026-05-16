# storage/

Generic async K/V store. Used for OAuth tokens, FSM state, paginator cursors,
idempotency keys, webhook dedup sets.

## Contract

- `BaseStorage[TDoc, TId]` — abstract; subclasses implement `get`, `put`,
  `delete`, and `namespaced(name)`.
- Values are JSON-friendly (`save(key, value)` JSON-encodes with
  `default=str` so `Decimal`/`datetime`/`UUID` round-trip).
- `ttl` is best-effort. Backends with no native TTL (in-memory) store the
  expiry inline and prune on read.
- `namespaced(name)` returns a view that prefixes every key with
  `<name>:`. Composes: `ns("a").ns("b")` keys land as `a:b:<key>`.

## Backends

- `MemoryStorage` — default. Deep-copies on `put` and `get` to prevent
  caller-side mutation of stored documents. Thread-safe via `asyncio.Lock`.
- `RedisStorage` — `[redis]` extra. Lazy `redis.asyncio` import. JSON
  values; `PEXPIRE` for TTL. Pass either `client=Redis(...)` (shared) or
  `url="redis://..."` (owns its client and closes on `close()`).
  `namespaced()` produces a view sharing the underlying client; only the
  owner's `close()` actually shuts the connection.
- `MongoStorage` — `[mongo]` extra. Lazy `motor.motor_asyncio` import.
  One doc per key: `{"_id": full_key, "value": <jsonable>, "expires_at":
  <datetime|None>}`. TTL via a Mongo TTL index on `expires_at` plus a
  read-side `now()` guard so writes are visibly expired before the
  background sweeper runs. Configurable `database` and `collection`.

## Don'ts

- Don't pass `bytes` — JSON can't encode it.
- Don't share one storage namespace across multiple `Client` instances in
  SaaS deployments; each account gets its own namespace.
- Don't hardcode cookie shapes inside storage — the session layer owns
  cookie serialisation; storage just sees the dict.

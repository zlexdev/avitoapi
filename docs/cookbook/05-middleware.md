# Middlewares — outer vs inner

Routers expose two middleware chains:

* **outer** — runs **once per router visit**, around predicate
  evaluation. Use for: per-event setup (tracing, FSM context build,
  auth binding), enrichment, blanket short-circuits.
* **inner** — wraps **each individual handler call**. Use for: per-
  handler retry, idempotency, rate limit, audit logging that needs the
  matched handler name.

Both implement the same `BaseMiddleware` contract.

---

## Writing a middleware

```python
from avitoapi import BaseMiddleware

class TracingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, ctx):
        ctx.workflow_data["trace_id"] = str(uuid.uuid4())
        log.info("event.in", event=type(event).__name__, trace=ctx.workflow_data["trace_id"])
        try:
            return await handler(event, ctx)
        finally:
            log.info("event.out", event=type(event).__name__)

dispatcher.outer_middleware.register(TracingMiddleware())
```

`handler` is the next link in the chain. Skip the call to short-circuit
(rate-limited, banned, duplicate). Always wrap call sites in `try/finally`
when you mutate `ctx` so a downstream failure still cleans up.

---

## Outer chain — request-shaped concerns

### FSM binding

```python
from avitoapi import BaseMiddleware
from avitoapi.fsm import AvitoStorageKeyBuilder, FSMContext, MemoryFSMStorage

class FSMMiddleware(BaseMiddleware):
    def __init__(self, storage):
        self._storage = storage
        self._kb = AvitoStorageKeyBuilder()

    async def __call__(self, handler, event, ctx):
        key = self._kb.build(event.account_id, getattr(event, "chat_id", ""))
        ctx.workflow_data["fsm"] = FSMContext(self._storage, key)
        return await handler(event, ctx)

dispatcher.outer_middleware.register(FSMMiddleware(MemoryFSMStorage()))
```

Handlers grab the context with `ctx.workflow_data["fsm"]` —
see [06-fsm.md](06-fsm.md) for usage.

### Auth / account binding

```python
class AccountClientMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, ctx):
        client = ctx.dispatcher.accounts.get(event.account_id)
        if client is None:
            log.warning("unknown_account", account_id=event.account_id)
            return None
        ctx.workflow_data["client"] = client
        return await handler(event, ctx)
```

Sets `ctx.workflow_data["client"]` so handlers skip the dict lookup.
Short-circuits with `return None` when the account is gone (deleted
seller, stale webhook).

---

## Inner chain — per-handler concerns

### Per-handler retry

```python
class RetryMiddleware(BaseMiddleware):
    def __init__(self, attempts: int = 3, delay_s: float = 0.5):
        self._attempts = attempts
        self._delay_s = delay_s

    async def __call__(self, handler, event, ctx):
        last = None
        for attempt in range(1, self._attempts + 1):
            try:
                return await handler(event, ctx)
            except (TimeoutError, ConnectionError) as exc:
                last = exc
                log.warning("handler.retry", attempt=attempt, error=str(exc))
                await asyncio.sleep(self._delay_s * attempt)
        raise last

dispatcher.inner_middleware.register(RetryMiddleware())
```

Retries the **handler call** — the queue still sees one delivery. For
queue-level retries with backoff + DLQ, see [08-queue.md](08-queue.md).

### Idempotency

```python
class IdempotencyMiddleware(BaseMiddleware):
    def __init__(self, store):
        self._store = store

    async def __call__(self, handler, event, ctx):
        key = getattr(event, "message_id", None) or ctx.queue.message_id
        if not key:
            return await handler(event, ctx)
        if await self._store.seen(key):
            log.info("handler.dedup", key=key)
            return None
        return await handler(event, ctx)
```

Backed by `dispatcher.idempotency_storage` (default in-process — swap
for Redis in production).

---

## Order matters

Middlewares fire **outer → inner → handler**, then unwind in reverse.
Within a single chain, registrations earlier in the code run earlier on
the way in and later on the way out (classic onion).

```python
dispatcher.outer_middleware.register(TracingMiddleware())   # 1st in, last out
dispatcher.outer_middleware.register(FSMMiddleware(...))    # 2nd in, 2nd-last out
dispatcher.outer_middleware.register(AccountClientMiddleware())  # 3rd in, 3rd-last out
```

Trace covers everything; FSM is bound before any handler logic; account
lookup is the last gate. If you need a strict order, register in one
place rather than scattering registrations across plugins.

---

## Per-router scoping

Middlewares attach to a specific router — sub-routers do **not**
inherit their parent's chain. Useful for plugin-local concerns:

```python
admin_router = Router(name="admin")
admin_router.outer_middleware.register(RequireAdminRoleMiddleware())

dispatcher.include_router(admin_router)
```

Only events propagated **inside** `admin_router` see its middleware;
the rest of the tree is unaffected.

---

## Decorator form

`MiddlewareChain` is also callable as a decorator:

```python
@dispatcher.outer_middleware
class LogMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, ctx):
        log.info("event", kind=type(event).__name__)
        return await handler(event, ctx)
```

Equivalent to `dispatcher.outer_middleware.register(LogMiddleware())`.
Pick the form that reads better in context.

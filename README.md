# avitoapi

Aiogram-style async Python SDK over the Avito Partner API.

In-tree dispatcher / router / middleware / FSM / circuit-breaker — no
external runtime deps beyond `pydantic`, `pydantic-settings`, `curl_cffi`,
`structlog`, `email-validator`.

Specs and design decisions live in `.plans/avito-sdk-framework/`.

Hands-on recipes — install, multi-account, routing, pipelines, sagas,
webhooks (aiohttp / FastAPI / Litestar / Sanic), proxy rotation — live
in [`docs/cookbook/`](docs/cookbook/README.md).

---

## Quickstart

```bash
uv pip install -e .[dev]
cp .env.example .env
# fill in AVITO_CLIENT_ID, AVITO_CLIENT_SECRET
```

```python
import asyncio
from avitoapi import Client, ClientConfig

async def main() -> None:
    async with Client(config=ClientConfig.from_env()) as client:
        me = await client.get_self()
        print(me.id, me.name)

asyncio.run(main())
```

---

## Client API examples

### Items + pagination

```python
async with Client(config=ClientConfig.from_env()) as client:
    # paginate everything in one expression
    async for item in client.list_items(status=ItemStatus.ACTIVE):
        print(item.id, item.title, item.price)

    # one-off lookup
    item = await client.get_item(item_id=12345)

    # apply VAS (idempotent — auto Idempotency-Key)
    await client.apply_vas([item.id], slug="highlight")
```

### Orders + state-machine guarded transitions

```python
order = await client.get_order("o-42")
await client.change_order_status(
    "o-42",
    OrderStatus.CONFIRMED,
    current=order.status,       # raises InvalidStateTransition on illegal jump
    strict=True,
)
```

### Messenger + send a chat reply

```python
async for chat in client.list_chats(unread_only=True):
    await client.send_text_message(chat.id, "Hi! Thanks for your interest.")
```

### Multi-account dispatcher

`ClientConfig` is a plain Pydantic model — build one per seller from
whatever your tenant store gives you (DB row, vault secret, admin form).
`client_id` / `client_secret` come from your Avito OAuth integration;
`user_id` scopes the token cache so each seller's tokens stay separate.
`account_id` is the routing label `Dispatcher` matches against
`event.account_id`.

```python
from avitoapi import Client, ClientConfig, make_dispatcher

# Pretend this comes from your DB / secrets manager.
SELLERS = [
    {"account_id": "alice", "user_id": 12345,
     "client_id": "int-abc", "client_secret": "shhh-a"},
    {"account_id": "bob",   "user_id": 67890,
     "client_id": "int-abc", "client_secret": "shhh-b"},
]


def build_client(row: dict) -> Client:
    config = ClientConfig(
        client_id=row["client_id"],
        client_secret=row["client_secret"],
        user_id=row["user_id"],
        rate_limit_global_rps=8.0,      # tune per-account at construction
    )
    return Client(config=config, account_id=row["account_id"])


dispatcher = make_dispatcher(accounts=[build_client(row) for row in SELLERS])

@dispatcher.new_message()
async def on_message(event, ctx):
    client = ctx.dispatcher.accounts[event.account_id]
    await client.send_text_message(event.chat_id, "echo: " + event.message.text)

await dispatcher.feed_event(some_inbound_event)

# Dynamic add / remove — the registry is just a dict:
dispatcher.accounts["carol"] = build_client(new_seller_row)
del dispatcher.accounts["bob"]
```

Pass `storage=`, `session=`, or `transport=` to `Client(...)` to share
infra across accounts (one connection pool, one Redis backend) while
keeping per-account `ClientConfig` distinct.

---

## Proxy support

The session funnel acquires a proxy per attempt via a `BaseProxyTransport`.
Three backends ship in-tree.

### Direct connection (default)

```python
from avitoapi import Client, NoProxyTransport
client = Client(config=ClientConfig.from_env(), transport=NoProxyTransport())
```

### List-based rotation with cumulative ban

```python
from avitoapi import ListProxyTransport, RotationStrategy

transport = ListProxyTransport(
    [
        "http://user:pass@1.2.3.4:8080",       # full URL
        "5.6.7.8:8080",                         # host:port, scheme defaults to http
        "9.9.9.9:8080:bob:secret",              # legacy host:port:user:pass
        "user:pass@10.0.0.1:8080",              # user:pass@host:port
        {"host": "11.0.0.1", "port": 8080,      # dict shape
         "user": "u", "password": "p"},
    ],
    strategy=RotationStrategy.ROUND_ROBIN,       # or RANDOM / STICKY
    max_failures=3,                              # 3 errors → ban
    cooldown_s=300,                              # reactivate after 5 min
    raise_on_ban=True,                           # surface ProxyBanned on threshold
)

client = Client(config=ClientConfig.from_env(), transport=transport)
```

`ListProxyTransport` keeps per-proxy `failure_count` / `banned` state.
After three consecutive `mark_invalid()` calls (TLS error, 407, dropped
connection, etc.) the proxy is banned and a `ProxyBanned` exception is
raised from the failing request — the funnel automatically rotates to
another healthy proxy on retry. If every proxy is banned: `ProxyExhausted`.

You can also parse a multi-line proxy file:

```python
from avitoapi import parse_proxy_list

proxies = parse_proxy_list(
    """
    # comments are skipped
    1.2.3.4:8080
    socks5://5.6.7.8:1080
    user:pass@10.0.0.1:8080
    """,
    skip_invalid=True,
)
transport = ListProxyTransport(proxies)
```

### Callback-driven rotation

When the rotation logic isn't a static list (warming a pool, querying a
third-party rotator, sticky-per-region) plug a callback in:

```python
from avitoapi import KEEP, CallbackProxyTransport, ProxyContext

POOL = ["1.2.3.4:8080", "5.6.7.8:8080", "9.9.9.9:8080"]
cursor = 0

def get_next_proxy(ctx: ProxyContext):
    global cursor
    # Stay on the current proxy until it errors out.
    if ctx.reason == "acquire" and ctx.current is not None:
        return KEEP
    proxy = POOL[cursor % len(POOL)]
    cursor += 1
    return proxy

transport = CallbackProxyTransport(get_next_proxy)
```

The callback receives a rich `ProxyContext`:

| Field             | Meaning                                       |
|-------------------|-----------------------------------------------|
| `reason`          | `"acquire"` or `"error"`                      |
| `current`         | proxy the funnel last used (or `None`)        |
| `total_requests`  | acquire calls served                          |
| `total_errors`    | cumulative invalidations                      |
| `current_errors`  | invalidations of the active proxy             |
| `last_error`      | the latest `ProxyError` (if any)              |
| `last_error_at`   | monotonic seconds of the last failure         |
| `account_id`      | what the funnel passed to `acquire`           |
| `host`            | target host                                   |
| `stats`           | per-proxy `(requests, errors)` snapshot       |

Return `KEEP` to keep the current proxy; return `None` for a direct
connection; return any parsable proxy spec (string / dict / `Proxy`) to
switch.

### Validating a pool before use

```python
from avitoapi import ProxyValidator

validator = ProxyValidator(check_url="https://api.avito.ru/", timeout_s=5)
results = await validator.validate_many(
    ["1.2.3.4:8080", "5.6.7.8:8080", "broken:1"],
)

healthy = [r.proxy for r in results if r.ok]
broken  = [(r.proxy, r.error) for r in results if not r.ok]
```

### Proxy-aware middlewares

Install on the session for harder retry / error-classification semantics:

```python
from avitoapi import ProxyErrorMiddleware, RetryMiddleware

client.request_middlewares.register(ProxyErrorMiddleware())   # late-stage error mapping
client.request_middlewares.register(RetryMiddleware(           # outer retry layer
    max_retries=3,
    initial_s=0.25,
    max_s=5.0,
))
```

`ProxyErrorMiddleware` translates generic `TransportError` into specific
`ProxyConnectionError` / `ProxyTimeoutError` / `ProxyTLSError` when a
proxy is bound, and marks the proxy invalid through the acquire context
so rotators advance their failure tally.

`RetryMiddleware` catches `ProxyError` (any subclass) and retries the
request through the funnel — since each retry triggers a fresh proxy
acquire, the request rotates away from the failing proxy automatically.
`ProxyExhausted` is treated as a hard give-up signal.

### Custom proxy exceptions

Catch the specific failure mode you care about:

```python
from avitoapi import (
    ProxyAuthError, ProxyBanned, ProxyConnectionError,
    ProxyError, ProxyExhausted, ProxyTimeoutError, ProxyTLSError,
)

try:
    await client.get_self()
except ProxyBanned as exc:
    log.warning("proxy banned", url=exc.proxy_url, count=exc.failure_count)
except ProxyExhausted:
    log.error("every proxy exhausted; pausing the worker")
except ProxyError as exc:           # catch-all
    log.error("proxy failure", url=exc.proxy_url, detail=exc.detail)
```

Inheritance: every `ProxyError` is a `TransportError` is an `SDKError`.

---

## Persistent event queue + atomic ack

Every event entering the `Dispatcher` is persisted to a queue. Handlers
must call `await ctx.atomic_completed()` to drop the event. Without that
call, the next startup replays the event via `dispatcher.replay_pending()`.
The queue itself does not implement storage — it composes any
`BaseStorage` instance.

```python
from avitoapi import Dispatcher, EventQueue
from avitoapi.storage.memory import MemoryStorage

queue = EventQueue(MemoryStorage())
dispatcher = Dispatcher(event_queue=queue)

@dispatcher.new_message()
async def handle(event, ctx):
    await save_to_db(event)
    await ctx.atomic_completed()      # ← atomically drop from the queue

# at startup, drain anything left over from the previous run:
await dispatcher.replay_pending()
```

The handler's `ctx.queue` is a typed `CtxQueue`:

| Attribute            | Meaning                                       |
|----------------------|-----------------------------------------------|
| `message_id`         | row id in the persistent queue                |
| `attempts`           | how many times the event was (re)delivered    |
| `queued_at`          | epoch seconds when it landed in the queue     |
| `metadata`           | free-form persisted bag (pipelines use it)    |
| `atomic_completed()` | atomically drop the event                     |
| `persist_metadata()` | flush `metadata` back to the queue row        |
| `is_acked` / `is_bound` | introspection flags                        |

---

## Pipelines — resumable multi-stage handlers

```python
from avitoapi import Pipeline, PipelineRouter, F

router = PipelineRouter()

@router.stage("ship-order", "validate")
async def validate(event, ctx):
    ctx.workflow_data["validated"] = await checks.run(event)

@router.stage("ship-order", "charge")
async def charge(event, ctx):
    await payments.capture(event.order_id)

@router.stage("ship-order", "dispatch")
async def dispatch(event, ctx):
    await warehouse.dispatch(event.order_id)

router.bind(dispatcher)
```

The router subscribes to the dispatcher; every event runs through every
matching pipeline. After each stage completes, the queue metadata is
updated atomically. If the process dies between stages — say `charge`
captured but `dispatch` never started — the next replay skips `validate`
and `charge` and resumes from `dispatch`.

`ctx.handler_type` is `HandlerType.HANDLER` inside a plain
`@router.observer` callback and `HandlerType.PIPELINE` while a pipeline
runs.

You can also gate a pipeline with a filter — pipelines accept the same
`(event, ctx)` shape as regular handlers, so any filter that works on
observers works here:

```python
pipeline = Pipeline(
    name="refund",
    event_filter=F.func(lambda ev: isinstance(ev, OrderRefunded)),
)

@pipeline.stage("notify-customer")
async def notify(event, ctx): ...

@pipeline.stage("post-back-funds")
async def repay(event, ctx): ...
```

Errors abort the pipeline and re-queue (no ack) so the next replay tries
again from the failed stage. Successful runs ack automatically — set
`Pipeline(..., auto_ack=False)` to take manual control.

---

## Filters

The aiogram-style magic filter `F` is the standard predicate builder:

```python
from avitoapi import F

@router.new_message(F.message.type == "text")
async def text(event, ctx): ...

@router.order_created(F.amount > 100_000)
async def big_order(event, ctx): ...

# combine
@router.new_message((F.message.type == "text") & ~F.message.text.contains("spam"))
async def clean_text(event, ctx): ...

# typed enums
@router.order_status_changed(F.status.in_({OrderStatus.SHIPPED, OrderStatus.DELIVERED}))
async def shipped(event, ctx): ...
```

---

## Middlewares

`Router` exposes `outer_middleware` (per-event) and `inner_middleware`
(per-handler-call) chains:

```python
from avitoapi import BaseMiddleware

class TracingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, ctx):
        log.info("event.in", event=type(event).__name__)
        try:
            return await handler(event, ctx)
        finally:
            log.info("event.out", event=type(event).__name__)

dispatcher.outer_middleware.register(TracingMiddleware())
```

Request-side middlewares live on the session funnel — same shape, but
they wrap one HTTP request:

```python
client.request_middlewares.register(ProxyErrorMiddleware())
client.request_middlewares.register(RetryMiddleware(max_retries=2))
```

---

## Custom session backend

```python
from avitoapi.sessions.base import BaseSession
from avitoapi.sessions._models import PreparedRequest, RawResponse

class MyBackend(BaseSession):
    async def _send(self, prepared: PreparedRequest) -> RawResponse:
        # build the wire request from prepared and return RawResponse
        ...

client = Client(config=ClientConfig.from_env(), session=MyBackend(config=cfg))
```

Subclasses only implement `_send` — the funnel (retries, status mapping,
proxy acquisition, middlewares, breaker) is fully inherited.

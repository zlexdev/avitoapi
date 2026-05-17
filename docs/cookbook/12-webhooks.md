# Webhooks — 4 backend HTTP servers

`avitoapi.web` exposes `Webhook` / `WebhookConfig` (framework-agnostic)
plus four backend runners — `aiohttp`, `fastapi`, `litestar`, `sanic`.
Every backend is **lazy-loaded** — importing `avitoapi.web` never
pulls a transitive HTTP framework.

The bare `WebApp` / `WebhookRunner` names alias **aiohttp** (no extra
dep).

---

## Minimal aiohttp setup

```python
from avitoapi import Dispatcher, make_dispatcher
from avitoapi.web import (
    AvitoWebhookHandler,
    Webhook,
    WebhookConfig,
    WebhookRunner,           # aiohttp alias
)

dispatcher: Dispatcher = make_dispatcher(accounts=[...])

webhook = AvitoWebhookHandler(dispatcher, mount_path="/messenger")
config = WebhookConfig(
    host="0.0.0.0",
    port=8080,
    webhooks=[Webhook(path=webhook.mount_path, handler=webhook.handle)],
)

runner = WebhookRunner(config)
await runner.start()           # blocks the loop with serving task
# ... eventually:
await runner.stop()
```

`AvitoWebhookHandler` parses the Avito envelope into typed
`NewMessage` / `MessageRead` / `ChatArchived` events and feeds them
into the dispatcher.

---

## Switching backend

Same `WebhookConfig`, swap the runner. All four runners share the
`BaseWebhookRunner` contract.

### FastAPI (extra: `pip install -e .[fastapi]`)

```python
from avitoapi.web import FastAPIWebhookRunner

runner = FastAPIWebhookRunner(config)
await runner.start()
```

Drives `uvicorn.Server` programmatically — `start()` returns when the
server is up; `stop()` flips `should_exit` and awaits the serve task.

### Litestar (extra: `pip install -e .[litestar]`)

```python
from avitoapi.web import LitestarWebhookRunner

runner = LitestarWebhookRunner(config)
await runner.start()
```

Routes register lazily — register every `Webhook` **before** calling
`start()`. After `start()`, the `Litestar` app is materialised and
further registrations raise.

### Sanic (extra: `pip install -e .[sanic]`)

```python
from avitoapi.web import SanicWebhookRunner

runner = SanicWebhookRunner(config)
await runner.start()
```

Uses `Sanic.create_server` to live inside the running event loop
(avoids `Sanic.run` which manages its own).

---

## Multiple webhooks on one server

```python
from avitoapi.web import AvitoWebhookHandler, Webhook, WebhookConfig

messenger = AvitoWebhookHandler(dispatcher, mount_path="/messenger")
orders = AvitoWebhookHandler(dispatcher, mount_path="/orders")
calls = AvitoWebhookHandler(dispatcher, mount_path="/calls")

config = WebhookConfig(
    host="0.0.0.0",
    port=8080,
    webhooks=[
        Webhook(path=messenger.mount_path, handler=messenger.handle),
        Webhook(path=orders.mount_path, handler=orders.handle),
        Webhook(path=calls.mount_path, handler=calls.handle),
    ],
)
```

Each `Webhook.handler` is a `Callable[[dict], Awaitable[(int, dict)]]`
— you can also drop in a custom handler instead of `AvitoWebhookHandler`
for non-Avito payloads.

---

## HMAC signature verification

Avito signs each delivery with the per-webhook secret. Verify before
processing:

```python
from avitoapi.web.middlewares import HMACSignatureMiddleware, SecretProvider

async def get_secret(webhook_id: str) -> str | None:
    row = await db.fetchrow("SELECT secret FROM webhooks WHERE id = $1", webhook_id)
    return row["secret"] if row else None

verifier = HMACSignatureMiddleware(get_secret, require_signature=True)

async def secure_handler(body: dict) -> tuple[int, dict]:
    # Pull the raw bytes + signature from your framework's request object
    # before parsing JSON — the verifier needs the unparsed body.
    raw = body.pop("_raw_body")
    signature = body.pop("_signature_header")
    webhook_id = body.get("webhook_id")
    if not await verifier.verify(raw, signature, webhook_id):
        return (401, {"error": "bad_signature"})
    return await webhook.handle(body)
```

`verify` uses `hmac.compare_digest` (constant-time). Missing signature
with `require_signature=True` raises `HMACSignatureMissingError` —
catch it in your adapter and return 401.

---

## Idempotent webhooks — dedup

Avito retries delivery on 5xx / timeout. Dedup by message id so a
retry doesn't double-process:

```python
from datetime import timedelta
from avitoapi.web.middlewares import WebhookIdempotencyMiddleware
from avitoapi.storage.redis import RedisStorage

storage = RedisStorage.from_url("redis://localhost:6379")
dedup = WebhookIdempotencyMiddleware(storage, ttl=timedelta(hours=24))

async def deduped_handler(body: dict) -> tuple[int, dict]:
    chat_id = body["payload"]["value"]["chat_id"]
    message_id = body["payload"]["value"]["id"]
    if await dedup.seen(chat_id, message_id):
        return (200, {"ok": True, "duplicate": True})
    return await webhook.handle(body)
```

TTL bounds the dedup set — 24 h is fine for Avito's retry window.

---

## Graceful shutdown

All backends honour cancellation cleanly:

```python
import asyncio
import signal

async def main():
    runner = WebhookRunner(config)
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop.set)

    await runner.start()
    log.info("up", host=config.host, port=config.port)
    await stop.wait()
    log.info("shutdown")
    await runner.stop()
    await dispatcher.shutdown(timeout=10.0)        # await in-flight handlers

asyncio.run(main())
```

`dispatcher.shutdown(timeout=...)` awaits every `dispatcher.spawn()`
background task — pair with the runner stop so in-flight handlers
finish their work before exit.

---

## Picking a backend

| Backend   | Pros                                            | Cons                                          |
|-----------|-------------------------------------------------|-----------------------------------------------|
| aiohttp   | Zero extra deps, default. Mature, stable.        | Bare web stack (no validation, no docs).      |
| fastapi   | OpenAPI, request validation, ecosystem.          | Pulls fastapi + uvicorn + pydantic-extras.    |
| litestar  | Faster startup than FastAPI, similar API.        | Newer; ecosystem still maturing.              |
| sanic     | Lightweight + fast.                              | Smaller ecosystem; quirky lifecycle.          |

For pure webhook ingestion: aiohttp wins on dep weight. For mixed
"webhooks + admin endpoints + auth + docs": FastAPI or Litestar.

---

## Custom backend

`BaseWebApp` + `BaseWebhookRunner` are abstract — implement your own
adapter (e.g. AWS Lambda + API Gateway, Starlette, Quart) by mirroring
the four built-in backends. Each only needs:

```python
class MyWebApp(BaseWebApp):
    def register_webhook(self, webhook: Webhook) -> None: ...

class MyRunner(BaseWebhookRunner):
    def _build_app(self) -> BaseWebApp: return MyWebApp()
    async def start(self) -> None: ...
    async def stop(self) -> None: ...
```

The `AvitoWebhookHandler` stays unchanged — it's already framework-
agnostic by design.

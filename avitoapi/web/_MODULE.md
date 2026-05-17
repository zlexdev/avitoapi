# avitoapi.web

Webhook server bits — multi-backend WebApp/Runner + Avito-specific adapter.

## Surface

- `Webhook`, `WebhookConfig`, `WebhookHandler` — framework-agnostic
  descriptors. `Webhook(path, handler, http_method="POST")`,
  `WebhookConfig(host, port, webhooks)`.
- `WebApp`, `WebhookRunner` — aliases to the aiohttp backend (default,
  zero extra deps). Lazy — aiohttp is only imported on first access.
- `BaseWebApp`, `BaseWebhookRunner` — ABCs every backend implements.
- `AiohttpWebApp` / `AiohttpWebhookRunner` — aiohttp backend.
- `FastAPIWebApp` / `FastAPIWebhookRunner` — FastAPI on uvicorn.
- `LitestarWebApp` / `LitestarWebhookRunner` — Litestar on uvicorn.
- `SanicWebApp` / `SanicWebhookRunner` — Sanic on `create_server`.
- `AvitoWebhookHandler(dispatcher, mount_path="/messenger")` —
  HTTP-framework-agnostic adapter. `await handler.handle(body)` accepts
  `bytes | str | dict`, returns `(status, body_dict)`.
- `AvitoWebhookParseError` — raised internally on malformed payloads;
  surfaced as `(400, {"error": "invalid_body"})`.

## Picking a backend

```python
from avitoapi.web import (
    Webhook, WebhookConfig,
    FastAPIWebhookRunner,   # or LitestarWebhookRunner, SanicWebhookRunner, AiohttpWebhookRunner
)

config = WebhookConfig(host="0.0.0.0", port=8080, webhooks=[
    Webhook(path="/messenger", handler=avito_handler.handle),
])
runner = FastAPIWebhookRunner(dispatcher=dp, config=config)
await runner.start()
# ... serves until ...
await runner.stop()
```

Every backend is **lazy-loaded** — importing `avitoapi.web` never pulls
aiohttp / FastAPI / Litestar / Sanic. The HTTP framework only gets
imported when you instantiate its concrete `*WebApp` / `*WebhookRunner`.

## Backend lifecycle

| backend  | server impl                        | start                          | stop                           |
| -------- | ---------------------------------- | ------------------------------ | ------------------------------ |
| aiohttp  | `web.AppRunner` + `web.TCPSite`    | `await site.start()`           | `site.stop()` + `runner.cleanup()` |
| fastapi  | `uvicorn.Server` background task   | `serve()` task + wait `started` | `should_exit = True`           |
| litestar | `uvicorn.Server` background task   | `serve()` task + wait `started` | `should_exit = True`           |
| sanic    | `Sanic.create_server`              | `await server.start_serving()` | `server.close()` + `wait_closed()` |

FastAPI and Litestar runners need `uvicorn` (covered by their extras).
Sanic ships its own server (`create_server`) — no uvicorn needed.

## Dispatcher contract

`AvitoWebhookHandler` looks for `event_entry` / `feed_event` / `dispatch` /
`propagate_event` on the dispatcher (in that order). Falls back to
`dispatcher.router.propagate(event, ctx)` if none exists.

## Why dict-in instead of `Request`

So the adapter is unit-testable without any HTTP framework. Concrete
framework wiring lives in the per-backend `*WebApp.register_webhook`
methods — each one parses the body to `dict` before invoking the
caller's handler.

## Middlewares

`avitoapi/web/middlewares/` — `hmac_signature`, `idempotency`, `fast_return`.
See its `_MODULE.md`.

## Files

- `server.py` — `Webhook` / `WebhookConfig` / `WebhookHandler` dataclasses
  + lazy `WebApp` / `WebhookRunner` aliases to the aiohttp backend.
- `avito_webhook_handler.py` — `AvitoWebhookHandler`, `AvitoWebhookParseError`.
- `servers/_base.py` — `BaseWebApp` / `BaseWebhookRunner` ABCs.
- `servers/aiohttp_server.py` — aiohttp backend.
- `servers/fastapi_server.py` — FastAPI + uvicorn backend.
- `servers/litestar_server.py` — Litestar + uvicorn backend.
- `servers/sanic_server.py` — Sanic backend.
- `middlewares/` — three webhook middlewares.

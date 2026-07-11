# servers/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

> Per-framework webhook server backends.

## __init__.py
```
# Per-framework webhook server backends.


__getattr__(name: str) -> Any

```

## _base.py
```
# Base contracts for HTTP-framework backends.


cls BaseWebApp(ABC)
  register_webhook(webhook: Webhook) -> None
    # Mount ``webhook`` on the underlying app under its path/method.

cls BaseWebhookRunner(ABC)
  __init__() -> None
  async start() -> None
    # Bind the socket and serve. Blocks until cancelled.
  async stop() -> None
    # Stop accepting new connections, drain, then return.

```

## aiohttp_server.py
```
# aiohttp-backed webhook server.


cls AiohttpWebApp(BaseWebApp)
  # Thin wrapper around ``aiohttp.web.Application``.
  __init__() -> None
  register_webhook(webhook: Webhook) -> None

cls AiohttpWebhookRunner(BaseWebhookRunner)
  # Boot an ``aiohttp.web.AppRunner`` + ``TCPSite`` pair.
  async start() -> None
  async stop() -> None

```

## fastapi_server.py
```
# FastAPI-backed webhook server.


cls FastAPIWebApp(BaseWebApp)
  # Thin wrapper around ``fastapi.FastAPI``.
  __init__() -> None
  register_webhook(webhook: Webhook) -> None

cls FastAPIWebhookRunner(BaseWebhookRunner)
  async start() -> None
  async stop() -> None

```

## litestar_server.py
```
# Litestar-backed webhook server.


cls LitestarWebApp(BaseWebApp)
  __init__() -> None
  app() -> Any
  app(value: Any) -> None
  register_webhook(webhook: Webhook) -> None

cls LitestarWebhookRunner(BaseWebhookRunner)
  # Drive ``uvicorn.Server`` over the Litestar app.
  async start() -> None
  async stop() -> None

```

## sanic_server.py
```
# Sanic-backed webhook server.


cls SanicWebApp(BaseWebApp)
  # Thin wrapper around ``sanic.Sanic``.
  __init__(name: str? = None) -> None
  register_webhook(webhook: Webhook) -> None

cls SanicWebhookRunner(BaseWebhookRunner)
  # Boot a Sanic server inside the current event loop.
  async start() -> None
  async stop() -> None

```

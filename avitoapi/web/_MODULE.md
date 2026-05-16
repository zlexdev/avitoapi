# avitoapi.web

Webhook server bits + Avito-specific adapter.

## Surface

- `WebApp`, `WebhookRunner`, `WebhookConfig`, `Webhook` — re-exports from
  `evented` when installed; stubs that raise `ImportError` on instantiation
  otherwise.
- `AvitoWebhookHandler(dispatcher, mount_path="/messenger")` —
  HTTP-framework-agnostic adapter. `await handler.handle(body)` accepts
  `bytes | str | dict`, returns `(status, body_dict)`.
- `AvitoWebhookParseError` — raised internally on malformed payloads;
  surfaced as `(400, {"error": "invalid_body"})`.

## Dispatcher contract

`AvitoWebhookHandler` looks for `feed_event` / `dispatch` /
`propagate_event` on the dispatcher (in that order). Falls back to
`dispatcher.router.<observer>.route(event)` if none exists.

## Why dict-in instead of `aiohttp.web.Request`

So the adapter is unit-testable without aiohttp. Concrete HTTP wiring
(parse body bytes, read signature header, mount on aiohttp / FastAPI /
Litestar) lives in `examples/echo_bot/`.

## Middlewares

`avitoapi/web/middlewares/` — `hmac_signature`, `idempotency`, `fast_return`.
See its `_MODULE.md`.

## Files

- `server.py` — evented re-exports + import-guard stubs.
- `avito_webhook_handler.py` — `AvitoWebhookHandler`, `AvitoWebhookParseError`.
- `middlewares/` — the three webhook middlewares.

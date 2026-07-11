# web/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

> Webhook server bits — multi-backend WebApp/Runner + Avito adapter.

## Submodules

- [`middlewares/`](middlewares\_MODULE_AUTO.md) — Webhook-side middlewares: signature verification, fast-return. (3 py, 5 cls)
- [`servers/`](servers\_MODULE_AUTO.md) — Per-framework webhook server backends. (5 py, 10 cls, 1 fn)

## __init__.py
```
# Webhook server bits — multi-backend WebApp/Runner + Avito adapter.

_LAZY_SERVER = {'WebApp', 'WebhookRunner'}
_LAZY_BACKENDS = …

__getattr__(name: str) -> Any

```

## avito_webhook_handler.py
```
# HTTP-agnostic Avito webhook adapter.


cls AvitoWebhookParseError(ValueError)
  # Raised when the webhook body does not match an Avito payload shape.

cls AvitoWebhookHandler
  __init__(dispatcher: Any) -> None
  async handle(body: bytes | str | JsonObject) -> tuple[int, JsonObject]
  parse_event(payload: JsonObject) -> Event

```

## server.py
```
# Framework-agnostic webhook descriptors + default backend aliases.


cls Webhook: path: str, handler: WebhookHandler, http_method: str

cls WebhookConfig: host: str, port: int, webhooks: list[Webhook]
  # Bundle of :class:`Webhook` descriptors used by any backend runner.

__getattr__(name: str) -> Any

```

# avitoapi.web.middlewares

Webhook-side middlewares. Each is an independent class; `AvitoWebhookHandler`
(see `avitoapi/web/avito_webhook_handler.py`) composes `HMACSignatureMiddleware`
+ `WebhookFastReturnMiddleware` for the standard chain. Dedup is no longer a
webhook-side middleware — it happens once at `Dispatcher.feed_event`, keyed by
`event.dedup_key`.

## `HMACSignatureMiddleware`

Verifies the `x-avito-messenger-signature` HMAC-SHA256 over the raw body
using a per-webhook secret looked up via an async `SecretProvider`.

```python
mw = HMACSignatureMiddleware(secret_provider, require_signature=True)
ok = await mw.verify(raw_body, signature_header, webhook_id)
```

Constant-time compare via `hmac.compare_digest`. With
`require_signature=False` a missing header just returns `False`; with
`True` it raises `HMACSignatureMissingError`.

## `WebhookFastReturnMiddleware`

Wraps the actual handler in a task so the HTTP response can return
inside Avito's 2 s SLA. Backed by `evented.TaskTracker` when available;
otherwise an in-package tracker with `asyncio.create_task` + strong-ref
set (so tasks aren't garbage-collected mid-execution).

```python
fr = WebhookFastReturnMiddleware()  # builds a fallback tracker
task = fr.schedule(some_async_handler(event))
# HTTP response returns now; handler keeps running.
```

## Files

- `hmac_signature.py` — `HMACSignatureMiddleware`, `SecretProvider`, `HMACSignatureMissingError`.
- `fast_return.py` — `WebhookFastReturnMiddleware`, `_FallbackTaskTracker`.
- `__init__.py` — public re-exports.

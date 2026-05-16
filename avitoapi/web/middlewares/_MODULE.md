# avitoapi.web.middlewares

Webhook-side middlewares. Each is an independent class; the echo bot
composes them (see `examples/echo_bot/echo_bot/dispatcher_factory.py`).

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

## `WebhookIdempotencyMiddleware`

TTL-bounded dedup on `(chat_id, message_id)`. Backed by `BaseStorage`;
namespace is auto-applied (`"webhook_seen"`). `await mw.seen(chat, msg)`
returns `True` on a replay and records the key on first sight.

Default TTL: 1 hour. Adjust via `ttl=timedelta(...)` for very chatty
chats.

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
- `idempotency.py` — `WebhookIdempotencyMiddleware`.
- `fast_return.py` — `WebhookFastReturnMiddleware`, `_FallbackTaskTracker`.
- `__init__.py` — public re-exports.

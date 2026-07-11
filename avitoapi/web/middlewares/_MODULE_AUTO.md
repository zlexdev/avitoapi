# middlewares/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

> Webhook-side middlewares: signature verification, fast-return.

## __init__.py
```
# Webhook-side middlewares: signature verification, fast-return.


```

## context.py
```
# Typed context carrier for the webhook-side middleware chain.


cls WebhookRequestContext: raw_body: bytes, headers: dict[str, str], webhook_id: str, chat_id: str, message_id: str

```

## fast_return.py
```
# Spawn-and-return middleware — keeps the HTTP reply under Avito's 2s timeout.


cls _FallbackTaskTracker
  # Minimal task tracker — keeps strong refs so tasks aren't GC'd.
  __init__() -> None
  spawn(coro: Coroutine[Any, Any, Any) -> asyncio.Task[Any]
    # Schedule ``coro`` and return the task. Reference held until done.
  async shutdown(timeout: float = 5.0) -> None
    # Wait for in-flight tasks. Idempotent.

cls WebhookFastReturnMiddleware(BaseMiddleware[Any, Any])
  __init__(task_tracker: Any? = None) -> None
  tracker() -> Any
    # The underlying tracker — exposed for shutdown coordination.
  schedule(coro_or_awaitable: Coroutine[Any, Any, Any] | Awaitable[Any) -> asyncio.Task[Any]
    # Hand off to the tracker. Returns the task; caller may ignore it.

```

## hmac_signature.py
```
# HMAC-SHA256 signature verification for inbound Avito webhooks.


cls HMACSignatureMissingError(ValueError)
  # Raised when ``require_signature=True`` and no header was supplied.

cls HMACSignatureMiddleware(BaseMiddleware[Any, Any])
  __init__(secret_provider: SecretProvider) -> None
  async verify(raw_body: bytes, signature: str?, webhook_id: str) -> bool

```

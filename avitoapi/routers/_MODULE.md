# avitoapi.routers

Per-domain routers exposing typed `EventObserver` attributes.

## Surface

- `MessengerRouter` — `new_message`, `message_read`, `chat_archived`.
- `EventObserver[E]` — re-export of `evented.EventObserver` when available,
  otherwise an in-package aiogram-style observer with `@obs()` decorator,
  `register()`, `route(event)` runtime.

## Backend selection

If `evented` is installed: `MessengerRouter` extends `evented.Router` and
gets the full filter / middleware / sub-router machinery.

If not: a minimal `_FallbackRouter` with three `_FallbackEventObserver`
attributes is used so tests + small single-process bots work without the
private dep.

## Adding a domain router (W5/W6)

```python
class OrdersRouter(_RouterBase):
    order_created: EventObserver[OrderCreated]
    order_status_changed: EventObserver[OrderStatusChanged]
```

## Files

- `messenger.py` — `MessengerRouter`, `EventObserver`, `_FallbackEventObserver`.
- `__init__.py` — public re-exports.

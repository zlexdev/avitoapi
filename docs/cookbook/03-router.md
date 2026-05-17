# Router & sub-routers

`Router` is the aiogram-style decorator surface. `Dispatcher` itself is
a `Router`, so handlers can attach directly when you don't need
sub-router isolation.

---

## Observers as attributes

Every SDK event is exposed as a named observer on the router. Decorating
a coroutine registers it for that event.

```python
from avitoapi import Router

router = Router()

@router.new_message()
async def on_message(event, ctx):
    print("got", event.message.text)

@router.order_created()
async def on_order(event, ctx):
    print("new order", event.order_id)

@router.balance_low()
async def on_balance_low(event, ctx):
    print("topup needed", event.amount)
```

Full observer catalog (see `_routers.py` for the source of truth):

| Domain     | Observers                                                                 |
|------------|---------------------------------------------------------------------------|
| Messenger  | `new_message`, `text_message`, `image_message`, `link_message`, `item_message`, `location_message`, `voice_message`, `call_message`, `file_message`, `system_message`, `app_call_message`, `deleted_message`, `unknown_message`, `message_read`, `chat_archived`, `chat_blacklisted`, `voice_file_resolved` |
| Orders     | `order_created`, `order_confirmed`, `order_shipped`, `order_delivered`, `order_completed`, `order_cancelled`, `order_refunded`, `order_status_changed` |
| Delivery   | `parcel_status_changed`, `parcel_handed_over`, `parcel_delivered`, `parcel_returned`, `announcement_tracked` |
| Reviews    | `review_received`, `review_answered`                                       |
| Autoload   | `autoload_report_ready`, `autoload_failed`                                 |
| Calls      | `call_received`, `call_ended`, `call_recording_ready`                      |
| Balance    | `balance_changed`, `balance_topped_up`, `balance_low`, `bonus_received`    |
| Items      | `item_status_changed`, `item_published`, `item_blocked`, `item_unblocked`, `item_sold`, `item_archived` |
| Lifecycle  | `on_startup`, `on_shutdown`, `on_token_refreshed`, `on_auth_failed`, `on_webhook_error`, `on_poll_error` |

---

## Sub-routers (plugin shape)

Compose a tree — one router per feature / plugin / domain. Sub-routers
inherit propagation but isolate handler registration.

```python
from avitoapi import Dispatcher, Router

dispatcher = Dispatcher()

# /plugins/chat/router.py
chat_router = Router(name="chat")

@chat_router.new_message()
async def chat_handler(event, ctx): ...

# /plugins/orders/router.py
orders_router = Router(name="orders")

@orders_router.order_created()
async def order_handler(event, ctx): ...

# wire them
dispatcher.include_routers(chat_router, orders_router)
```

`include_router` returns the child so you can chain. Re-including the
same router under a second parent raises `RuntimeError` — sub-routers
have exactly one parent.

---

## Multiple handlers per event

A single observer can hold many handlers; each is filtered independently.
All matching handlers run in registration order.

```python
@router.new_message(F.message.text.contains("/start"))
async def on_start(event, ctx): ...

@router.new_message(F.message.text.contains("/help"))
async def on_help(event, ctx): ...

# Catch-all — fires for any new_message that none of the others matched
@router.new_message()
async def fallback(event, ctx): ...
```

The catch-all still fires on every new message — there is no
"no-other-matched" gate. Order your handlers accordingly, or use FSM
([06-fsm.md](06-fsm.md)) to gate by conversational state.

---

## Custom routes (string keys)

For non-event triggers (debug pings, custom signals) the bare
`router.manager(name)` returns a `HandlerManager` you can target with
`router.on(name, ...)`:

```python
debug = router.manager("debug.ping")

@router.on("debug.ping")
async def pong(event, ctx):
    print("pong", event)

# elsewhere:
await debug.trigger(my_event, ctx)
```

This is the same shape the built-in observers use internally — just
without the predicate gate. Useful for testing or for surfacing
non-Avito application events through the same router.

---

## Inspecting the tree

```python
for r in dispatcher.iter_routers():
    print(r.name, "→ handlers:", sum(len(m.handlers) for m in r._managers.values()))
```

Depth-first walk: dispatcher → every descendant. Handy for startup logs
or admin dashboards.

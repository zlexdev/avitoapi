# avitoapi.routers

A single aiogram-style `Router` exposing every SDK event as a named
`EventObserver` attribute. One class, one instance per scope, sub-routers
compose via `include_router` for plugin / per-feature isolation.

`avitoapi.Dispatcher` multiply-inherits from `Router` so every observer
attribute is available directly on the dispatcher — handlers can attach
without an intermediate routing layer.

## Surface

`Router(name: str = "avito")` — extends `evented.Router`. Observers:

- **Messenger:** `new_message`, `text_message`, `image_message`,
  `link_message`, `item_message`, `location_message`, `voice_message`,
  `call_message`, `file_message`, `system_message`, `app_call_message`,
  `deleted_message`, `unknown_message`, `message_read`, `chat_archived`,
  `chat_blacklisted`, `voice_file_resolved`. The typed `*_message`
  observers are pre-filtered views over `new_message` keyed by `MessageType`.
- **Orders:** `order_status_changed`, `order_created`, `order_confirmed`,
  `order_shipped`, `order_delivered`, `order_completed`, `order_cancelled`,
  `order_refunded`.
- **Delivery:** `parcel_status_changed`, `parcel_handed_over`,
  `parcel_delivered`, `parcel_returned`, `announcement_tracked`.
- **Reviews:** `review_received`, `review_answered`.
- **Autoload:** `autoload_report_ready`, `autoload_failed`.
- **Calltracking:** `call_received`, `call_ended`, `call_recording_ready`.
- **Balance:** `balance_changed`, `balance_topped_up`, `balance_low`,
  `bonus_received`.
- **Items:** `item_status_changed`, `item_published`, `item_blocked`,
  `item_unblocked`, `item_sold`, `item_archived`.
- **Lifecycle:** `on_startup`, `on_shutdown`, `on_token_refreshed`,
  `on_auth_failed`, `on_webhook_error`, `on_poll_error`. The `on_`
  prefix avoids colliding with `Dispatcher.shutdown()` (the async
  graceful-stop method inherited from `evented.Dispatcher`).

`EventObserver` — re-export of `evented.EventObserver` for type annotations.
`install_observers(router_like)` — free function attaching every observer
to any `evented.Router` subclass; used by both `Router.__init__` and
`Dispatcher.__init__`.

## Usage

```python
from avitoapi import Dispatcher

dp = Dispatcher()

@dp.text_message()
async def on_text(event, ctx):
    await event.message.reply("hi")

@dp.order_created()
async def on_new_order(event, ctx):
    print(event.order_id)
```

Composition (plugin pattern):

```python
from avitoapi import Router

plugin = Router(name="my_plugin")

@plugin.order_refunded()
async def alert_refund(event, ctx): ...

dp = Dispatcher()
dp.include_router(plugin)
```

## Backend

Hard dep on `evented` (private at `github.com/zlexdev/evented`). Install:

```bash
pip install 'git+https://${GH_TOKEN}@github.com/zlexdev/evented.git'
```

## Files

- `_routers.py` — the `Router` class, `install_observers` helper, `EventObserver` alias.
- `__init__.py` — public surface.

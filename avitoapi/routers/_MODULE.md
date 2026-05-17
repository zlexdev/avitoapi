# avitoapi.routers

Per-domain routers exposing typed `EventObserver` attributes. Aiogram-style:
each domain owns one `Router` subclass, each observer is one attribute, the
Dispatcher composes them via `include_router`.

## Surface

- `MessengerRouter` — `new_message`, `text_message`, `image_message`,
  `link_message`, `item_message`, `location_message`, `voice_message`,
  `call_message`, `file_message`, `system_message`, `app_call_message`,
  `deleted_message`, `unknown_message`, `message_read`, `chat_archived`,
  `chat_blacklisted`, `voice_file_resolved`. The typed `*_message`
  observers are convenience pre-filtered views over `new_message` keyed by
  `MessageType`.
- `OrdersRouter` — `order_status_changed`, `order_created`,
  `order_confirmed`, `order_shipped`, `order_delivered`, `order_completed`,
  `order_cancelled`, `order_refunded`.
- `DeliveryRouter` — `parcel_status_changed`, `parcel_handed_over`,
  `parcel_delivered`, `parcel_returned`, `announcement_tracked`.
- `ReviewsRouter` — `review_received`, `review_answered`.
- `AutoloadRouter` — `report_ready`, `failed`.
- `CalltrackingRouter` — `call_received`, `call_ended`, `recording_ready`.
- `BalanceRouter` — `balance_changed`, `balance_topped_up`, `balance_low`,
  `bonus_received`.
- `ItemsRouter` — `item_status_changed`, `item_published`, `item_blocked`,
  `item_unblocked`, `item_sold`, `item_archived`.
- `LifecycleRouter` — `startup`, `shutdown`, `token_refreshed`,
  `auth_failed`, `webhook_error`, `poll_error`.
- `Router`, `EventObserver` — re-exports of the `evented` primitives.

## Backend

All routers subclass `evented.Router` directly — `evented` is a **required**
private dep at `github.com/zlexdev/evented`. No fallbacks. Install:

```bash
pip install 'git+https://${GH_TOKEN}@github.com/zlexdev/evented.git'
```

## Files

- `_routers.py` — every `*Router` class.
- `__init__.py` — public re-exports.

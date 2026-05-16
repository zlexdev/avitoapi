# avitoapi.events

Typed event classes that flow through the Dispatcher.

## Surface

- `NewMessage(account_id, chat_id, message)` — inbound message arrived.
- `MessageRead(account_id, chat_id, message_id)` — counterparty read receipt.
- `ChatArchived(account_id, chat_id)` — chat archived.

All inherit `MessengerEvent`, which inherits the `evented.Event` base when
the `evented` package is installed. Without `evented`, a minimal fallback
base is shipped that supports the same `event_name=` class-kwarg pattern
so handlers can dispatch by name.

## Why `message: Any`

The discriminated message-type union lives in `avitoapi.models.messenger`
(wave 3). Pinning the type here would create a circular dep between
`events` and `models.messenger`. Consumers cast at the use site.

## Files

- `messenger.py` — `MessengerEvent`, `NewMessage`, `MessageRead`, `ChatArchived`.
- `__init__.py` — public re-exports.

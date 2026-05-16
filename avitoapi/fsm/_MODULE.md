# avitoapi.fsm

Aiogram-style finite state machine for multi-step chat / order /
payment flows on top of Avito's messenger.

## Surface

- `FSMContext` — per-key facade exposing `get_state`, `set_state`,
  `get_data`, `set_data`, `update_data`, `clear`.
- `State` — single state declaration; the string id is auto-prefixed
  with the owning `StatesGroup` (`ChatStates.idle.state ==
  "ChatStates:idle"`).
- `StatesGroup` — container for related `State` declarations.
- `StateFilter(*states)` — async predicate matching when an
  `FSMContext`'s current state is one of `states`. Pass `None` to
  match cleared contexts.
- `StorageKey(account_id, chat_id)` — composite identity, rendered as
  `f"fsm:{account_id}:{chat_id}"`.
- `AvitoStorageKeyBuilder.build(account_id, chat_id)` — helper that
  stringifies both inputs and produces a `StorageKey`.
- `MemoryFSMStorage` — in-process backend (state + data in two
  parallel dicts) used by tests and short-lived workers.

## Backend selection

- When `evented` is importable, the package re-exports its primitives
  verbatim (`evented.FSMContext`, `evented.State`, ...). This is the
  intended production path — `evented` ships persistent backends
  (redis / mongo / asyncpg) and a real Dispatcher integration.
- When `evented` is **not** importable (the common case in CI before
  the private dep is pinned), Wave 3 falls back to in-house
  stand-ins in `_fallback.py`. They cover the exact API surface the
  handlers and tests use, so swapping in `evented` later is a no-op
  for handler code.

Wave 4 pins `evented @ <tag>` in `pyproject.toml`; once installed,
the `_fallback` path is never selected.

## Storage key shape

Avito's per-account chat model maps onto `(account_id, chat_id)`:

```python
key = AvitoStorageKeyBuilder().build(account_id="12345", chat_id="abc")
str(key) == "fsm:12345:abc"
```

Account namespace prevents two accounts talking about the same
`chat_id` from sharing FSM state.

## Why a fallback at all

The Wave-3 ship gate is "FSM round-trip test green without
`evented`". `evented` is a private dep behind `GH_TOKEN`; CI without
the secret must still pass. The fallback is intentionally minimal —
not a competitor to `evented`, just enough to satisfy the contract
this package promises.

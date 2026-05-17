# FSM — finite state machine per chat

`FSMContext` gives each `(account_id, chat_id)` pair an independent
state + data bag. Backed by any storage; the in-tree default is
`MemoryFSMStorage`.

---

## Declare states

States are grouped under a `StatesGroup`. The metaclass auto-prefixes
each `State` with its group name so `Onboarding:awaiting_name` is the
full identifier — collisions across groups are impossible.

```python
from avitoapi.fsm import State, StatesGroup

class Onboarding(StatesGroup):
    awaiting_name = State()
    awaiting_phone = State()
    awaiting_address = State()
    done = State()
```

Reference states as `Onboarding.awaiting_name` — they expose
`.state == "Onboarding:awaiting_name"` for comparisons.

---

## Bind FSM context to handlers

Use an outer middleware to construct one `FSMContext` per event (see
[05-middleware.md](05-middleware.md) for the full middleware shape):

```python
from avitoapi import BaseMiddleware
from avitoapi.fsm import AvitoStorageKeyBuilder, FSMContext, MemoryFSMStorage

class FSMMiddleware(BaseMiddleware):
    def __init__(self, storage):
        self._storage = storage
        self._kb = AvitoStorageKeyBuilder()

    async def __call__(self, handler, event, ctx):
        if hasattr(event, "account_id") and hasattr(event, "chat_id"):
            key = self._kb.build(event.account_id, event.chat_id)
            ctx.workflow_data["fsm"] = FSMContext(self._storage, key)
        return await handler(event, ctx)

dispatcher.outer_middleware.register(FSMMiddleware(MemoryFSMStorage()))
```

`AvitoStorageKeyBuilder` stringifies inputs and renders
`fsm:<account_id>:<chat_id>` — two sellers talking about the same
`chat_id` get separate state buckets.

---

## Drive a conversation

```python
@router.new_message(F.message.text == "/start")
async def start(event, ctx):
    fsm = ctx.workflow_data["fsm"]
    await fsm.set_state(Onboarding.awaiting_name)
    await client.send_text_message(event.chat_id, "What's your name?")

@router.new_message()
async def collect_name(event, ctx):
    fsm = ctx.workflow_data["fsm"]
    if await fsm.get_state() != Onboarding.awaiting_name.state:
        return                                # not our turn
    await fsm.update_data(name=event.message.text)
    await fsm.set_state(Onboarding.awaiting_phone)
    await client.send_text_message(event.chat_id, "And your phone?")

@router.new_message()
async def collect_phone(event, ctx):
    fsm = ctx.workflow_data["fsm"]
    if await fsm.get_state() != Onboarding.awaiting_phone.state:
        return
    await fsm.update_data(phone=event.message.text)
    data = await fsm.get_data()
    await client.send_text_message(
        event.chat_id, f"Got it: {data['name']} / {data['phone']}"
    )
    await fsm.set_state(Onboarding.done)
```

`get_state()` / `set_state()` / `get_data()` / `set_data()` /
`update_data(**kwargs)` / `clear()` cover everything most flows need.

---

## Filter by state — `StateFilter`

Skip the boilerplate `if state != X: return` with a `StateFilter`
predicate. The filter is async (it reads from storage), so attach it
through a custom predicate adapter rather than the magic filter `F`.

```python
from avitoapi.fsm import StateFilter

awaiting_phone = StateFilter(Onboarding.awaiting_phone)

async def in_phone_state(event) -> bool:
    # custom adapter — we don't have the FSM in scope here, but the
    # outer middleware bound it on ctx. So gate by checking ctx in the
    # handler instead. See the "Cleaner: predicate over ctx" snippet
    # below.
    raise NotImplementedError

# Cleaner: gate by ctx via inner middleware that reads ctx.workflow_data["fsm"]
```

In practice the most ergonomic shape is the explicit guard inside the
handler (as shown above) — it keeps `event` filters synchronous and
state filters explicit. If you do want a predicate-style approach,
build it as an **inner middleware** that reads
`ctx.workflow_data["fsm"]` and short-circuits with `return None` when
the state doesn't match.

---

## Clear at end-of-flow

```python
await fsm.clear()    # drops both state and data for this key
```

Forgetting to clear is the most common FSM bug — a returning user
restarts mid-flow. Pair every `set_state` with a known terminal state
or call `clear()` when you reach the end.

---

## Custom storage

`MemoryFSMStorage` is the reference implementation. Swap to any backend
that implements `get_state` / `set_state` / `get_data` / `set_data` /
`clear` over `StorageKey`. The in-tree `RedisStorage` /
`PostgresStorage` / `MongoStorage` modules ship with the FSM-compatible
shape — pick one for cross-process deploys:

```python
from avitoapi.fsm import FSMContext
from avitoapi.storage.redis import RedisStorage

storage = RedisStorage.from_url("redis://localhost:6379")
dispatcher.outer_middleware.register(FSMMiddleware(storage))
dispatcher.fsm_storage = storage    # also visible to other plugins via dispatcher
```

State + data live under separate inner keys so `clear()` is atomic
without dropping unrelated dispatcher bookkeeping.

---

## Inspecting state at runtime

```python
state = await fsm.get_state()
data = await fsm.get_data()
log.info("fsm", state=state, data=data, key=fsm.key.render())
```

`fsm.key` is the `StorageKey` instance — `render()` gives you the
exact key the backend stores under (handy for debug tooling).

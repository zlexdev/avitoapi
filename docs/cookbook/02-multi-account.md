# Multi-account dispatcher

`Dispatcher` is a `Router` that knows about `Client` instances. One
process, many sellers, one event surface.

---

## Mental model

* `ClientConfig.client_id` + `client_secret` — your OAuth2 **integration
  app** credentials (the same pair across every seller you onboard).
* `ClientConfig.user_id` — the **OAuth scope** for the token cache; one
  seller = one `user_id` = one token bucket.
* `Client(..., account_id="alice")` — the **routing label** the
  dispatcher matches against `event.account_id`.

Different sellers can share the same `client_id`/`client_secret` (one
integration app) but **must** have distinct `user_id` and `account_id`.

---

## Static account list

```python
import asyncio
from avitoapi import Client, ClientConfig, make_dispatcher

SELLERS = [
    {"account_id": "alice", "user_id": 12345,
     "client_id": "int-abc", "client_secret": "shhh-a"},
    {"account_id": "bob",   "user_id": 67890,
     "client_id": "int-abc", "client_secret": "shhh-b"},
]

def build_client(row: dict) -> Client:
    config = ClientConfig(
        client_id=row["client_id"],
        client_secret=row["client_secret"],
        user_id=row["user_id"],
        rate_limit_global_rps=8.0,
    )
    return Client(config=config, account_id=row["account_id"])

dispatcher = make_dispatcher(accounts=[build_client(row) for row in SELLERS])

@dispatcher.new_message()
async def on_message(event, ctx):
    client = ctx.dispatcher.accounts[event.account_id]
    await client.send_text_message(event.chat_id, "echo: " + event.message.text)
```

`ctx.dispatcher.accounts` is a plain `dict[str, Client]` keyed by
`account_id` — add/remove at runtime without any framework dance:

```python
dispatcher.accounts["carol"] = build_client(new_seller_row)
del dispatcher.accounts["bob"]
```

---

## Tenant store as the source of truth

Pull `ClientConfig` rows from your DB / Vault / admin form and rebuild
the dispatcher on change — there's no hidden state.

```python
import asyncpg
from avitoapi import Client, ClientConfig, make_dispatcher

async def load_sellers(pool: asyncpg.Pool) -> list[Client]:
    rows = await pool.fetch(
        "SELECT account_id, user_id, client_id, client_secret, rate_limit "
        "FROM sellers WHERE active",
    )
    return [
        Client(
            config=ClientConfig(
                client_id=r["client_id"],
                client_secret=r["client_secret"],
                user_id=r["user_id"],
                rate_limit_global_rps=r["rate_limit"],
            ),
            account_id=r["account_id"],
        )
        for r in rows
    ]

async def main() -> None:
    pool = await asyncpg.create_pool(DATABASE_URL)
    dispatcher = make_dispatcher(accounts=await load_sellers(pool))
    # ... start your webhook server here
```

A pub/sub "seller-changed" channel can re-run `load_sellers` and swap
entries in `dispatcher.accounts` without restart.

---

## Per-account knobs

Tune any `ClientConfig` field per seller — keep the integration credentials
identical but vary throttling / breakers / endpoints individually.

```python
def build_client(row: dict) -> Client:
    config = ClientConfig(
        client_id=row["client_id"],
        client_secret=row["client_secret"],
        user_id=row["user_id"],
        rate_limit_global_rps=row.get("rps", 5.0),
        breaker_fail_threshold=row.get("breaker_threshold", 5),
        breaker_open_seconds=row.get("breaker_open_s", 30.0),
        breaker_per_account=True,            # isolate breaker per (host, path, account)
        request_timeout_s=row.get("timeout_s", 30.0),
    )
    return Client(config=config, account_id=row["account_id"])
```

`breaker_per_account=True` keeps one slow seller from tripping the
circuit for every other seller hitting the same endpoint.

---

## Shared infra, per-account config

Pass `session=`, `transport=`, or `storage=` to share heavy resources
across clients while keeping per-account `ClientConfig` distinct:

```python
from avitoapi import Client, ClientConfig, ListProxyTransport
from avitoapi.sessions.httpx_session import HttpxSession
from avitoapi.storage.redis import RedisStorage

shared_transport = ListProxyTransport([...])
shared_storage = RedisStorage.from_url("redis://localhost:6379")

def build_client(row: dict) -> Client:
    config = ClientConfig(client_id=row["cid"], client_secret=row["secret"],
                          user_id=row["user_id"])
    session = HttpxSession(config=config)         # one connection pool per client
    return Client(
        config=config,
        account_id=row["account_id"],
        session=session,
        transport=shared_transport,                # shared rotating proxy pool
        storage=shared_storage,                    # shared FSM / token cache
    )
```

`transport`, `storage`, and `session` are independent dimensions — mix
shared vs per-account freely.

---

## Dispatching events

`Dispatcher.feed_event` is the entry point — it persists the event,
fans out through every router, and (when the handler acks) drops it
from the queue.

```python
from avitoapi.events import NewMessage

event = NewMessage(account_id="alice", chat_id="c-1", message={...})
await dispatcher.feed_event(event)
```

In production you'll feed events from the webhook server
([12-webhooks.md](12-webhooks.md)) or from a polling loop —
`dispatch`, `event_entry`, and `feed_event` are interchangeable aliases
so app code can pick the name it prefers.

---

## Replay on restart

Unacked events survive a crash. On startup, drain them:

```python
async def on_startup(app):
    replayed = await dispatcher.replay_pending()
    log.info("replayed", count=replayed)
```

See [08-queue.md](08-queue.md) for queue + DLQ semantics.

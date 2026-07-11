# Quickstart

The shortest path from "I have client credentials" to "I'm hitting the
Avito Partner API from Python".

---

## Install

```bash
uv pip install -e .[dev]
# or, after the package lands on PyPI:
uv pip install avitoapi
```

Optional extras (lazy-loaded — install only what you use):

| Extra      | Purpose                                       |
|------------|-----------------------------------------------|
| `aiohttp`  | webhook server (default, no extra dep)        |
| `fastapi`  | FastAPI + uvicorn webhook backend             |
| `litestar` | Litestar + uvicorn webhook backend            |
| `sanic`    | Sanic webhook backend                         |
| `redis`    | `RedisStorage` for FSM + queues               |
| `postgres` | `PostgresStorage` for FSM + queues            |
| `mongo`    | `MongoStorage` for FSM + queues               |

---

## Configure

`ClientConfig` is a strict Pydantic model. The two required fields are
your OAuth2 app credentials.

### From `.env`

```bash
# .env
AVITO_CLIENT_ID=int-abc123
AVITO_CLIENT_SECRET=shhh-very-secret
AVITO_USER_ID=12345
```

```python
from avitoapi import ClientConfig
config = ClientConfig.from_env()  # reads AVITO_CLIENT_ID, AVITO_CLIENT_SECRET, AVITO_USER_ID, ...
```

### Inline

```python
from avitoapi import ClientConfig

config = ClientConfig(
    client_id="int-abc123",
    client_secret="shhh-very-secret",
    user_id=12345,
    request_timeout_s=30.0,
    rate_limit_global_rps=8.0,
)
```

`from_env` reads `AVITO_*` variables — see `config.py` for the full key
list (`AVITO_REQUEST_TIMEOUT_S`, `AVITO_MAX_RETRIES`, `AVITO_USER_AGENT`,
etc.). Construct inline when configuration comes from your own
DB / vault / admin form rather than process env.

---

## First call

```python
import asyncio
from avitoapi import Client, ClientConfig

async def main() -> None:
    async with Client(config=ClientConfig.from_env()) as client:
        me = await client.get_self()
        print(me.id, me.name)

asyncio.run(main())
```

`async with` opens the session funnel (connection pool, OAuth refresher,
rate-limit semaphore) and closes it on exit. Skip it only inside test
fixtures that own the lifecycle themselves.

---

## Paginated reads

Every paginated endpoint returns an async iterator:

```python
from avitoapi import Client, ClientConfig, ItemStatus

async with Client(config=ClientConfig.from_env()) as client:
    async for item in client.list_items(status=ItemStatus.ACTIVE):
        print(item.id, item.title, item.price)
```

The iterator transparently follows the next-page cursor and stops at
end-of-data. A configurable runaway guard
(`ClientConfig.pagination_max_pages`, default 1000) raises
`RunawayPagination` if the upstream cursor never terminates.

---

## State-machine-guarded mutations

Order / parcel / item status updates accept a `current=` and `strict=`
pair so an illegal transition raises before the request leaves the box:

```python
from avitoapi import OrderStatus

order = await client.get_order("o-42")

await client.change_order_status(
    "o-42",
    OrderStatus.CONFIRMED,
    current=order.status,   # raises InvalidStateTransition on illegal jump
    strict=True,
)
```

---

## Send a chat reply

```python
async for chat in client.list_chats(unread_only=True):
    await client.send_text_message(chat.id, "Hi! Thanks for your interest.")
```

`send_text_message` auto-attaches an `Idempotency-Key` derived from the
chat id + body hash, so a network retry won't double-send.

---

## Errors

```python
from avitoapi import (
    AuthError, ForbiddenError, NotFoundError, RateLimitedError,
    SDKError, ServerError, ValidationFailed,
)

try:
    await client.get_item(item_id=12345)
except NotFoundError:
    ...                       # 404 → item gone
except RateLimitedError as exc:
    await asyncio.sleep(exc.retry_after_s)
except ServerError:
    ...                       # 5xx, will retry under default policy
except SDKError as exc:
    ...                       # catch-all parent
```

Every Avito HTTP error subclasses `SDKError`. See `exceptions.py` for
the full hierarchy.

---

## Next

* **Multiple sellers** → [02-multi-account.md](02-multi-account.md)
* **Routing + filters** → [03-router.md](03-router.md), [04-filters.md](04-filters.md)
* **Webhooks (4 backends)** → [12-webhooks.md](12-webhooks.md)

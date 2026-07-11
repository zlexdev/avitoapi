<p align="center">
  <strong>avitoapi</strong>
</p>

<p align="center">
  <strong>Aiogram-style async Python SDK over the Avito Partner API — generated from the official OpenAPI spec.</strong>
</p>

<p align="center">
  <a href="pyproject.toml"><img src="https://img.shields.io/badge/version-0.1.0-blue?style=for-the-badge" alt="Version"></a>
  <a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.11+"></a>
  <a href="https://docs.pydantic.dev/"><img src="https://img.shields.io/badge/pydantic-v2-E92063?style=for-the-badge&logo=pydantic&logoColor=white" alt="Pydantic v2"></a>
  <img src="https://img.shields.io/badge/typed-mypy%20strict-2A6DB2?style=for-the-badge" alt="Typed">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License: MIT"></a>
</p>

---

**avitoapi** is a fully-typed async client for the Avito Partner API. The whole request
surface — method-as-class DTOs, per-domain response models, `StrEnum`s and flat `Client`
facades — is **generated from Avito's OpenAPI spec**, while the runtime (dispatcher, routers,
typed events, FSM, circuit breaker, proxy pool, webhook + polling feeds) is hand-written and
never touched by the generator. No runtime dependency beyond `pydantic`, `pydantic-settings`,
`curl_cffi`, `structlog`, and `email-validator`.

[Docs](docs/) · [Cookbook](docs/cookbook/README.md) · [API surface](docs/api-surface.md) · [AI-agent docs](docs/for_ai/index.md)

## Quickstart

```bash
uv pip install "git+https://github.com/zlexdev/avitoapi"
```

```python
import asyncio

from avitoapi import Client, ClientConfig


async def main() -> None:
    # Reads AVITO_CLIENT_ID / AVITO_CLIENT_SECRET from the environment.
    async with Client(config=ClientConfig.from_env()) as client:
        me = await client.user_info_self()
        print(me.id, me.name, me.email)


asyncio.run(main())
```

Every operation is a real `async def` on `Client` (`await client.user_info_self()`), typed
end to end: the call returns a `UserInfoSelf` model, not a raw dict. Browse the full method
catalogue in [`docs/api-surface.md`](docs/api-surface.md), or step through
[`docs/cookbook/01-quickstart.md`](docs/cookbook/01-quickstart.md).

## Examples

Four ways to drive the SDK, each on a different axis — pick the one that matches your topology.

### Direct calls — one account, request/response

Simplest entry point: construct a `Client`, `await` operations, get typed models back.

```python
from avitoapi import Client, ClientConfig

async with Client(config=ClientConfig.from_env()) as client:
    me = await client.user_info_self()
    balance = await client.user_balance(user_id=me.id)
    print(me.name, balance)
```

### Multi-account dispatch — routed events

Bind many accounts to one `Dispatcher` and route inbound events aiogram-style. The session
pool, storage and breaker store are shared across accounts by reference.

```python
from avitoapi.dispatcher import make_dispatcher
from avitoapi.events import NewMessage

dp = make_dispatcher(accounts=[client_a, client_b])


@dp.new_message()
async def on_message(event: NewMessage) -> None:
    print(event.account_id, event.chat_id, event.message.type)
```

Specialised observers pre-filter by message kind — `@dp.text_message()`, `@dp.image_message()`,
… — and magic filters narrow further: `@dp.new_message(F.message.type == "text")`. See
[`docs/cookbook/03-router.md`](docs/cookbook/03-router.md) and
[`docs/cookbook/04-filters.md`](docs/cookbook/04-filters.md).

### Webhook ingestion — push

For the messenger surface Avito pushes webhooks. `AvitoWebhookHandler` parses the payload into
a typed event, verifies the signature, dedups by event id, and feeds the dispatcher — behind any
of the bundled server backends (aiohttp / FastAPI / Litestar / Sanic).

```python
from avitoapi.web.avito_webhook_handler import AvitoWebhookHandler

handler = AvitoWebhookHandler(dp)

# Inside your web framework's POST route:
status, body = await handler.handle(raw_body, headers=request.headers, webhook_id=event_id)
```

Full per-framework server wiring lives in the [cookbook](docs/cookbook/README.md).

### Polling feed — pull

Every domain without webhooks (orders, items, reviews, …) is polled. Subclass `PollingRunner`:
it owns the cursor loop, persistence, backoff and error events — you implement only `poll()`.

```python
from avitoapi import PollBatch, PollingRunner
from avitoapi.events import OrderStatusChanged


class OrdersPoller(PollingRunner):
    def __init__(self, dp, client):
        super().__init__(dp, account_id=client.account_id, poller="orders", storage=client.storage)
        self._client = client

    async def poll(self, cursor):
        page = await self._client.orders(cursor=cursor)
        events = [OrderStatusChanged(order_id=o.id, status=o.status) for o in page.orders]
        return PollBatch(events=events, cursor=page.next_cursor)


await OrdersPoller(dp, client).start()  # mirrors BaseWebhookRunner.start()/stop()
```

A runnable end-to-end bot lives in [`examples/echo_bot.py`](examples/echo_bot.py).

### Channels & fan-out — merging multiple sources

`avitoapi.channels` gives handlers a bounded, backpressure-aware publish
surface (`dispatcher.channels.register(MemoryEventChannel(...))` +
`await dispatcher.publish(name, event)`); `avitoapi.fanout.SourceHub`
supervises several event sources (webhook + pollers + custom feeds) into
one dispatcher with health tracking and restart policy. See the module
docs under `avitoapi/channels/` and `avitoapi/fanout/`.

## Regenerating the SDK from the spec

The request surface is built by an in-tree codegen that fetches Avito's OpenAPI specs and emits
`methods/`, `models/`, `enums/` and the `Client` facades in house style:

```bash
python -m avitoapi.codegen --all          # regenerate every domain
python -m avitoapi.codegen --slug item    # or a single domain
```

The generator runs two-phase over the whole catalogue: build every domain, run global passes
(dedup structurally-identical models into `models/_shared.py`, make facade method names globally
unique), then emit and `ruff`-format. It is deliberately portable — `avitoapi/codegen/` depends
only on the stdlib, with the generic engine under `codegen/engine/`, the OpenAPI parser in
`codegen/parser.py`, and the Avito-specific bits (`fetch.py`, `config.py`) isolated so the whole
folder can be lifted out and retargeted. Map: [`docs/for_ai/index.md`](docs/for_ai/index.md).

## Community

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to set up locally, run the test suite, and submit
PRs. Use [issues](../../issues/new/choose) for bugs and feature requests.

## License

[MIT](LICENSE) © 2026 [zlexdev](https://github.com/zlexdev)

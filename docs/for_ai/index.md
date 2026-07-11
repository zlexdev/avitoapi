# avitoapi — map for AI agents

Compressed navigation for an AI agent working in this repo. Read this before spelunking source.
Each package ships a `_MODULE_AUTO.md` (generated surface digest) and often a `_MODULE.md`
(hand-written intent) — open those before the `.py` files.

## What this is

`avitoapi` is an aiogram-style async SDK over the **Avito Partner API**. The request surface
(methods / models / enums / per-domain `Client` facades) is **generated from the official
OpenAPI spec**; the runtime machinery is **hand-written and never touched by the generator**.

## Layers

| Concern | Where | Generated? |
|---|---|---|
| Method-as-class DTOs (`BaseMethod[T]`) | `avitoapi/methods/<domain>.py` | ✅ codegen |
| Response models (`AvitoObject`) + bound methods | `avitoapi/models/<domain>.py` | ✅ codegen |
| `StrEnum`s | `avitoapi/enums/<domain>.py` | ✅ codegen |
| Per-domain `Client` mixins (`await client.<op>(…)`) | `avitoapi/facade/<domain>.py` | ✅ codegen |
| Cross-domain shared models | `avitoapi/models/_shared.py`, `models/common.py` | ✅ codegen |
| Base classes / protocol / transport / sessions | `methods/_base.py`, `protocol/`, `transport/`, `sessions/` | hand-written |
| `Client` (flat facade over every op) | `avitoapi/client.py` | hand-written |
| Dispatcher / routers / typed events / FSM | `dispatcher.py`, `routers/`, `events/`, `fsm/` | hand-written |
| Event feeds (pull) | `avitoapi/polling.py` (`PollingRunner`) | hand-written |
| Webhook ingestion (push) | `web/avito_webhook_handler.py`, `web/servers/` (aiohttp/fastapi/litestar/sanic) | hand-written |
| Pagination / breaker / storage / proxy | `pagination/`, `breaker/`, `storage/`, `transport/proxy/` | hand-written |
| **Codegen (the auto-builder)** | `avitoapi/codegen/` | — |

## Codegen internals (`avitoapi/codegen/`)

Portable: the whole folder depends only on the stdlib and can be lifted out.

- `parser.py` — OpenAPI 3.0 document → intermediate representation (`Domain`/`Operation`/`Resolver`).
- `engine/` — host-agnostic IR → source machinery: `naming`, `types`, `build`, `entities`
  (bound-method inference), `render`, `emit_{enums,models,methods,facade}`, `dedup`
  (collapse identical models), `collisions` (globally-unique facade method names), `generate`.
- `fetch.py` + `config.py` — the only Avito-specific bits (spec URLs, slug↔module aliases,
  entity overrides). Swap these + `parser` to retarget another OpenAPI API.
- Run: `python -m avitoapi.codegen --all` (two-phase: build every domain → global passes → emit).

## Full API surface

- [`docs/api-surface.md`](../api-surface.md) — the exhaustive public surface.
- [`docs/cookbook/`](../cookbook/README.md) — hands-on recipes (multi-account, routing, filters,
  middleware, FSM, circuit-breaker, queue, webhooks, proxy rotation).

## Invariants worth knowing

- Money is `Money`/`Decimal`; datetimes are timezone-aware (`TZDatetime`).
- Every domain constant is a `StrEnum`; every boundary carries a typed DTO, never a raw dict.
- Errors are a typed hierarchy under `SDKError`, carrying args (not pre-formatted strings).
- `Client` inherits one `*Facade` mixin per domain; facade method names are globally unique.

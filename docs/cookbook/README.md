# avitoapi cookbook

Hands-on recipes for the `avitoapi` SDK. Each entry is self-contained
— scan the index, jump to the page you need, copy the snippet.

For the project overview see the [root README](../../README.md). For
exhaustive surface docs see each module's `_MODULE.md`.

---

## Getting started

| #   | Page                                            | What you'll learn                                                                    |
|-----|-------------------------------------------------|--------------------------------------------------------------------------------------|
| 01  | [Quickstart](01-quickstart.md)                  | Install, configure, first API call, pagination, state-guarded mutations, errors.     |
| 02  | [Multi-account dispatcher](02-multi-account.md) | Building `Client` per seller from a tenant store. Per-account tuning. Shared infra.  |

## Routing & filters

| #   | Page                                            | What you'll learn                                                                    |
|-----|-------------------------------------------------|--------------------------------------------------------------------------------------|
| 03  | [Router & sub-routers](03-router.md)            | Observer catalog, plugin-shaped routers, `include_router`, catch-all handlers.       |
| 04  | [Filters (`F`, `MagicFilter`)](04-filters.md)   | Magic filter chains, combinators, `in_`/`contains`/`func`, plain callables, reuse.   |
| 05  | [Middlewares — outer vs inner](05-middleware.md)| `BaseMiddleware`, FSM binding, retry / dedup, decorator form, per-router scope.      |

## Stateful flows

| #   | Page                                            | What you'll learn                                                                    |
|-----|-------------------------------------------------|--------------------------------------------------------------------------------------|
| 06  | [FSM (state machines)](06-fsm.md)               | `StatesGroup`, `FSMContext`, conversation flows, custom storage backends.            |
| 07  | [Circuit breaker](07-circuit-breaker.md)        | Per-endpoint breakers, per-account isolation, lifecycle, manual reset.               |

## Persistence

| #   | Page                                            | What you'll learn                                                                    |
|-----|-------------------------------------------------|--------------------------------------------------------------------------------------|
| 08  | [Persistent queue](08-queue.md)                 | At-least-once delivery, leases / DLQ / scheduler / worker pool, partition-by.        |

## Surface

| #   | Page                                            | What you'll learn                                                                    |
|-----|-------------------------------------------------|--------------------------------------------------------------------------------------|
| 12  | [Webhooks (4 backends)](12-webhooks.md)         | aiohttp / FastAPI / Litestar / Sanic runners, HMAC verify, dedup, graceful shutdown. |
| 13  | [Proxy transports](13-proxy.md)                 | Direct / list / callback, parsing, validation, rotation strategies, custom backends. |

---

## End-to-end example

A full working bot lives in [`examples/echo_bot`](../../examples/echo_bot/) —
multi-account dispatcher + aiohttp webhook + healthcheck endpoint +
Docker shell. Read it after the cookbook to see all the pieces wired
together.

---

## Conventions

* All snippets are Python 3.12+; the SDK uses `StrEnum` and `Self` features.
* Code is async unless trivially side-effect-free.
* `from avitoapi import X` is the supported public surface — anything
  reachable via that import is part of the stable API.
* Module-internal imports (`avitoapi.<sub>...`) are documented per
  module — see each module's `_MODULE.md`.

---

## Contributing examples

Found a pattern that took you an hour to figure out? Open a PR adding
a new cookbook page. Keep it:

* one topic per page,
* runnable snippets (no `...` placeholders for the load-bearing line),
* a "Next" pointer at the bottom to the closest neighbouring page,
* English prose.

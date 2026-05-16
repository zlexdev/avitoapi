# 00 — Audit (existing patterns + adopted decisions)

Greenfield repo — no existing code to audit. Findings here are the patterns
**adopted from the reference SDK** (`PlayerokAPI` plrk2) and the framework
**skill** (`aiogram-style-sdk-framework`), with `follow` / `fix` / `defer`
tags marking how the Avito SDK relates to each.

Severity legend: `critical` = load-bearing for the doctrine, `high` = strong
default, `medium` = nice-to-have, `low` = stylistic.

## Reference patterns from PlayerokAPI (plrk2)

| # | Pattern | Severity | Action | Notes |
|---|---|---|---|---|
| A1 | Flat client — `Account` holds ~50 public methods, no namespaces | critical | follow | Renamed `Client` per skill; identical shape |
| A2 | Mixin-based internal organisation (Properties, Auth, …) — split `client.py` once it grows | high | follow | Apply at >1500 LOC per `client.md` |
| A3 | Pydantic models with parent binding (`as_(account)`) | critical | follow | `BoundModel.as_(client)` per skill |
| A4 | `from_dict()` deserialization on each type | high | fix | Replace with `model_validate` (Pydantic v2 idiom); decoder lives in `protocol/rest.py` |
| A5 | GraphQL operations as classes (`_graphql/methods.py`) | n/a | defer | Avito is REST — no GraphQL ops to model |
| A6 | Custom exception hierarchy with factory pattern for pattern-matched errors | high | follow | `exceptions.py` mirrors shape; error-mapper reads Avito JSON `error.code` field |
| A7 | Rate limiting via `_delays` dict + `_handle_delay()` (sync sleep) | medium | fix | Replace with `evented.TokenBucket` (async, per-(account, scope) keys) |
| A8 | `Processor` updater + Router + Event classes for chat polling | critical | fix | Replace with `evented.Dispatcher` + `Router` + `EventObserver[T]` (per skill `_evented-integration.md`) |
| A9 | `apihelper.py` 1318-line monolith — curl_cffi + retry + ETag + CF detection + headers + Sentry | medium | fix | Split per skill: `sessions/curl.py` (HTTP) + `transport/retry.py` (policy) + `transport/headers.py` (UA) + `breaker/` (CF / 5xx) |
| A10 | `categories/` — static const classes for category UUIDs | medium | follow | Avito has similar category UUID tree; ship `categories/` with `Realty`, `Vehicles`, `Job`, etc. — populate as needed |
| A11 | Serialization via `to_dict()` / `from_dict()` for persistence | high | fix | Use `model_dump(mode="json")` / `model_validate(json.loads(...))` directly |
| A12 | `EdgesKw` TypedDict + `paginate_results()` utility | high | fix | Replace with `IndexPaginator[T]` + `TimeWindowPaginator[T]` per skill (Avito has two pagination shapes, not GraphQL edges) |

## Patterns from the skill (`aiogram-style-sdk-framework`)

| # | Pattern | Severity | Action | Notes |
|---|---|---|---|---|
| S1 | `BaseMethod[T]` aiogram-style with `__http_method__` + `__endpoint__` + `__returning__` + `__protocol__` | critical | follow | Core contract |
| S2 | `Protocol` ABC + `RestProtocol` as the only concrete impl | critical | follow | GraphQL/JSON-RPC siblings = defer (out of scope) |
| S3 | `BoundModel.as_(client)` — recursive bind, `_require_client` guard | critical | follow | Per `models.md` |
| S4 | `__pre_encoded_fields__` validator enforcement at import time | high | follow | Useful for OAuth state-param + URL-encoded item paths |
| S5 | `BaseSession` funnel — `make_request(client, method)` calls protocol encode/decode | critical | follow | Per `sessions.md` |
| S6 | Three execution surfaces — flat method / `await client(M())` / bound model method | critical | follow | All route through funnel |
| S7 | Shared infrastructure across accounts — session pools, dispatcher, web server, middleware are ONE instance | critical | follow | See `client.md` "Sharing infra" + `dispatcher.md` |
| S8 | `evented` for dispatcher / FSM / web / breaker / token-bucket / idempotency / DLQ | critical | follow | Per `_evented-integration.md`; private dep from `github.com/zlexdev/evented` |
| S9 | `asyncbus` for outbound at-least-once events | n/a | defer | Not needed in v1; users opt-in themselves |
| S10 | `ChallengeSolver` ABC + `NullSolver` default; lazy `playwright`/`twocaptcha`/`capsolver` impls | medium | follow ABC | Avito Partner API has no captcha; ship ABC + NullSolver only, no concrete solvers |
| S11 | `BaseProxyTransport` + `Static/List/Callback` strategies | medium | follow | Realistic for multi-account from different egress IPs |
| S12 | `FakeSession` + `FakeProtocol` + HAR/JSON fixtures + gated live tests | critical | follow | Avito has no sandbox — non-negotiable |
| S13 | `_MODULE.md` per package | high | follow | Per `module-docs.md` |
| S14 | Docstrings inverted policy — every public method-class, model, Client method gets one | critical | follow | Per skill `Docstrings — inverted policy` section |
| S15 | Cookie persistence policy (`manual` / `on_close` / `after_each` with debounce) | medium | follow | OAuth tokens stored via storage; cookies are minimal on Avito (Bearer auth) so this matters less |

## Anti-patterns to avoid

| # | Anti-pattern | Severity | Action |
|---|---|---|---|
| X1 | `client.users.get_self()` / `client.messenger.list_chats()` namespacing | critical | reject — user explicitly wants flat |
| X2 | Empty subsystem stubs (`auth/solvers/twocaptcha.py` with `pass`) | high | reject — only ship a file when its impl is real |
| X3 | Returning `dict` from a Client public method | critical | reject — every public surface is typed |
| X4 | Inline retry/backoff loops sprinkled across method-classes | high | reject — retry lives in `transport/retry.py` + breaker |
| X5 | String literals for chat-state / order-state / message-type | high | reject — `IntEnum` / `StrEnum` per `~/.claude/rules/code-quality.md` |
| X6 | Sync I/O (`requests`, `time.sleep`) anywhere | critical | reject — async-only SDK |
| X7 | Hardcoded API base URL inside method-classes | high | reject — base URLs live in `ClientConfig.hosts` keyed by `__host__` |
| X8 | Bool flag where domain has ≥3 states (e.g. `is_active` while chat has active/archived/blocked) | high | reject — model as `StrEnum` from day one |

## Tech debt in blast radius
Greenfield — no debt to inherit. Wave-1 tasks default to `must-include` for
the audit items tagged `follow` or `fix`.

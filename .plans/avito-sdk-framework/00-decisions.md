# 00 — Decisions (self-answered)

Autonomous mode — every question that would normally hit Checkpoint #1 was
answered by the orchestrator using the research dossier
(`_research/raw/avito-api-surface.md`), the reference SDK
(`_research/raw/plrok-reference.md`), and the framework skill
(`~/.claude/skills/aiogram-style-sdk-framework/`). User overrides any line below.

## Naming + packaging
1. **Package name = `avitoapi`.** Mirrors `PlayerokAPI` shape and is the
   obvious match for the user's request ("по avito"). Reserved on PyPI is
   the user's problem at publish time; if taken, the suggestion is
   `avitoapi-sdk`.
2. **Python = 3.11+.** `Self` type, `tomllib`, `asyncio.TaskGroup`, modern
   `match` — all justified. 3.10 buys nothing, 3.12 forbids nothing.
3. **Repo root = `C:\Users\User\Desktop\avito-bot\`.** Existing `main.py`
   placeholder is replaced by the example bot in `examples/` and a fresh
   `pyproject.toml` is added at root. No worktree (greenfield, not under git).
4. **Build tool = `uv` + `pyproject.toml`.** Faster than poetry, native lockfile.
5. **Lint/types = `ruff` + `mypy --strict`.** Matches user's global rules.

## Wire protocol + transport
6. **REST only.** `Protocol` ABC stays for the contract; `RestProtocol` is
   the single concrete impl. GraphQL/JSON-RPC siblings are not shipped.
7. **HTTP session backend = `curl_cffi`.** Avito gates obvious `python-
   requests` user agents; `curl_cffi` ships browser TLS fingerprints +
   HTTP/2 and is exactly what plrk2 already chose. `httpx` available as
   lazy alt under `[httpx]` extra for environments that can't link
   libcurl-impersonate.
8. **`User-Agent` = `f"avitoapi/{__version__} (+https://github.com/zlexdev/avitoapi)"`.**
   Configurable via `ClientConfig.user_agent`.
9. **Pydantic = v2.** No v1 compatibility shim.

## Auth
10. **OAuth = both grants shipped from Wave 1.** `client_credentials` for
    single-tenant bots, `authorization_code` for multi-tenant dashboards.
    Refresh-on-403 with body containing `token_expired` (Avito quirk).
11. **Token storage** — `BaseStorage` keyed `oauth:{client_id}:{user_id}`.
    TTL recorded; refresh fires when ≤60 s remaining or on 403.
12. **Auth state-param for `authorization_code`** = `secrets.token_urlsafe(32)`,
    one-shot, stored via `storage.namespaced("oauth_state")` with 10-min TTL.

## Rate limiting + reliability
13. **Token-bucket = `evented.TokenBucket`.** 5 rps global default per account,
    1 rps per `(account_id, chat_id)` for messenger sends. Both tunable via
    `ClientConfig`.
14. **Circuit breaker = `evented.CircuitBreaker` keyed by
    `(host, path_template[, account_id])`.** Open after 5 consecutive 5xx,
    half-open probe after 30 s. Account dimension is opt-in via
    `ClientConfig.breaker_per_account: bool = False` (default off — share
    breaker state across accounts since most failures are Avito-side, not
    account-specific).
15. **Retry policy** — exponential with jitter: 0.5s, 1s, 2s, 4s, max 5
    attempts. Honour `Retry-After` header on 429. Idempotent methods only
    (GET / DELETE / explicit-opt-in for POST via `__retry_safe__: bool = False`
    on the method-class).
16. **Idempotency-Key header** — auto-injected by `RestProtocol` for any
    method-class declaring `__idempotent_mutation__: bool = True`. Key =
    `uuid4().hex` on first attempt, reused across retries. Stored in the
    `RequestContext` so retries see the same key.

## Pagination
17. **Two paginator classes ship in Wave 2:** `IndexPaginator[T]` for
    `page`+`per_page` shape (items, reports, reviews) and `TimeWindowPaginator[T]`
    for `date_time_from`/`date_time_to`+offset (messenger chats, calls, CPA).
    Both async-iterable, both runaway-guard via `max_pages` config.

## Storage
18. **Default backend = `MemoryStorage`.** Lazy `redis.py` under `[redis]`
    extra. Lazy `mongo.py` under `[mongo]` extra. Both implement the same
    `BaseStorage[TDoc, TId]` contract.
19. **Storage shared across accounts; per-account namespace via
    `storage.namespaced(f"acc:{account_id}")`.** Per `dispatcher.md`.
20. **Webhook dedup** — `(chat_id, message_id)` TTL set (1h) inside the
    same storage namespace. Survives webhook redelivery.

## Dispatcher / FSM / Web
21. **Use `evented` for Dispatcher/Router/FSM/WebApp/PollingRunner/
    WebhookRunner/BaseMiddleware/MagicFilter.** Pulled as private dep
    `evented @ git+https://${GH_TOKEN}@github.com/zlexdev/evented.git@<TAG>`.
    **Installed in W1** (loose `@master` so FSM in W3 can use it);
    **pinned to a tag in W4** before release-ready cut.
22. **`avitoapi/dispatcher.py`** = thin subclass + `make_dispatcher()` factory.
23. **Events under `avitoapi/events/`** — typed `Event` subclasses:
    `NewMessage`, `MessageRead`, `ChatArchived`, `OrderStatusChanged`
    (poll-only — order events are not push on Avito), etc.
24. **Routers under `avitoapi/routers/`** — `MessengerRouter`, `OrdersRouter`
    each declaring `EventObserver[T]` attributes.
25. **Webhook server backend = `aiohttp` (default).** Lazy `fastapi`/
    `litestar` adapters under their respective extras.
26. **Webhook signature middleware** = `HMACSignatureMiddleware` reading
    `x-avito-messenger-signature`, computing HMAC-SHA256 over raw body with
    the per-webhook secret stored under `webhook:{webhook_id}:secret`.
    Constant-time compare via `hmac.compare_digest`.

## Models + state machines
27. **`models/` split per domain.** One file per: `accounts.py`, `items.py`,
    `messenger.py` (Chat + Message + MessageType), `orders.py`, `reviews.py`,
    `balance.py`, `stats.py`, `promotion.py`, `autoload.py`, `cpa.py`,
    `calltracking.py`, `job.py`, `realty.py`, `autoteka.py`. Plus
    `common.py` (Money, page/cursor wrappers, generic Error).
28. **Message types modeled as discriminated union** (`type` field) per the
    research dossier §2: `text | image | link | item | location | voice |
    call | file | system | appCall | deleted`.
29. **Chat state** = `StrEnum`: `active | archived | blocked`.
30. **Order state** — Avito ships ~7 states per `DBS` flow. Model exactly
    those + transition table; consult `developers.avito.ru` order docs in
    Wave 5 (deferred from Wave 1).

## Optional subsystems shipped vs. deferred
31. **Ship in Wave 1:** `client.py`, `methods/_base.py`, `models/_base.py` +
    `models/common.py`, `models/accounts.py`, `protocol/base.py` +
    `protocol/rest.py`, `sessions/base.py` + `sessions/curl.py`,
    `transport/headers.py` + `transport/retry.py`, `exceptions.py`,
    `config.py`, `logging.py`, `types.py`, `auth/oauth.py`.
32. **Ship in Wave 2:** `pagination/`, `storage/` (memory + redis + mongo),
    `models/items.py` + `methods/items.py`, `models/stats.py` +
    `methods/stats.py`, `models/balance.py` + `methods/balance.py`.
33. **Ship in Wave 3:** `models/messenger.py` + `methods/messenger.py`,
    `fsm/` (re-exported from `evented`), `assets/` (image upload helpers
    + `FileStorage`).
34. **Ship in Wave 4:** `dispatcher.py` factory, `events/`, `routers/`,
    `web.py` re-export, `breaker/` registry shim, full ops scripts, Locust
    load tests, README, `.env.example`, `examples/echo_bot.py`. Release-ready.
35. **Ship in Wave 5:** `models/orders.py` + `methods/orders.py`,
    `models/reviews.py` + `methods/reviews.py`, `models/promotion.py` +
    `methods/promotion.py`, `models/cpa.py` + `methods/cpa.py`,
    `categories/` static UUID maps.
36. **Ship in Wave 6:** `models/autoload.py` + `methods/autoload.py`,
    `models/calltracking.py` + `methods/calltracking.py`,
    `models/job.py` + `methods/job.py`, `models/realty.py` +
    `methods/realty.py`, `models/autoteka.py` + `methods/autoteka.py`.

## Test strategy
37. **`FakeSession`** — implements `BaseSession.make_request` by looking up
    `(method, request_signature)` in a JSON fixtures dir. Records new
    interactions when `AVITOAPI_RECORD=1`.
38. **Live tests** under `tests/live/` gated on `AVITOAPI_LIVE=1` env var.
    Skipped by default — they need real OAuth credentials.
39. **Load tests** — Locust scenarios in `tests/load/` for: OAuth refresh,
    `send_message`, `list_chats` paginator, webhook ingestion under
    concurrent load.

## Concerns deferred to user (none)
None. Every decision above is defensible from research; user reviews at
the end and any of the 39 lines can be overridden.

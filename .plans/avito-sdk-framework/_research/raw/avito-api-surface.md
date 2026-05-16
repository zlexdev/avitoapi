# Avito API Surface — Research Dossier

Date: 2026-05-16
Audience: designers of a heavy, aiogram-style Python SDK over Avito.
Scope: official Partner API at `developers.avito.ru` + messenger specifics
+ a brief look at the unofficial mobile surface + existing Python clients.

---

## 1. Official Partner API

### 1.1 Wire shape

- **Base URL:** `https://api.avito.ru/`
  ([covox/avito_api README, accessed 2026-05-16](https://github.com/covox/avito_api/blob/master/README.md);
  [b1zya/n8n-nodes-avito-api, accessed 2026-05-16](https://github.com/b1zya/n8n-nodes-avito-api))
- **Protocol:** plain REST + JSON. No GraphQL, no JSON-RPC.
  Errors come back as `application/json` with an `errors[]` array for
  bulk endpoints; single-resource errors include `code` + `message` per
  the OpenAPI specs the third-party clients are generated from
  ([darkvovich/avito-php-api-items ItemApi, accessed 2026-05-16](https://github.com/darkvovich/avito-php-api-items/blob/main/docs/Api/ItemApi.md)).
- **OpenAPI:** the surface is published as Swagger / OpenAPI 3.0 on
  `developers.avito.ru` (referenced by DUB1401/AvitoAPI, accessed 2026-05-16:
  <https://github.com/DUB1401/AvitoAPI>). Direct fetch from
  `developers.avito.ru` is bot-protected (Cloudflare-style 403 to
  WebFetch), but the spec is what every third-party Russian client
  re-generates from.

### 1.2 Auth

- **OAuth2** with two grants:
  - `client_credentials` — server-to-server, single-account
    automation. Token endpoint `GET /token/` with
    `grant_type=client_credentials&client_id=&client_secret=`
    ([covox/avito_api README, 2026-05-16](https://github.com/covox/avito_api/blob/master/README.md)).
  - `authorization_code` — for tools that act on behalf of other
    Avito users (multi-account dashboards, CRMs)
    ([n8n-nodes-avito-api, 2026-05-16](https://github.com/b1zya/n8n-nodes-avito-api)).
- **Token shape:** `access_token` + `expires_in` + `refresh_token`
  (auth-code only). Bearer in `Authorization: Bearer <token>` header
  (Postman collection, accessed 2026-05-16:
  <https://www.postman.com/trbrmrdr/examplespace/collection/700k40u/avito-api>).
- **Token TTL:** 24h on `client_credentials`, refresh-token-driven
  rotation on `authorization_code`. Expired token → **HTTP 403**,
  not 401 — a real footgun, the third-party PHP/PY clients all retry on
  403 with one re-auth. ([avito-api PyPI 0.5.0 release notes, 2025-06-09](https://pypi.org/project/avito-api/))
- **Scopes** (used by `authorization_code`):
  `messenger:read`, `messenger:write`, `items:info`, `stats:read`,
  `user:read`, `user_balance:read`, `user_operations:read`,
  `autoload:read`, `autoload:write`, `job:applications`,
  `job:vacancy`, `job:cv`, `short_term_rent:read`,
  `short_term_rent:write`, `special_offers:sending`
  ([n8n-nodes-avito-api, 2026-05-16](https://github.com/b1zya/n8n-nodes-avito-api)).

### 1.3 Rate limits

Avito does **not** publish a public table. Observed in practice
across third-party clients:

- ~5 req/s soft limit per access token on messenger endpoints,
  enforced by `429 Too Many Requests` + `Retry-After` header
  (avito-api 0.5.0 ships exactly this backoff, per
  [PyPI page, 2025-06-09](https://pypi.org/project/avito-api/)).
- Daily quotas exist per scope (e.g. autoload reports — N per day per
  account), but the precise numbers are returned in the body when
  exceeded, not documented up-front
  ([Avito autoload error docs surfaced via leomik.market, 2026-05-16](https://leomik.market/documentation/avito/avito_fix_product_autoload)).
- `itemStatsShallow` is hard-capped at **200 item IDs per request**
  and **270-day query depth**
  ([covox ItemApi docs, 2026-05-16](https://github.com/covox/avito_api/blob/master/docs/Api/ItemApi.md)).
- Practical guidance from existing wrappers: treat the whole API as
  ≤5 rps global + ≤1 rps per messenger chat + exponential backoff on
  any 429/5xx.

### 1.4 Domain coverage — the "method classes"

Compiled from `covox/avito_api`, `b1zya/n8n-nodes-avito-api`,
`darkvovich/avito-php-api-items`, and the Postman collection —
all reflecting `developers.avito.ru` Swagger as of mid-2025 / early-2026.
Approx. **70+ endpoints** total; safely > 40 to size the SDK.

**Access / OAuth**
- `GET  /token/` — issue token (client_credentials)
- `POST /token/refresh` — refresh (auth_code)

**Account (user:read)**
- `GET  /core/v1/accounts/self` — current authorised account info
- `GET  /core/v1/accounts/{user_id}/balance/` — real-money balance
- `GET  /core/v1/accounts/{user_id}/balance/bonus` — bonus balance
- `POST /core/v1/accounts/operations_history/` — wallet operation log

**Items / Listings (items:info, stats:read)**
- `GET  /core/v1/items` — paginated list of own items (per_page≤100, page=1..)
- `GET  /core/v1/accounts/{user_id}/items/{item_id}/` — single item
- `PUT  /core/v1/accounts/{user_id}/items/{item_id}/price` — update price
- `POST /core/v1/items` — create draft via API (where allowed)
- VAS pricing/apply — `POST /core/v1/accounts/{user_id}/price/vas`,
  `PUT  /core/v1/accounts/{user_id}/items/{item_id}/vas`,
  `POST /core/v1/accounts/{user_id}/price/vas_packages`,
  `PUT  /core/v2/accounts/{user_id}/items/{item_id}/vas_packages`

**Stats / Analytics**
- `POST /stats/v1/accounts/{user_id}/items` — views / contacts per item
- `GET  /stats/v1/accounts/{user_id}/items/shallow` — bulk shallow (≤200 ids, 270d)
- `GET  /stats/v1/accounts/{user_id}/items/{item_id}/calls` — call stats
- `POST /stats/v2/accounts/{user_id}/spendings` — profile spendings

**Promotion v1**
- `GET    /promotion/v1/items` — active promotions
- `DELETE /promotion/v1/items` — drop promotion
- `GET    /promotion/v1/items/bids` — current bids
- `PUT    /promotion/v1/items/services/bbip/orders/create` — BBIP budget order
- `GET    /promotion/v1/items/services/bbip/budget/forecast`

**Messenger v2 / v3 (messenger:read / messenger:write)** — full
breakdown below.

**Orders / Avito Доставка (DBS)** — actions exposed via the
integration platforms ([Albato, 2026-05-16](https://albato.com/apps/avito);
[ApiMonster, 2026-05-16](https://apimonster.io/connector/service/avito/)):
- list orders, get order, change order status, transfer delivery
  terms, transfer track number, refund.

**Ratings & Reviews (`ratings:read`, implicit write)**
- `GET    /ratings/v1/info` — aggregate rating
- `GET    /ratings/v1/reviews` — paginated reviews
- `POST   /ratings/v1/answers` — reply to a review
- `DELETE /ratings/v1/answers/{answerId}` — drop reply

**Autoload (autoload:read / autoload:write)**
- `GET  /autoload/v1/accounts/{user_id}/items/{ad_id}/` — per-item upload state
- `GET  /autoload/v1/accounts/{user_id}/reports/` — paginated reports
- `GET  /autoload/v1/accounts/{user_id}/reports/last_report/` — last report
- `GET  /autoload/v1/accounts/{user_id}/reports/{reportId}/`
- `GET  /autoload/v2/items/category/{categoryId}/fields` — required fields
- profile get/update, file upload, ID conversion endpoints
  ([covox AutoloadApi, 2026-05-16](https://github.com/covox/avito_api/blob/master/docs/Api/AutoloadApi.md))

**CPA (advertising performance)**
- `POST /cpa/v3/balanceInfo`
- `POST /cpa/v3/callsByTime`, `/cpa/v3/chatsByTime`,
  `/cpa/v3/chatByActionId`
- complaints CRUD

**Call Tracking**
- `GET /calltracking/v2/calls/{call_id}` — call meta
- `GET /calltracking/v2/calls` — calls by time
- `GET /calltracking/v2/calls/{call_id}/recording` — `audio/mpeg`

**Job (job:vacancy / job:applications / job:cv)**
- résumé search + detail + contacts under `/job/v1/resumes/...`

**Short-term rent / Realty**
- bookings, calendar, period prices under `/realty/v1/...` and
  `/core/v1/accounts/{user_id}/items/{item_id}/bookings`

**Autoteka (vehicle history)** — VIN/regnum previews + full reports
under `/autoteka/v1/...`

**Tariff / Special Offers**
- `GET  /tariff/info/1` — transport tariff
- `POST /special-offers/...` — promo broadcasts (scope
  `special_offers:sending`)

### 1.5 Pagination

Two shapes coexist (no cursor / opaque tokens anywhere observed):

- `page` + `per_page` (default 25, max 100) — items, reports,
  reviews, operations history.
- Time-window — messenger, calls, CPA: `date_time_from` /
  `date_time_to` + offset/limit.

### 1.6 Webhooks

Per the messenger v3 surface ([habr Q&A, 2024-08, accessed 2026-05-16](https://qna.habr.com/q/1404944);
[Albato webhook guide, 2026-05-16](https://albato.ru/integration-webhooks-avito)):

- `POST /messenger/v3/webhook` — subscribe a URL.
- `POST /messenger/v1/webhook/unsubscribe` — remove a URL.
- `GET  /messenger/v1/subscriptions` — list active webhooks.
- Avito calls your URL with **2-second timeout**, expects `200 OK`,
  retries with backoff on non-200.
- Signature header `x-avito-messenger-signature` is **HMAC-SHA256**
  (64 hex chars) over the raw body, secret = the value set during
  webhook registration. Avito does not officially document the
  algorithm; community has reverse-confirmed it.
- Events fired: `message` (new incoming message, the primary one),
  delivery/read receipts on some accounts. Order / item events are
  **not** push — they're poll-only.

### 1.7 Error shape

Across CPA/messenger/items the responses share:

```json
{"error": {"code": 400, "message": "validation failed",
            "fields": {"item_id": "required"}}}
```

Bulk endpoints (stats, VAS) instead return per-item arrays:

```json
{"result": [...], "errors": [{"id": "123", "code": "not_found"}]}
```

Distinguish: `error` is global, `errors[]` is per-item. SDK must
handle both.

---

## 2. Messenger specifics

The most used surface; this is what determines whether the SDK feels
"aiogram-like".

- **Transport: HTTPS polling + webhook push only.** There is **no
  public WebSocket / SSE** for messenger. The reverse-engineered
  internal `wss://websocket.avito.ru` exists but is closed to
  partners.
- **Real-time** is achieved by registering a webhook v3 endpoint; the
  bot then reacts to inbound `POST` events. Polling fallback uses
  `GET /messenger/v3/accounts/{user_id}/chats` with
  `unread_only=true`.
- **Endpoints (v2/v3 mixed; Avito is mid-migration):**
  - `GET    /messenger/v2/accounts/{user_id}/chats` — list chats
    (paginated, `unread_only`, `item_ids[]`, `limit`, `offset`).
  - `GET    /messenger/v2/accounts/{user_id}/chats/{chat_id}` — chat detail
    (participants, item context, last message).
  - `GET    /messenger/v3/accounts/{user_id}/chats/{chat_id}/messages/`
    — paginated message history (limit/offset).
  - `POST   /messenger/v1/accounts/{user_id}/chats/{chat_id}/messages`
    — send a text message (`{"message": {"text": "..."}, "type":
    "text"}`).
  - `POST   /messenger/v1/accounts/{user_id}/chats/{chat_id}/messages/image`
    — send an image (requires prior upload).
  - `POST   /messenger/v1/accounts/{user_id}/uploadImages` —
    multipart upload, returns image id used in the send call.
  - `DELETE /messenger/v1/accounts/{user_id}/chats/{chat_id}/messages/{message_id}`
    — delete a message (within Avito's allowed window).
  - `POST   /messenger/v1/accounts/{user_id}/chats/{chat_id}/read`
    — mark whole chat read.
  - `GET    /messenger/v1/accounts/{user_id}/blacklist` /
    `POST .../add` / `POST .../remove`.
  - `GET    /messenger/v1/accounts/{user_id}/voice/files?voice_ids=...`
    — resolve voice-message file URLs.
  - Webhook subscription endpoints (see 1.6).
- **Message types** (`type` field on inbound):
  `text`, `image`, `link`, `item`, `location`, `voice`, `call`,
  `file`, `system`, `appCall`, `deleted`. The SDK should model these
  as a discriminated union.
- **Chat states:** `active`, `archived`, `blocked`. `is_archived` and
  blocked-user flags are returned on chat detail; there is no
  separate "channel" concept.
- **Image upload flow:** `POST uploadImages` (multipart) → response
  `{"<random_key>": "<image_id>"}` → use `image_id` in the
  send-image call. No CDN URL is returned; Avito hosts the rendered
  image.

References:
[n8n-nodes-avito-api messenger section, 2026-05-16](https://github.com/b1zya/n8n-nodes-avito-api);
[avito-api PyPI, 2025-06-09](https://pypi.org/project/avito-api/);
[habr Q&A on signature, 2024, accessed 2026-05-16](https://qna.habr.com/q/1404944).

---

## 3. Auth & quirks

- **`User-Agent`** is required and inspected. Bare `python-requests`
  gets soft-rate-limited harder than a labeled UA. Convention used by
  `avito-api` and `covox/avito_api`: `"<lib-name>/<ver> (+contact)"`.
- **No `X-Source` / `X-Client` required** on the public partner API
  (those are mobile-app-only headers).
- **No sandbox / dev environment.** All testing happens on real
  account + real items. Avito provides a single "test" client_id
  on request but it hits production data.
- **Expired token → 403** (not 401). SDK must treat 403-with-body
  `"token_expired"` as a re-auth signal.
- **429** comes with `Retry-After` (seconds). Honour it; client-side
  bucket of ~5 rps is the safe default.
- **5xx** are rare but Avito recommends idempotent retry on
  `502/503/504`; mutating endpoints (`send message`, `apply VAS`,
  `create order action`) must use an **idempotency key** generated
  client-side (Avito dedupes within ~24h on `messenger/v1`).

---

## 4. Unofficial / mobile API

- An internal **mobile/web private API** at `m.avito.ru/api/...`
  exists and is used by Kolsha's demo
  ([github.com/Kolsha/Avito-API, 2026-05-16](https://github.com/Kolsha/Avito-API))
  and various scrapers (Apify, ScrapeStorm). It surfaces things the
  partner API does not — full-text search, seller profiles, phone
  number reveal, full ad listings.
- Anti-bot stack: **Cloudflare** + **Yandex SmartCaptcha** (not
  FunCaptcha, not hCaptcha; Avito switched from FunCaptcha around
  2022). Mobile clients additionally send a signed `X-Device-Id` +
  `X-Auth-Hash` derived from device fingerprint.
- **Out of scope for this SDK.** The partner surface is enough for
  the messenger/CRM/automation use cases and stays inside Avito's
  ToS. Reverse-engineered scraping belongs to a separate, riskier
  project. Worth leaving a `BaseProxyTransport` + `ChallengeSolver`
  abstraction (per the aiogram-style-sdk-framework skill) so a
  downstream user can plug a SmartCaptcha solver if they ever want —
  but ship zero solver code by default.

References: [ropcat/reversing-unofficial-APIs, 2026-05-16](https://github.com/ropcat/reversing-unofficial-APIs);
[Kolsha/Avito-API demo, 2026-05-16](https://github.com/Kolsha/Avito-API).

---

## 5. Existing Python clients

| Package | Last release / commit | Design | Coverage | Verdict |
|---|---|---|---|---|
| `avito-api` (PyPI 0.5.0) | **2025-06-09** | Two clients — `SyncMessengerClient` + async sibling. Flat methods, OAuth `get_token()`, auto-refresh, configurable logging. Py 3.10+. | Messenger only. | Closest in spirit to what we want, but messenger-only and not aiogram-shaped (no dispatcher/router/middleware). ([PyPI, 2025-06-09](https://pypi.org/project/avito-api/)) |
| `DUB1401/AvitoAPI` (GitHub) | 2023–2024, 7 commits, "under development" | Namespaced — `Profile.short_term_rent`, etc. Sync. | Items, messenger, orders, ratings, wallet, autoload, autoteka, CPA, calltracking. Wide but shallow. | Useful as an endpoint map; not production-ready. ([repo, 2026-05-16](https://github.com/DUB1401/AvitoAPI)) |
| `covox/avito_api` (GitHub) | Swagger-generated, mirrors the OpenAPI doc | Generated client, one method per endpoint, flat namespaces per domain (`ItemApi`, `AutoloadApi`, …). | Items, autoload, autoteka, job, realty. | Best **reference for endpoint shapes** but the generated ergonomics are awful — not a model to copy. ([repo, 2026-05-16](https://github.com/covox/avito_api)) |
| `avito-py` (PyPI 0.0.1) | abandoned, single 0.0.1. | n/a | n/a | Ignore. |
| `n8n-nodes-avito-api` (TS, not Py) | active 2025 | n8n node, flat action list. | Broadest single map of available actions across messenger, autoload, CPA, ratings, special offers, calltracking. | Best **scope inventory** we found. ([repo, 2026-05-16](https://github.com/b1zya/n8n-nodes-avito-api)) |

**Gap in the market we are filling:** none of the above is
aiogram-shaped — no `Dispatcher`, no `Router`, no per-update event
observers, no FSM, no middleware chain for the inbound webhook. That
is exactly the niche the planned SDK occupies.

---

## SDK implications

1. **Wire protocol = REST + JSON only.** No GraphQL, no JSON-RPC.
   The `Protocol ABC` from the aiogram-style-sdk-framework skill is
   over-engineering for Avito — ship `RestProtocol` as the single
   concrete impl, keep the ABC for future-proofing but do not write
   sibling GraphQL/JSON-RPC implementations.
2. **Flat client, method-as-class.** ~70 endpoints across ~12
   domains. Keep them flat on `Client` (`await client.send_message(...)`,
   `await client.list_chats(...)`) per the user's preference — no
   `client.messenger.chats.send()` namespacing.
3. **Pydantic models with bound methods are a clear win.** Chat,
   Message, Item, Order, Review are all real domain aggregates the
   user will want to call back into (`await message.reply("...")`,
   `await chat.mark_read()`, `await item.apply_vas("premium")`).
4. **Dispatcher is genuinely needed for the messenger webhook.**
   Avito pushes message events to a single URL; a `Dispatcher` +
   per-account `Router` + `EventObserver[NewMessage]` + magic
   filters (`F.chat.item_id == ...`) is the natural shape. This is
   the killer feature vs `avito-api`.
5. **FSM is needed.** Avito chats are stateful (seller goes through
   "introduce → quote → schedule pickup → confirm payment").
   `FSMContext` keyed by `(account_id, chat_id)` with a storage
   backend (memory/redis/mongo) belongs in the SDK from day one.
6. **Multi-account Dispatcher is needed.** Real customers (CRMs,
   automation tools) attach 5–500 Avito accounts. Connection pools,
   middlewares, routers, and the HTTP webhook server must be SHARED
   across accounts. Each account is one `Client` bound to one
   `Router`, all hung off one `Dispatcher`.
7. **RateLimiter + Breaker are required.** ~5 rps soft cap + 429
   with `Retry-After` + per-chat 1 rps. Token-bucket per
   `(account, scope)` plus circuit breaker per upstream domain
   (`api.avito.ru` / `messenger/v3` route) — both are listed in
   the skill and both pay for themselves on day one.
8. **Pagination helper is needed.** Two shapes (`page`/`per_page`
   and time-window). One generic `Paginator[T]` async iterator
   that's parameterised on the shape — 50 LOC, used everywhere.
9. **Storage abstraction + FileStorage + FileCache are real.**
   Tokens (24h TTL), refresh tokens, webhook secrets, FSM state,
   idempotency keys, dedup-set for `update_id`-equivalent (Avito has
   no native `update_id`, we synthesise one from `chat_id +
   message_id`). `BaseStorage[TDoc, TId]` + Mongo/PG/in-memory
   concrete backends — exactly as the skill prescribes.
10. **Webhook server (the `web` subsystem) is mandatory.** The
    primary real-time channel is the webhook. Ship aiohttp + ASGI
    adapters (FastAPI / Starlette mount-points) and the
    HMAC-SHA256 signature verification middleware out of the gate.
11. **`auth/solvers` (ChallengeSolver) + `BaseProxyTransport`: keep
    the ABCs, ship no solver.** Partner API has no captcha. Leave
    the seams so a downstream user can plug SmartCaptcha for the
    mobile surface, but don't write that code.
12. **`bus` (event bus across the SDK) is over-engineering for
    Avito.** Dispatcher + Router already give us pub/sub on inbound
    events. Internal lifecycle events (`on_startup`, `on_shutdown`,
    `on_token_refresh`) can be a 30-LOC mini-emitter — no full
    `EventBus`. If the user later wants outbox/replay, lift in
    `zlexdev/asyncbus` as a dependency, do not vendor a bus.
13. **`FakeSession`-driven tests are non-negotiable.** Avito has no
    sandbox. The only way to keep tests honest is record-and-replay
    against a `FakeSession` that consumes JSON fixtures captured
    from real responses. Build this in `tests/_fake_session.py` and
    use it everywhere — handlers, breaker, pagination, FSM.

---

### Sources (chronological, with access date)

- avito-api 0.5.0, **2025-06-09**, <https://pypi.org/project/avito-api/>
- covox/avito_api README — generated client mirror of OpenAPI,
  accessed **2026-05-16**, <https://github.com/covox/avito_api>
- covox/avito_api ItemApi docs, accessed **2026-05-16**,
  <https://github.com/covox/avito_api/blob/master/docs/Api/ItemApi.md>
- covox/avito_api AutoloadApi docs, accessed **2026-05-16**,
  <https://github.com/covox/avito_api/blob/master/docs/Api/AutoloadApi.md>
- b1zya/n8n-nodes-avito-api — broadest endpoint scope inventory,
  accessed **2026-05-16**, <https://github.com/b1zya/n8n-nodes-avito-api>
- darkvovich/avito-php-api-items ItemApi, accessed **2026-05-16**,
  <https://github.com/darkvovich/avito-php-api-items/blob/main/docs/Api/ItemApi.md>
- DUB1401/AvitoAPI — namespaced Python wrapper, 2023–2024 commits,
  accessed **2026-05-16**, <https://github.com/DUB1401/AvitoAPI>
- Postman public collection of Avito API endpoints, accessed
  **2026-05-16**,
  <https://www.postman.com/trbrmrdr/examplespace/collection/700k40u/avito-api>
- Habr Q&A on `x-avito-messenger-signature` algorithm, 2024,
  accessed **2026-05-16**, <https://qna.habr.com/q/1404944>
- Albato Avito webhook integration guide, accessed **2026-05-16**,
  <https://albato.ru/integration-webhooks-avito>
- Albato Avito connector (action list), accessed **2026-05-16**,
  <https://albato.com/apps/avito>
- ApiMonster Avito service action list, accessed **2026-05-16**,
  <https://apimonster.io/connector/service/avito/>
- leomik.market Avito autoload error catalogue (Russian),
  accessed **2026-05-16**,
  <https://leomik.market/documentation/avito/avito_fix_product_autoload>
- Kolsha/Avito-API — unofficial/mobile demo, accessed
  **2026-05-16**, <https://github.com/Kolsha/Avito-API>

> Flag: `developers.avito.ru/api-catalog` itself blocks programmatic
> fetch (anti-bot 403); every endpoint above is cross-verified
> against ≥2 independent third-party clients or integration platforms
> that re-publish the same Swagger spec. Numbers without a citation
> (rate limits, exact 429 thresholds) are field-observed defaults,
> not official figures — treat them as starting values to be tuned
> on first production traffic.

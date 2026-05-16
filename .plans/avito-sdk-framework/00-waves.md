# Wave Map — avito-sdk-framework

## Goal recap
Build `avitoapi`, an aiogram-style async Python SDK over the Avito Partner
API. Six waves; release-ready at Wave 4 with the full messenger+items+webhook
surface working end-to-end. Waves 5–6 are pure breadth — more method-classes
and models, no new architecture.

"Releasable" for an SDK = a downstream user can install it, instantiate
`Client`, call the documented surface for that wave's domains, and get
typed responses + handle errors. Wave 4 additionally requires Locust
baseline + ops scripts + docs floor (per release-ready criteria in
`00-overview.md`).

## Wave dependency graph
- wave-01 → none
- wave-02 → wave-01
- wave-03 → wave-02
- wave-04 → wave-03
- wave-05 → wave-04
- wave-06 → wave-04   (parallelizable with wave-05 after release-ready)

## Waves

### wave-01 — Skeleton + OAuth + first endpoint
- **Delivers:** Package installs; `Client` boots; OAuth2 `client_credentials`
  flow issues + caches token; first endpoint `client.get_self()` returns
  typed `Account` model bound to the client. End-to-end through the funnel:
  `Client.__call__` → `BaseSession.make_request` → `RestProtocol.build_request`
  → `CurlSession.send` → `RestProtocol.decode_response` → `BoundModel.as_(client)`.
- **Releasable definition:** `pip install -e .` works; `python -c "import
  asyncio, avitoapi; asyncio.run(_main())"` smoke prints account_id from a
  real token; `pytest tests/unit/` green with FakeSession fixtures for
  OAuth + GET /core/v1/accounts/self; `ruff` + `mypy --strict` clean.
- **Estimated size:** ~2.5K LOC (~1.5K production + ~1K tests/fixtures);
  ~28 files; ~10 tasks.
- **Release-ready:** `no` (development scaffolding).
- **Tests:** FakeSession-driven unit tests covering OAuth flow, 403→re-auth,
  Account decode. No live tests required to call the wave done.
- **Scripts:** `scripts/test.sh` (run pytest), `scripts/lint.sh` (ruff + mypy).
- **In-wave hardcodes:**
  - `RestProtocol` is hardwired in `BaseMethod.__protocol__` default →
    closes on its own when Wave 6 ends (no replacement needed; we just want
    the seam to exist).
  - `MemoryStorage` is the only backend → replaced by
    `[redis]`/`[mongo]` extras in **wave-02**.
  - Webhook signature verification stubbed (function exists, no transport
    around it) → wired up in **wave-04**.
- **Out of scope:** anything not OAuth or `get_self` — items, messenger,
  webhook, dispatcher all deferred.

### wave-02 — Items + Stats + Balance + Pagination + Storage backends
- **Delivers:** `list_items`, `get_item`, `update_item_price`, `apply_vas`,
  `item_stats_shallow`, `get_balance`, `get_balance_bonus`,
  `operations_history`. Two paginators (Index for `page`/`per_page`,
  TimeWindow for time-bounded queries). Storage backends: `RedisStorage`
  and `MongoStorage` under extras. Bound methods on `Item`
  (`await item.apply_vas("premium")`, `await item.update_price(123)`).
- **Releasable definition:** Above methods work end-to-end against
  FakeSession fixtures; paginators handle multi-page; `[redis]` extra
  installs and `RedisStorage` round-trips a token; `ruff`+`mypy` clean.
- **Estimated size:** ~3K LOC (~2K production + ~1K tests); ~32 files;
  ~12 tasks.
- **Release-ready:** `no` (no messenger / no webhook yet).
- **Tests:** FakeSession fixtures for items list (multi-page), single item,
  stats bulk, balance. Paginator unit tests + runaway-guard tests.
  Storage round-trip tests with `fakeredis` (no live Redis required).
- **Scripts:** unchanged from W1.
- **In-wave hardcodes:**
  - VAS package IDs hardwired in test fixtures only → no production replacement.
  - Bulk stats request hard-caps `item_ids` at 200 per Avito docs — that's
    correct, not a hardcode to remove.
- **Hardcodes replaced from W1:** Storage backend default still `MemoryStorage`,
  but `[redis]` and `[mongo]` are now wireable — the W1 "memory-only"
  hardcode is now closed via opt-in extras.
- **Out of scope:** messenger, dispatcher, webhook, orders, reviews.

### wave-03 — Messenger + FSM + Assets
- **Delivers:** `list_chats`, `get_chat`, `list_messages`,
  `send_text_message`, `send_image_message`, `mark_chat_read`,
  `delete_message`, `upload_image`, `list_blacklist`, `add_blacklist`,
  `remove_blacklist`, `get_voice_files`. `Chat` + `Message` Pydantic
  models with discriminated union on `Message.type`. `evented.FSMContext`
  re-export + `StorageKey` keyed `(account_id, chat_id)`. `AssetDownloader`
  + `FileStorage` for downloading inbound voice/image URLs.
- **Releasable definition:** All messenger methods work against FakeSession
  fixtures; FSM round-trip test passes; discriminated message-type decoding
  parses all 11 type variants; `ruff`+`mypy` clean.
- **Estimated size:** ~3K LOC (~2K production + ~1K tests); ~24 files;
  ~12 tasks.
- **Release-ready:** `no` (no dispatcher / no webhook yet — bot still
  can't be built on top).
- **Tests:** FakeSession fixtures for all 12 messenger endpoints + 11
  message-type variants. FSM round-trip test. Image-upload multipart
  test.
- **Scripts:** unchanged.
- **In-wave hardcodes:** `Message.type` discriminated union enumerates the
  11 known types — if Avito adds a new type post-W3, decoder gracefully
  falls back to `UnknownMessage` (not a hardcode to remove, just a
  forward-compat hatch).
- **Out of scope:** dispatcher, webhook server, orders, reviews.

### wave-04 — Dispatcher + Webhook + Multi-account + Release-ready
- **Delivers:** `make_dispatcher()` factory wraps `evented.Dispatcher`.
  `MessengerRouter` with `EventObserver[NewMessage]`,
  `EventObserver[MessageRead]`. `WebhookRunner` from `evented` mounted on
  `aiohttp` with `HMACSignatureMiddleware` verifying
  `x-avito-messenger-signature`. Multi-account orchestration — one
  `Dispatcher` feeds N `Client` instances, shared session pool + webhook
  server + middleware. Rate-limiter (`evented.TokenBucket` 5 rps global +
  1 rps per chat). Circuit breaker registry. Idempotency dedup via TTL
  set. Example bot in `examples/echo_bot.py`. Full ops scripts: `install.sh`,
  `update.sh`, `run.sh`, `backup.sh`, `restore.sh`, `rollback.sh`,
  `healthcheck.sh`. Locust load tests in `tests/load/`. `README.md`,
  `.env.example`, `LICENSE`, `CHANGELOG.md`.
- **Releasable definition:** `python examples/echo_bot.py` boots a webhook
  server, registers with Avito (manual webhook URL setup), echoes inbound
  messages on a real account; load tests have documented baseline and
  pass; `scripts/install.sh` brings a fresh host from clone to running
  service; all release-ready exit criteria (see `00-overview.md`) hold.
- **Estimated size:** ~3.5K LOC (~2K production + ~1K tests + ~500 ops
  scripts/docs); ~30 files; ~16 tasks.
- **Release-ready:** **`yes` — production-grade for messenger automation
  + items management.**
- **Tests:** Webhook signature verify (positive + negative), dispatcher
  multi-account routing test, rate-limiter under burst, breaker open/close
  cycle, idempotency dedup on webhook redelivery. Locust scenarios:
  100 concurrent send_message, 1000 webhook events/min, 10 accounts
  each polling list_chats.
- **Scripts:** `scripts/install.sh`, `scripts/update.sh`, `scripts/run.sh`,
  `scripts/backup.sh`, `scripts/restore.sh`, `scripts/rollback.sh`,
  `scripts/healthcheck.sh`, `scripts/lint.sh`, `scripts/test.sh`. All
  idempotent, all with `--dry-run`.
- **In-wave hardcodes:** Locust target rates are baselines, not contracts —
  re-tune on first prod traffic.
- **Hardcodes replaced from earlier:** stubbed HMAC signature verification
  from W1 is now real and wired into the webhook ingestion path.
- **Out of scope:** orders, reviews, autoload, CPA, calltracking, job,
  realty, autoteka — all push to W5/W6 (post-release).

### wave-05 — Orders + Reviews + Promotion + CPA + Categories
- **Delivers:** `list_orders`, `get_order`, `change_order_status`,
  `transfer_delivery_terms`, `transfer_track_number`, `refund_order`.
  `list_reviews`, `reply_to_review`, `delete_review_reply`. Promotion v1
  (bids, BBIP, forecast). CPA v3 (balance, calls/chats by time,
  complaints). `categories/` populated with top-level Avito category UUID
  maps (Vehicles, Realty, Job, etc.).
- **Releasable definition:** All listed methods work against FakeSession
  fixtures; order state-machine test covers the documented transition
  table; review-reply round-trip; `ruff`+`mypy` clean. Post-release wave —
  delivered as a minor version bump.
- **Estimated size:** ~3K LOC (~2K production + ~1K tests); ~28 files;
  ~14 tasks.
- **Release-ready:** `post`.
- **Tests:** FakeSession fixtures for each new endpoint, order
  state-machine invalid-transition raises.
- **Scripts:** unchanged.
- **In-wave hardcodes:** Order state names sourced from Avito docs as of
  research date — if they evolve, model updates via subsequent minor.
- **Out of scope:** autoload, calltracking, job, realty, autoteka.

### wave-06 — Autoload + Calltracking + Job + Realty + Autoteka
- **Delivers:** Remaining domains. `autoload_*` (status, reports, fields,
  profile, file upload). `calltracking_*` (call meta, calls by time, audio
  recording). `job_*` (resume search/detail/contacts). `realty_*`
  (bookings, calendar, period prices). `autoteka_*` (VIN/regnum
  preview, full report). 100% of documented `developers.avito.ru` surface
  covered.
- **Releasable definition:** Every endpoint in §1.4 of the research
  dossier has a corresponding `BaseMethod[T]` subclass, `Client` flat
  method, and Pydantic model in `models/`. FakeSession fixtures for
  each.
- **Estimated size:** ~3.5K LOC (~2.5K production + ~1K tests); ~32 files;
  ~16 tasks.
- **Release-ready:** `post`.
- **Tests:** As above — one fixture per endpoint at minimum.
- **Scripts:** unchanged.
- **In-wave hardcodes:** None new.
- **Out of scope:** Anything not on the documented partner API.

# 00 — Overview

## Goal
Build `avitoapi` — a heavy, aiogram-style async Python SDK over the Avito
Partner API (REST + JSON over `https://api.avito.ru`). Reference style:
`PlayerokAPI` (plrk2). Reference framework doctrine: aiogram-style-sdk-framework
skill at `~/.claude/skills/aiogram-style-sdk-framework/`.

Killer feature vs. existing Python clients (`avito-api`, `DUB1401/AvitoAPI`):
**aiogram-shaped Dispatcher + Router + FSM + multi-account orchestration** for
the messenger webhook surface. None of the existing libraries ship this.

## Mode + tier
- Planning mode: **waves**.
- Complexity tier: **library**.
- Parallelization: **parallel subagents** (W1/W3 fanned out, W2 orchestrator-authored).

## Scope (in)
- Flat `Client` facade — every public method directly on `Client`
  (`client.send_message`, `client.list_items`). NO namespaces.
- `BaseMethod[T]` aiogram-style — every endpoint is a Pydantic v2 class
  with `__http_method__`, `__endpoint__`, `__returning__`, `__protocol__`.
- Per-domain Pydantic models in `models/` — each owns its enums, DTOs, state
  transitions. Response models inherit from `BoundModel` and expose bound
  methods (`await message.reply("...")`, `await chat.mark_read()`).
- Protocol ABC with `RestProtocol` as the only concrete impl (Avito is REST-only).
- OAuth2 — `client_credentials` (single account) + `authorization_code`
  (multi-account dashboards). Auto re-auth on 403 with `token_expired` body.
- Rate-limit (token bucket, 5 rps global + 1 rps per `(account, chat_id)`).
- Circuit breaker per `(host, path_template)`.
- Pagination — two shapes: `page`/`per_page` and time-window. One paginator
  per shape, both async-iterable.
- Storage — generic `BaseStorage[TDoc, TId]` with in-memory + redis + mongo
  (lazy-imported).
- FSM — `evented.FSMContext` keyed by `(account_id, chat_id)`, storage-backed.
- Multi-account Dispatcher via `evented` (private dep `github.com/zlexdev/evented`).
  Shared session pool, shared webhook server, shared middleware, per-account
  cookie jars and storage namespaces.
- Webhook server — `evented.WebhookRunner` with HMAC-SHA256 signature
  verification middleware (`x-avito-messenger-signature`).
- Idempotency — client-side `Idempotency-Key` header on mutating endpoints;
  webhook dedup via `(chat_id, message_id)` TTL set.
- FakeSession-driven tests — Avito has no sandbox, so JSON fixtures
  captured from real responses are the only honest test bed.
- Optional extras: `[redis]`, `[mongo]`, `[fastapi]`, `[litestar]`.

## Scope (out — explicit non-goals)
- Unofficial mobile/web `m.avito.ru` API (Cloudflare + Yandex SmartCaptcha).
  Out of scope. Keep `BaseProxyTransport` + `ChallengeSolver` ABCs as seams;
  ship no captcha solver.
- GraphQL / JSON-RPC protocols. Avito is REST-only; sibling impls left for later.
- Sagas / outbox / EventStore. If a downstream user needs at-least-once event
  emission, they pull `zlexdev/asyncbus` separately; we don't vendor it.
- A Telegram bot built on top — this repo ships the **framework**; example bot
  goes into `examples/`.
- Sync API. Async-only.

## Success criteria
1. `pip install -e .` works on Python 3.11+; `from avitoapi import Client` succeeds.
2. `async with Client(config=ClientConfig(client_id=..., client_secret=...)) as c:
    me = await c.get_self()` — OAuth token issued + cached, first endpoint returns
   a typed `Account` Pydantic model bound to the client.
3. Every domain in §Domain coverage has at least one `BaseMethod[T]` subclass
   + one entry on `Client` + one model file under `models/`.
4. Webhook example (`examples/echo_bot.py`) — subscribes to messenger webhook,
   echoes inbound text messages back. End-to-end smoke against a real account.
5. `ruff check` + `mypy --strict` clean on `avitoapi/`.
6. Test suite green: `pytest tests/` with FakeSession-driven fixtures
   covering: OAuth flow, 429+Retry-After, 403→re-auth, page-paginator,
   time-window-paginator, webhook signature verify, FSM round-trip.
7. `_MODULE.md` exists for every package under `avitoapi/`.

## Release-ready exit criteria
Marked at **Wave 4** (`Release-ready: yes`). All eight bullets per
`~/.claude/rules/workflow.md` waves-mode must hold by end of Wave 4:
- Core user-facing features done: OAuth, items CRUD-read, messenger send/recv,
  webhook ingestion, multi-account dispatch.
- Hardcodes from W1–W3 closed (see hardcode tables per wave file).
- Locust baseline in `tests/load/` for: token issue, send_message, paginator,
  webhook ingestion. Documented numbers + green latest run.
- Operational scripts under `scripts/`: `install.sh`, `update.sh`, `run.sh`,
  `backup.sh`, `restore.sh`, `rollback.sh`. All idempotent.
- Observability: structured logging via `structlog`, `/healthz` on the webhook
  server, metric counters on send/recv/webhook paths.
- Security: secrets in `.env` (gitignored), HMAC signature verified on every
  webhook, OAuth token never logged, rate-limit floor.
- Docs: `README.md` (clone → run), `.env.example`, public API reference auto-
  generated from docstrings.

## Worktree directive
Skip. This is greenfield in an empty repo (`C:\Users\User\Desktop\avito-bot\`
contains only a placeholder `main.py` and no git). Work happens directly in
the root.

## Complexity reference
Total budget: ~18K LOC across all 6 waves (revised after wave-detail
estimates landed; per plan-checker T2). Per-wave: W1 ~2.5K (scaffolding),
W2 ~3K, W3 ~3K, W4 ~3.5K (library + sibling example app), W5 ~3K, W6 ~3.5K.
Waves 5–6 are pure breadth (more method-classes + models, no new
architecture).

**Library-vs-application split.** `avitoapi/` is a pure library: install
via `pip install avitoapi`, no ops baggage. Production-grade deploy
artifacts (systemd, nginx, certbot, Locust, install/update/backup
scripts) live in `examples/echo_bot/` as a sibling subproject in the same
repo. Per plan-checker T1.

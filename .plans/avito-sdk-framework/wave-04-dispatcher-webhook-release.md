# Wave 04 — Dispatcher + Webhook + Multi-account + Release-ready

**Release-ready: YES.** Wave 4 closes every release-ready criterion in
`00-overview.md`. Waves 5–6 are post-release breadth additions.

## Delivers
Multi-account Dispatcher via `evented`, webhook ingestion with HMAC-SHA256
signature verification, rate-limiter + circuit-breaker registries, idempotency
dedup, working `examples/echo_bot.py`, full ops scripts, Locust load tests,
release-ready README + `.env.example` + CHANGELOG + LICENSE.

## Releasable definition
- [ ] `python examples/echo_bot.py` boots a webhook server, registers the
      URL with Avito on first run (one-shot CLI flag), echoes inbound text
      messages on a real account.
- [ ] Multi-account smoke: 3 `Client` instances share one `Dispatcher`,
      one session pool, one webhook server; each routes its own messages
      to its own handlers.
- [ ] HMAC signature verify rejects bad signatures with 401; accepts good
      ones with 200; constant-time compare verified.
- [ ] `evented.TokenBucket` enforces 5 rps global + 1 rps per chat;
      breaker opens after 5 consecutive 5xx.
- [ ] Idempotency dedup: replaying a webhook event with same
      `(chat_id, message_id)` runs the handler once.
- [ ] Locust scenarios in `tests/load/` pass baselines:
      - 100 concurrent send_message ≤ p95 800 ms, error rate ≤ 0.5%.
      - 1000 webhook events/min sustained for 5 min, zero drops.
      - 10 accounts polling list_chats — no breaker trips.
- [ ] `scripts/install.sh` brings a fresh Ubuntu 22.04 host from `git
      clone` to running `systemd` service in one command (interactive
      prompts cached in `~/.avitoapi.conf`).
- [ ] `scripts/update.sh` pulls + redeploys with auto-rollback on
      `healthcheck.sh` failure.
- [ ] `scripts/backup.sh` + `scripts/restore.sh` round-trip Redis +
      MongoDB state.
- [ ] `README.md` walks a new operator from clone to running bot in
      under 15 minutes; `.env.example` lists every required variable.
- [ ] `ruff` + `mypy --strict` + all unit/integration tests green.

## Library-vs-application split (plan-checker T1)
The library (`avitoapi/`) stays pure. Production-grade ops live in
`examples/echo_bot/` as a sibling subproject inside the repo. Users who
`pip install avitoapi` get only the library; users who `git clone` the
repo can run the example bot via the included scripts.

## Logic
- `dispatcher.py` is a **thin** subclass of `evented.Dispatcher` plus
  `make_dispatcher(...)` factory that wires nothing by default.
  Application code (the example bot) composes middlewares on top.

### Load-bearing class signatures

```python
# avitoapi/dispatcher.py
class Dispatcher(evented.Dispatcher):
    """Project-specific Dispatcher subclass. Currently identical to base,
    placeholder for future SDK-wide hooks."""

def make_dispatcher(
    *,
    accounts: list[Client],
    fsm_storage: BaseStorage | None = None,
    idempotency_storage: BaseStorage | None = None,
    dlq: evented.InMemoryDeadLetterQueue | None = None,
    web: evented.WebApp | None = None,
    log_level: str = "INFO",
) -> Dispatcher:
    """Build a Dispatcher attached to the given Client instances. Storage
    backends default to in-memory; pass real backends for multi-process
    deploys."""

# avitoapi/web/middlewares/hmac_signature.py
SecretProvider = Callable[[str], Awaitable[str | None]]

class HMACSignatureMiddleware(evented.BaseMiddleware):
    """Verifies x-avito-messenger-signature (HMAC-SHA256 over raw body).
    Rejects with 401 if mismatch or missing signature."""

    def __init__(
        self,
        secret_provider: SecretProvider,
        *,
        header_name: str = "x-avito-messenger-signature",
        require_signature: bool = True,
    ) -> None: ...

    async def __call__(self, handler, event, data): ...
    @staticmethod
    def _resolve_webhook_id(event) -> str:
        """Map inbound webhook URL path segment → webhook_id used to look up secret."""

# avitoapi/web/middlewares/idempotency.py
class WebhookIdempotencyMiddleware(evented.BaseMiddleware):
    """TTL-bounded dedup on (chat_id, message_id) for the messenger webhook.
    Replays return 200 OK + skip handler."""
    def __init__(
        self, storage: BaseStorage, *, ttl: timedelta = timedelta(hours=1)
    ) -> None: ...

# avitoapi/web/middlewares/fast_return.py  (cheap guard G1 from review)
class WebhookFastReturnMiddleware(evented.BaseMiddleware):
    """Wraps every webhook handler in evented.TaskTracker.spawn(...) so the
    HTTP response can return 200 within Avito's 2 s timeout while the
    handler runs in the background. Default-on in make_dispatcher()."""
    def __init__(self, task_tracker: evented.TaskTracker) -> None: ...

# avitoapi/routers/webhook_handler.py
class AvitoWebhookHandler:
    """Adapter mounted at POST /messenger (configurable). Parses Avito's
    webhook body into a typed NewMessage / MessageRead / ChatArchived
    event and forwards into the Dispatcher."""

    def __init__(
        self, dispatcher: Dispatcher, *, mount_path: str = "/messenger"
    ) -> None: ...

    async def handle(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """Parse → dispatch → return 200 (after fast-return middleware queues work).
        On parse failure: 400 + structured error body (no internal trace)."""
```
- `events/` — typed `Event` hierarchy under `evented.Event`:
  `NewMessage`, `MessageRead`, `ChatArchived`. Each carries
  `(account_id, chat_id, message)` payload.
- `routers/messenger.py` — `MessengerRouter(evented.Router)` with
  `EventObserver[NewMessage]`, `EventObserver[MessageRead]` attributes.
- `web.py` — re-exports `evented.WebhookRunner`, `WebhookConfig`,
  `Webhook` + `AvitoWebhookHandler` adapter that parses Avito's webhook
  body shape into a typed `NewMessage` event.
- `breaker.py` — re-export shim around `evented.CircuitBreaker` with
  Avito-keyed registry helper.
- `auth/oauth.py` — gains webhook-secret storage + register/unsubscribe
  helpers (`POST /messenger/v3/webhook`, `POST /messenger/v1/webhook/unsubscribe`).
- `examples/echo_bot.py` — canonical multi-account bot with `--register`
  one-shot CLI for setting webhook URL.
- `tests/integration/` — runs against `aiohttp.test_utils.TestClient` to
  exercise the real webhook ingestion path.
- `tests/load/` — Locust scenarios.
- Ops scripts via `ops-scripts` skill conventions: idempotent, ANSI-color,
  cached prompts, `--dry-run` flag.

## Files (additions)
```
avitoapi/                       ← PURE LIBRARY
├── dispatcher.py               ← thin subclass + make_dispatcher() factory
├── breaker/
│   ├── __init__.py
│   ├── _MODULE.md
│   └── registry.py             ← BreakerRegistry shim over evented.CircuitBreaker
├── events/
│   ├── __init__.py
│   ├── _MODULE.md
│   └── messenger.py            ← NewMessage, MessageRead, ChatArchived
│                                  (orders events deferred to W5 — Order model lives there)
├── routers/
│   ├── __init__.py
│   ├── _MODULE.md
│   └── messenger.py            ← MessengerRouter
├── web/
│   ├── __init__.py
│   ├── _MODULE.md
│   ├── server.py               ← re-export evented.WebApp + WebhookRunner + WebhookConfig
│   ├── avito_webhook_handler.py
│   └── middlewares/
│       ├── __init__.py
│       ├── _MODULE.md
│       ├── hmac_signature.py
│       ├── idempotency.py
│       └── fast_return.py
└── sessions/middleware/        ← (sessions/middleware.py grows into a package)
    ├── __init__.py
    └── rate_limit.py           ← AvitoRateLimitMiddleware (outbound; wraps evented.TokenBucket)

examples/echo_bot/              ← SIBLING APPLICATION (ops live here)
├── README.md                   ← walkthrough + deploy notes
├── pyproject.toml              ← depends on `avitoapi`
├── echo_bot/__init__.py
├── echo_bot/main.py            ← multi-account bot, --register one-shot CLI
├── echo_bot/dispatcher_factory.py  ← pre-wires HMAC+idempotency+fast_return+ratelimit
├── echo_bot/healthz.py         ← aiohttp /healthz handler
├── .env.example
└── scripts/
    ├── install.sh              ← fresh-host bootstrap (systemd + nginx + certbot)
    ├── update.sh
    ├── run.sh
    ├── backup.sh
    ├── restore.sh
    ├── rollback.sh
    └── healthcheck.sh

tests/                          ← LIBRARY TESTS only (no app integration)
├── integration/
│   ├── test_webhook_handler.py     ← parser + HMAC verify in-process
│   ├── test_multi_account_dispatch.py
│   ├── test_rate_limit_middleware.py
│   ├── test_breaker_registry.py
│   └── test_idempotency_middleware.py

examples/echo_bot/tests/
├── integration/
│   └── test_echo_bot_e2e.py       ← aiohttp TestClient → webhook → handler → 200
└── load/
    ├── locustfile_send.py
    ├── locustfile_webhook.py
    └── locustfile_polling.py
    docs/load-baseline.md           ← documented Locust numbers (per acceptance)

README.md                           ← library quickstart + link to examples/echo_bot
CHANGELOG.md                        ← v0.1.0 release notes
LICENSE                             ← MIT (configurable)
docs/load-baseline.md               ← references examples/echo_bot/tests/load/ output
```

## Tasks
```yaml
- id: W4-T1
  title: "Pull evented as private dep + dispatcher.py factory"
  files: [pyproject.toml, avitoapi/dispatcher.py]
  depends_on: []
  parallelizable: false

- id: W4-T2
  title: "events/ + routers/ packages"
  files: [avitoapi/events/**, avitoapi/routers/**]
  depends_on: [W4-T1]
  parallelizable: true

- id: W4-T3
  title: "middlewares/ — HMAC, rate-limit, idempotency"
  files: [avitoapi/middlewares/**]
  depends_on: [W4-T1]
  parallelizable: true

- id: W4-T4
  title: "web.py + breaker.py re-exports"
  files: [avitoapi/web.py, avitoapi/breaker.py]
  depends_on: [W4-T1]
  parallelizable: true

- id: W4-T5
  title: "auth/oauth.py — webhook register/unsubscribe + secret storage"
  files: [avitoapi/auth/oauth.py]
  depends_on: [W4-T1]
  parallelizable: true

- id: W4-T6
  title: "examples/echo_bot.py"
  files: [examples/**]
  depends_on: [W4-T2, W4-T3, W4-T4, W4-T5]
  parallelizable: false

- id: W4-T7
  title: "ops scripts (install/update/run/backup/restore/rollback/healthcheck)"
  files: [scripts/**]
  depends_on: []
  parallelizable: true

- id: W4-T8
  title: "Integration tests (webhook e2e, multi-account, rate-limit, breaker, idempotency)"
  files: [tests/integration/**]
  depends_on: [W4-T6]
  parallelizable: false

- id: W4-T9
  title: "Locust load tests + baseline doc"
  files: [tests/load/**]
  depends_on: [W4-T6]
  parallelizable: true

- id: W4-T10
  title: "Release docs (README, CHANGELOG, LICENSE, .env.example)"
  files: [README.md, CHANGELOG.md, LICENSE, .env.example]
  depends_on: [W4-T6, W4-T7]
  parallelizable: false

- id: W4-T11
  title: "RELEASE-READY checkpoint — verify all release-ready exit criteria hold"
  files: []
  depends_on: [W4-T8, W4-T9, W4-T10]
  parallelizable: false
```

## Risks
- `evented` private repo access requires `GH_TOKEN`; CI needs the secret
  configured. Document in `README.md` deploy section.
- Avito webhook 2 s timeout. The handler must enqueue work and return
  `200 OK` immediately — heavy lifting goes to a background worker
  inside `evented`'s `TaskTracker`. Document this prominently in the
  echo_bot example so users don't accidentally do blocking work inline.
- Locust baseline numbers are starting points; user retunes on first
  prod traffic.

## Hardcodes introduced
None new (all earlier hardcodes either closed below or carried forward
as explicit configurables).

## Hardcodes replaced
| What | Was in wave | Now backed by |
|---|---|---|
| Webhook signature middleware stubbed | wave-01 | `HMACSignatureMiddleware` in `middlewares/hmac_signature.py` with real HMAC-SHA256 verify |
| FakeSession as only session (in tests) | wave-01 | Gated live integration tests now run against a real local `aiohttp.test_utils.TestClient`-served webhook + real `CurlSession` |

## Acceptance checklist (release-ready exit criteria)
- [ ] All 11 tasks land
- [ ] All core user-facing features done (auth, items read, messenger
      send/recv, webhook ingestion, multi-account dispatch)
- [ ] Earlier-wave hardcodes closed (HMAC verify, sessions)
- [ ] `tests/load/` has Locust scenarios + green baseline run + documented
      numbers in `docs/load-baseline.md`
- [ ] `scripts/install.sh`, `update.sh`, `run.sh`, `backup.sh`,
      `restore.sh`, `rollback.sh` exist, idempotent, `--dry-run` works
- [ ] structlog configured; `/healthz` endpoint live; metric counters on
      send/recv/webhook paths
- [ ] Secrets in `.env` (gitignored); HMAC verified on every webhook;
      token never logged; rate-limit floor enforced
- [ ] `README.md` walks fresh operator clone → running bot; `.env.example`
      complete; public API docs auto-generated from docstrings (mkdocs +
      mkdocstrings)
- [ ] CHANGELOG.md `v0.1.0` entry

# Wave 01 — Skeleton + OAuth + first endpoint

## Delivers
Empty package becomes installable; `Client` boots; OAuth `client_credentials`
flow exchanges (client_id, client_secret) for a bearer token, caches it in
`BaseStorage`, refreshes on 403 with `token_expired`; first end-to-end
endpoint `client.get_self()` returns a fully-typed `Account` Pydantic model
bound to the client. Every layer of the funnel exists in stub-but-real form:
`Client.__call__` → `BaseSession.make_request` → middleware chain →
`RestProtocol.build_request` → `CurlSession.send` → `RestProtocol.decode_response`
→ `BoundModel.as_(client)`.

## Releasable definition
- [ ] `uv pip install -e .` succeeds on Python 3.11+ in a clean venv.
- [ ] `python -c "import avitoapi; print(avitoapi.__version__)"` prints.
- [ ] Smoke (with real creds in `.env`):
  `python -c "import asyncio; from avitoapi import Client, ClientConfig; \
   asyncio.run((lambda: __import__('asyncio').run(Client(config=ClientConfig.from_env()).get_self()))())"`
  returns an `Account` with non-None `id`.
- [ ] `pytest tests/unit/` green with FakeSession fixtures covering:
  - OAuth client_credentials happy path
  - OAuth token cached and reused on second call
  - 403 + `token_expired` → re-auth + retry
  - GET /core/v1/accounts/self decodes into `Account`
  - `BoundModel.as_(client)` attached on response
- [ ] `ruff check avitoapi/ tests/` — zero findings.
- [ ] `mypy --strict avitoapi/` — zero findings.
- [ ] `scripts/test.sh` and `scripts/lint.sh` both succeed.

## Logic

### Layers touched (all new — greenfield)
- `client.py` — flat Client facade, `__call__`, `__aenter__`/`__aexit__`,
  `get_self` method.
- `methods/` — `BaseMethod[T]` + `methods/accounts.py:GetSelf`.
- `models/` — `BoundModel` base + `models/common.py` (Money, Page, Error)
  + `models/accounts.py:Account`.
- `protocol/` — `Protocol` ABC + `RestProtocol` concrete.
- `sessions/` — `BaseSession` funnel + `CurlSession`.
- `transport/` — `headers.py` (UA, Accept) + `retry.py` (RetryPolicy
  frozen dataclass).
- `auth/` — `oauth.py` (OAuth2 client_credentials + authorization_code helpers,
  token cache, refresh-on-403 detection) + `solvers/base.py` (ChallengeSolver
  ABC + NullSolver — seam only, no concrete solvers).
- `utils/proxy/` — `BaseProxyTransport` ABC + `NoProxyTransport` (seam only).
- `storage/` — `BaseStorage[TDoc, TId]` ABC + `MemoryStorage` only.
- `exceptions.py`, `config.py`, `logging.py`, `types.py`.

### Dependencies (W1 pyproject)
- Runtime: `pydantic>=2.6`, `curl_cffi>=0.7`, `structlog>=24`,
  `evented @ git+https://${GH_TOKEN}@github.com/zlexdev/evented.git@master`
  (loose master pin in W1; tag pin in W4 before release).
- Dev extras: `pytest`, `pytest-asyncio`, `ruff`, `mypy`, `fakeredis`,
  `mongomock`, `httpx` (fallback).
- Optional extras (declared, no code yet): `[redis]`, `[mongo]`,
  `[fastapi]`, `[litestar]`, `[playwright]`, `[twocaptcha]`, `[capsolver]`.

### Data flow (single request)
1. User: `await client.get_self()`.
2. `Client.get_self` → `await self(GetSelf())`.
3. `Client.__call__(method)` → `method.as_(self).emit(self)`.
4. `BaseMethod.emit` → `client.session.make_request(client, self)`.
5. `BaseSession.make_request`:
   a. Run request-side middleware chain (auth-injector adds `Authorization:
      Bearer <token>`, idempotency-key middleware NO-OPs for GET).
   b. `protocol.build_request(method, context)` → `PreparedRequest`.
   c. Subclass `CurlSession.send(prepared)` → `RawResponse`.
   d. On 4xx/5xx: `_should_retry` → backoff → maybe re-auth → retry.
   e. `protocol.decode_response(method, raw)` → typed `T`.
   f. If `T` is `BoundModel`: `result.as_(client)` (recursive).
6. User receives `Account` with `_client` attached.

### OAuth refresh-on-403 (Avito quirk)
- Treat `403` with response body containing `"token_expired"` as a re-auth
  signal (not as a permission error). One re-auth, one retry, then raise.
- `OAuthInjectorMiddleware` reads cached token from storage; if missing or
  age > `expires_in - 60s`, issues new one. Holds a `asyncio.Lock` per
  `(client_id, user_id)` to prevent thundering-herd refresh on cold start.

## Files

```
avito-bot/
├── pyproject.toml              ← uv-managed, py3.11+, deps: pydantic v2,
│                                  curl_cffi, structlog. Extras: [redis],
│                                  [mongo], [fastapi], [litestar], [dev].
├── .env.example                ← AVITO_CLIENT_ID, AVITO_CLIENT_SECRET, etc.
├── .gitignore                  ← .env, __pycache__, dist/, .venv/, .pytest_cache/
├── README.md                   ← stub: "Wave 1 — see .plans/avito-sdk-framework/"
├── main.py                     ← keep placeholder; will become example bot in W4
├── scripts/
│   ├── test.sh                 ← `set -euo pipefail; uv run pytest tests/`
│   └── lint.sh                 ← `set -euo pipefail; uv run ruff check . && uv run mypy --strict avitoapi/`
├── avitoapi/
│   ├── __init__.py             ← re-exports: Client, ClientConfig, Account, exceptions; __version__
│   ├── _MODULE.md              ← top-level package contracts
│   ├── client.py               ← Client facade, get_self, lifecycle, __call__
│   ├── config.py               ← ClientConfig (BaseModel, .from_env() helper)
│   ├── exceptions.py           ← SDKError hierarchy + http_error_for_status
│   ├── types.py                ← HostKey, BreakerKey, HealthStatus, RawResponse view
│   ├── logging.py              ← structlog config + redaction processor
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── _MODULE.md
│   │   └── oauth.py            ← OAuthClient (client_credentials + auth_code),
│   │                              TokenCache (BaseStorage-backed),
│   │                              OAuthInjectorMiddleware,
│   │                              is_token_expired_403(body) heuristic
│   ├── methods/
│   │   ├── __init__.py
│   │   ├── _MODULE.md
│   │   ├── _base.py            ← BaseMethod[T] aiogram-style; .as_(client); emit;
│   │   │                          __init_subclass__ guards (per skill methods.md)
│   │   └── accounts.py         ← GetSelf(BaseMethod[Account])
│   ├── models/
│   │   ├── __init__.py
│   │   ├── _MODULE.md
│   │   ├── _base.py            ← BoundModel(BaseModel) — .as_(client) +
│   │   │                          _require_client + recursive bind
│   │   ├── common.py           ← Money(amount: Decimal, currency: StrEnum),
│   │   │                          Page generic, AvitoErrorBody
│   │   └── accounts.py         ← Account(BoundModel) with id, name, email,
│   │                              phone, profile_url
│   ├── protocol/
│   │   ├── __init__.py
│   │   ├── _MODULE.md
│   │   ├── base.py             ← Protocol ABC: validate_subclass,
│   │   │                          build_request, decode_response, is_idempotent
│   │   └── rest.py             ← RestProtocol — verb routing, path-templating,
│   │                              JSON encode/decode, Idempotency-Key injection
│   ├── sessions/
│   │   ├── __init__.py
│   │   ├── _MODULE.md
│   │   ├── base.py             ← BaseSession ABC + make_request funnel
│   │   ├── _models.py          ← PreparedRequest, RawResponse, RequestContext (slots)
│   │   ├── middleware.py       ← RequestMiddleware ABC + Manager
│   │   └── curl.py             ← CurlSession (curl_cffi.requests.AsyncSession)
│   ├── transport/
│   │   ├── __init__.py
│   │   ├── _MODULE.md
│   │   ├── headers.py          ← build_default_headers(config)
│   │   └── retry.py            ← RetryPolicy frozen dataclass + should_retry()
│   └── storage/
│       ├── __init__.py
│       ├── _MODULE.md
│       ├── base.py             ← BaseStorage[TDoc, TId] ABC + namespaced()
│       └── memory.py           ← MemoryStorage
└── tests/
    ├── __init__.py
    ├── conftest.py             ← FakeSession fixture, sample fixtures loader
    ├── fixtures/
    │   ├── oauth_token.json
    │   ├── oauth_token_expired.json
    │   └── accounts_self.json
    ├── _fake_session.py        ← FakeSession(BaseSession) — JSON-fixture lookup
    └── unit/
        ├── test_oauth.py       ← token issue, cache, refresh-on-403
        ├── test_client.py      ← Client.__call__, lifecycle, get_self
        ├── test_protocol_rest.py
        ├── test_methods_base.py ← BaseMethod.__init_subclass__ guards
        └── test_models_base.py ← BoundModel.as_ + recursive bind
```

## Types

### Public API surface (W1)
- `avitoapi.Client` — facade, `async with` context manager, `get_self()`,
  `__call__(method)`.
- `avitoapi.ClientConfig` — Pydantic BaseModel. Full field list:
  ```python
  class ClientConfig(BaseModel):
      model_config = ConfigDict(strict=True, frozen=False, extra="forbid")

      # auth
      client_id: str
      client_secret: SecretStr
      user_id: int | None = None                    # required for auth_code grant
      redirect_uri: HttpUrl | None = None
      oauth_grant_endpoint: Literal["post_form", "get_query"] = "post_form"

      # hosts (logical key → base URL)
      hosts: dict[HostKey, HttpUrl] = Field(default_factory=lambda: {
          HostKey("www"):     HttpUrl("https://api.avito.ru"),
      })

      # transport
      user_agent: str = f"avitoapi/{__version__} (+https://github.com/zlexdev/avitoapi)"
      request_timeout_s: float = 30.0
      max_retries: int = 5
      backoff_initial_s: float = 0.5
      backoff_max_s: float = 30.0

      # rate-limit (per decisions §13)
      rate_limit_global_rps: float = 5.0
      rate_limit_per_chat_rps: float = 1.0

      # breaker
      breaker_fail_threshold: int = 5
      breaker_open_seconds: float = 30.0
      breaker_per_account: bool = False

      # webhook (used in W4 but knob ships in W1 so we don't churn config later)
      webhook_signature_header: str = "x-avito-messenger-signature"

      # categories (R11 hedge — Avito uses integer category_id, NOT UUID)
      category_overrides: dict[str, int] = Field(default_factory=dict)

      # cookies / token persistence
      cookie_persistence: Literal["manual", "on_close", "after_each"] = "on_close"

      @classmethod
      def from_env(cls, prefix: str = "AVITO_") -> ClientConfig: ...
  ```
- `avitoapi.Account` — Pydantic BoundModel; fields `id: int`, `name: str`,
  `email: str | None`, `phone: str | None`, `profile_url: str`.
- `avitoapi.exceptions.*` — `SDKError` (root), `AuthError`, `RateLimitedError`
  (carries `retry_after_s: float`), `ForbiddenError`, `NotFoundError`,
  `ValidationError`, `ServerError`, `MethodNotBoundError`,
  `MethodDeclarationError`, `ProtocolError`, `ResponseDecodingError`.
- `avitoapi.types.HostKey = NewType("HostKey", str)`,
  `avitoapi.types.HealthStatus`.

### Method-classes (W1)
- `methods.accounts.GetSelf(BaseMethod[Account])`:
  - `__http_method__ = "GET"`
  - `__endpoint__ = "/core/v1/accounts/self"`
  - `__returning__ = Account`
  - no body / no query / no path fields

### Models (W1)
- `models.accounts.Account(BoundModel)` — fields per Avito Swagger
  `/core/v1/accounts/self` response: `id: int`, `name: str`,
  `email: EmailStr | None`, `phone: str | None`, `profile_url: HttpUrl`.
  No bound methods in W1 (those land in W2 when items/balance arrive).

### `BaseMethod[T]` (per skill `methods.md`)
- `model_config = ConfigDict(strict=True)`
- ClassVars: `__host__`, `__returning__`, `__protocol__`, `__breaker_path__`,
  `__http_method__`, `__endpoint__`, `__path_fields__`, `__query_fields__`,
  `__body_fields__`, `__pre_encoded_fields__`, `__idempotent_mutation__`,
  `__retry_safe__`.
- `_client: Any = PrivateAttr(default=None)`.
- `as_(client) -> Self`, `emit(client) -> T`, `__await__`.
- `__init_subclass__`: protocol validates required class-vars; bans
  `__path__`; resolves `__returning__` from Generic param.

### `BoundModel` (per skill `models.md`)
- `model_config = ConfigDict(strict=True, populate_by_name=True)`.
- `_client: Any = PrivateAttr(default=None)`.
- `as_(client) -> Self` — sets `_client` + recursively binds any field
  that is also a `BoundModel` (including inside `list`s and `dict`s).
- `_require_client()` — raises `MethodNotBoundError` if `_client is None`.

### `Protocol` ABC (per skill `protocol.md`)
- `validate_subclass(cls: type[BaseMethod]) -> None` (raise on missing class-vars).
- `build_request(method, ctx) -> PreparedRequest`.
- `decode_response(method, raw) -> Any`.
- `is_idempotent(method) -> bool`.

### `OAuthClient` (auth/oauth.py)
```python
class Token(BaseModel):
    access_token: SecretStr
    token_type: Literal["Bearer"] = "Bearer"
    expires_at: datetime          # absolute, UTC
    refresh_token: SecretStr | None = None
    scope: frozenset[str] = frozenset()

class TokenCache:
    def __init__(self, storage: BaseStorage) -> None: ...
    async def get(self, key: str) -> Token | None: ...
    async def put(self, key: str, token: Token) -> None: ...
    async def invalidate(self, key: str) -> None: ...

class OAuthClient:
    def __init__(
        self,
        config: ClientConfig,
        http: BaseSession,
        cache: TokenCache,
    ) -> None: ...
    async def issue_client_credentials(self) -> Token: ...
    async def issue_authorization_code(
        self, code: str, *, state: str
    ) -> Token: ...
    async def refresh_if_needed(self, token: Token) -> Token:
        """Refresh when ≤60s remaining or already expired; else return as-is."""

    @staticmethod
    def is_token_expired_403(body: bytes | str) -> bool:
        """Match Avito's 403 + 'token_expired' body heuristic."""

class OAuthInjectorMiddleware:
    """Request-side middleware. Looks up token in cache, refreshes,
    injects ``Authorization: Bearer <token>``. Re-auths on 403+token_expired
    once per request, then surfaces failure."""
    def __init__(self, oauth: OAuthClient, cache_key_builder: Callable[[Client], str]) -> None: ...
```

### `ChallengeSolver` ABC (auth/solvers/base.py — seam only)
```python
class ChallengeRequest(BaseModel):
    kind: str
    page_url: HttpUrl
    site_key: str | None = None

class ChallengeSolution(BaseModel):
    token: str
    metadata: dict[str, str] = Field(default_factory=dict)

class ChallengeSolver(ABC):
    @abstractmethod
    async def solve(self, request: ChallengeRequest) -> ChallengeSolution: ...

class NullSolver(ChallengeSolver):
    async def solve(self, request: ChallengeRequest) -> ChallengeSolution:
        raise NotImplementedError(
            "Avito Partner API does not require captcha. Install an extra "
            "([playwright]/[twocaptcha]/[capsolver]) and inject a real solver "
            "to handle mobile/web surface."
        )
```

### `BaseProxyTransport` ABC (utils/proxy/_base.py — seam only)
```python
class Proxy(BaseModel):
    url: AnyUrl
    label: str | None = None

class ProxyAcquireContext:
    """Async context manager returned by `BaseProxyTransport.acquire`.
    On exit, the transport learns whether the call succeeded so
    rotation strategies can react."""
    proxy: Proxy | None
    def mark_invalid(self) -> None: ...
    async def __aenter__(self) -> Proxy | None: ...
    async def __aexit__(self, *exc_info) -> None: ...

class BaseProxyTransport(ABC):
    @abstractmethod
    def acquire(self, *, account_id: str | None = None, host: str | None = None) -> ProxyAcquireContext: ...

class NoProxyTransport(BaseProxyTransport):
    """Default. Yields None — direct connection."""
```

## Tasks

```yaml
- id: W1-T1
  title: "Bootstrap pyproject + lint/test scripts + .env.example + .gitignore"
  files:
    - pyproject.toml
    - .gitignore
    - .env.example
    - README.md
    - scripts/test.sh
    - scripts/lint.sh
  depends_on: []
  parallelizable: true
  notes: |
    pyproject deps: pydantic>=2.6, curl_cffi>=0.7, structlog>=24.
    dev: pytest, pytest-asyncio, ruff, mypy, types-* as needed.
    extras: [redis] (redis>=5), [mongo] (motor>=3), [fastapi] (fastapi),
            [litestar] (litestar), [dev] (everything above).

- id: W1-T2
  title: "Write avitoapi/config.py, exceptions.py, types.py, logging.py"
  files:
    - avitoapi/__init__.py
    - avitoapi/config.py
    - avitoapi/exceptions.py
    - avitoapi/types.py
    - avitoapi/logging.py
    - avitoapi/_MODULE.md
  depends_on: [W1-T1]
  parallelizable: true

- id: W1-T3
  title: "Storage layer: BaseStorage ABC + MemoryStorage"
  files:
    - avitoapi/storage/__init__.py
    - avitoapi/storage/base.py
    - avitoapi/storage/memory.py
    - avitoapi/storage/_MODULE.md
  depends_on: [W1-T2]
  parallelizable: true

- id: W1-T4
  title: "Protocol layer: Protocol ABC + RestProtocol"
  files:
    - avitoapi/protocol/__init__.py
    - avitoapi/protocol/base.py
    - avitoapi/protocol/rest.py
    - avitoapi/protocol/_MODULE.md
  depends_on: [W1-T2]
  parallelizable: true

- id: W1-T5
  title: "Transport: headers + RetryPolicy"
  files:
    - avitoapi/transport/__init__.py
    - avitoapi/transport/headers.py
    - avitoapi/transport/retry.py
    - avitoapi/transport/_MODULE.md
  depends_on: [W1-T2]
  parallelizable: true

- id: W1-T6
  title: "Sessions: BaseSession funnel + RequestMiddleware + CurlSession"
  files:
    - avitoapi/sessions/__init__.py
    - avitoapi/sessions/_models.py
    - avitoapi/sessions/middleware.py
    - avitoapi/sessions/base.py
    - avitoapi/sessions/curl.py
    - avitoapi/sessions/_MODULE.md
  depends_on: [W1-T4, W1-T5]
  parallelizable: false

- id: W1-T7
  title: "Methods + Models base classes + Account model + GetSelf method"
  files:
    - avitoapi/methods/__init__.py
    - avitoapi/methods/_base.py
    - avitoapi/methods/accounts.py
    - avitoapi/methods/_MODULE.md
    - avitoapi/models/__init__.py
    - avitoapi/models/_base.py
    - avitoapi/models/common.py
    - avitoapi/models/accounts.py
    - avitoapi/models/_MODULE.md
  depends_on: [W1-T4]
  parallelizable: true

- id: W1-T8
  title: "Auth: OAuthClient + TokenCache + OAuthInjectorMiddleware + ChallengeSolver ABC + Proxy ABC"
  files:
    - avitoapi/auth/__init__.py
    - avitoapi/auth/oauth.py
    - avitoapi/auth/_MODULE.md
    - avitoapi/auth/solvers/__init__.py
    - avitoapi/auth/solvers/base.py
    - avitoapi/auth/solvers/_MODULE.md
    - avitoapi/utils/__init__.py
    - avitoapi/utils/_MODULE.md
    - avitoapi/utils/proxy/__init__.py
    - avitoapi/utils/proxy/_base.py
    - avitoapi/utils/proxy/_MODULE.md
  depends_on: [W1-T3, W1-T6, W1-T7]
  parallelizable: false

- id: W1-T9
  title: "Client facade + get_self end-to-end + re-export public API"
  files:
    - avitoapi/client.py
    - avitoapi/__init__.py     # update with full re-exports
  depends_on: [W1-T6, W1-T7, W1-T8]
  parallelizable: false

- id: W1-T10
  title: "Test suite: FakeSession + fixtures + unit tests"
  files:
    - tests/__init__.py
    - tests/conftest.py
    - tests/_fake_session.py
    - tests/fixtures/oauth_token.json
    - tests/fixtures/oauth_token_expired.json
    - tests/fixtures/accounts_self.json
    - tests/unit/test_oauth.py
    - tests/unit/test_client.py
    - tests/unit/test_protocol_rest.py
    - tests/unit/test_methods_base.py
    - tests/unit/test_models_base.py
  depends_on: [W1-T9]
  parallelizable: false
```

## Idempotency-key persistence (cheap guard G4 from review)
`RestProtocol` injects `Idempotency-Key` header for any method-class
declaring `__idempotent_mutation__: bool = True`. Key generation:

```python
async def _idempotency_key(self, method: BaseMethod, ctx: RequestContext) -> str:
    body_hash = hashlib.sha256(
        method.model_dump_json(exclude={"_client"}).encode()
    ).hexdigest()[:16]
    cache_key = f"idemp:{type(method).__name__}:{body_hash}"
    store = ctx.client.storage.namespaced("idempotency")
    cached = await store.get(cache_key)
    if cached:
        return cached
    key = uuid4().hex
    await store.put(cache_key, key, ttl=timedelta(hours=24))
    return key
```

5 lines on top of skeleton infrastructure; survives process restart per
risk R7.

## curl_cffi → httpx fallback (cheap guard G7)
`sessions/__init__.py` exposes `create_default_session(config, *, proxy_transport=None) -> BaseSession`:

```python
def create_default_session(config, *, proxy_transport=None):
    try:
        from .curl import CurlSession
    except ImportError:
        from .httpx_session import HttpxSession
        log.warning("curl_cffi unavailable; falling back to httpx (no TLS spoofing)")
        return HttpxSession(config=config, proxy_transport=proxy_transport or NoProxyTransport())
    return CurlSession(config=config, proxy_transport=proxy_transport or NoProxyTransport())
```

`HttpxSession` ships as stub in W1 (~30 LOC) — same `BaseSession` contract,
no TLS impersonation, behind `[httpx]` extra.

## Risks
- **`curl_cffi` install on Windows.** Wheels exist for Python 3.11/3.12 on
  win_amd64 (per curl_cffi PyPI page). If the user's env hits a build
  failure, fall back to `httpx` lazy session in W1 and revisit. Mitigate
  by leaving `httpx` as an optional extra from day one.
- **OAuth token endpoint URL is undocumented for `client_credentials` in
  many third-party clients.** Two candidates seen: `GET /token/` with query
  params (covox) vs. `POST /token` form-encoded (avito-api). W1 ships **both
  paths under a feature flag** `ClientConfig.oauth_grant_endpoint: Literal[
  "get_query", "post_form"] = "post_form"` (post_form is more standards-
  compliant and matches `avito-api` 0.5.0 from 2025-06). User can flip
  if their account hits the GET variant.
- **`developers.avito.ru` blocks programmatic fetch.** Cannot pull Swagger
  at build time. Accept that — every endpoint shape is hand-transcribed
  from third-party clients, double-checked across at least two sources.
- **Live smoke test cannot run in CI by default.** Gate behind `AVITOAPI_LIVE=1`.
  Wave 1 declares "FakeSession unit tests green" as the bar; first live
  smoke happens on the user's machine.

## Hardcodes introduced
| What | Where | Replaced in wave |
|---|---|---|
| `MemoryStorage` is the only storage backend | `avitoapi/storage/` | wave-02 |
| OAuth endpoint flavor flag defaults to `post_form` | `config.py` | none (configurable, user-tunable; not a true hardcode) |
| FakeSession is the only test session backend | `tests/_fake_session.py` | wave-04 (gated live tests) |
| Webhook signature middleware stubbed but not wired | n/a — not present in W1 | wave-04 |

## Hardcodes replaced
None (this is the first wave).

## Acceptance checklist
- [ ] All 10 tasks land + their files exist
- [ ] `uv pip install -e .` succeeds
- [ ] `scripts/lint.sh` exits 0
- [ ] `scripts/test.sh` exits 0 with 100% of unit tests passing
- [ ] `python -c "from avitoapi import Client, ClientConfig, Account; print(Account.__name__)"` works
- [ ] Smoke (manual, with real creds): `client.get_self()` returns Account
      with non-empty `id`
- [ ] Every package has `_MODULE.md`
- [ ] No `TODO` / `FIXME` / commented-out code in shipped files

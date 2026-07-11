# avitoapi/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

> avitoapi — aiogram-style async SDK over the Avito Partner API.

## Submodules

- [`_backup_handwritten/`](_backup_handwritten\_MODULE_AUTO.md) (54 py, 343 cls, 12 fn)
- [`assets/`](assets\_MODULE_AUTO.md) — Asset (image / voice) download and caching subsystem. (5 py, 6 cls)
- [`auth/`](auth\_MODULE_AUTO.md) — Authentication helpers. See ``_MODULE.md``. (1 py, 4 cls, 1 fn)
- [`breaker/`](breaker\_MODULE_AUTO.md) — Circuit breaker registry — keyed by ``(host, path, account_id)``. (1 py, 4 cls)
- [`channels/`](channels\_MODULE_AUTO.md) — Push channels — bounded producer→dispatcher pipes with an overflow policy. (3 py, 6 cls)
- [`codegen/`](codegen\_MODULE_AUTO.md) — avitoapi codegen — the auto-builder. (16 py, 18 cls, 81 fn)
- [`enums/`](enums\_MODULE_AUTO.md) — Auto-generated domain enums — one module per Avito API domain (see ``avitoapi.codegen``). (25 py, 479 cls)
- [`events/`](events\_MODULE_AUTO.md) — Typed Avito events flowing through the Dispatcher. (10 py, 56 cls)
- [`fanout/`](fanout\_MODULE_AUTO.md) — Fanout — merge many supervised event sources into one dispatcher. (3 py, 6 cls)
- [`fsm/`](fsm\_MODULE_AUTO.md) — FSM primitives — in-package implementation, no external dependency. (2 py, 9 cls)
- [`idempotency/`](idempotency\_MODULE_AUTO.md) — Accept-once idempotency: :class:`IdempotencyStore` + event-level :class:`DedupFilter`. (2 py, 2 cls, 1 fn)
- [`methods/`](methods\_MODULE_AUTO.md) — Per-domain method-classes. See ``_MODULE.md``. (26 py, 247 cls)
- [`models/`](models\_MODULE_AUTO.md) — Per-domain Pydantic response DTOs. See ``_MODULE.md``. (29 py, 1486 cls, 3 fn)
- [`pagination/`](pagination\_MODULE_AUTO.md) — Declarative pagination — methods carry pagination fields, ``Client`` auto-dispatches. (2 py, 6 cls, 1 fn)
- [`protocol/`](protocol\_MODULE_AUTO.md) — Wire-protocol abstraction. See ``_MODULE.md``. (2 py, 2 cls)
- [`queue/`](queue\_MODULE_AUTO.md) — Persistent event queue with at-least-once delivery + lease semantics. (6 py, 15 cls, 4 fn)
- [`routers/`](routers\_MODULE_AUTO.md) — Aiogram-style single ``Router`` — every event as a named observer attribute. (5 py, 10 cls, 4 fn)
- [`sessions/`](sessions\_MODULE_AUTO.md) — Session funnel + concrete backends. See ``_MODULE.md``. (9 py, 13 cls, 6 fn)
- [`storage/`](storage\_MODULE_AUTO.md) — Generic K/V storage layer. See ``_MODULE.md`` for the contract. (5 py, 6 cls)
- [`transport/`](transport\_MODULE_AUTO.md) — Transport-layer helpers (headers, retry policy). See ``_MODULE.md``. (7 py, 15 cls, 15 fn)
- [`web/`](web\_MODULE_AUTO.md) — Webhook server bits — multi-backend WebApp/Runner + Avito adapter. (10 py, 19 cls, 3 fn)

## __init__.py
```
# avitoapi — aiogram-style async SDK over the Avito Partner API.


```

## categories.py
```
# Static Avito category-id catalogue.


cls Vehicles(IntEnum): CARS, MOTORCYCLES, TRUCKS
  # Subset of the Vehicles tree. Values are integer category ids.

cls Realty(IntEnum): FLATS, HOUSES, COMMERCIAL
  # Subset of the Realty tree.

cls Job(IntEnum): VACANCIES, RESUMES
  # Subset of the Job tree.

cls Services(IntEnum): SERVICES
  # Subset of the Services tree.

cls Electronics(IntEnum): PHONES, LAPTOPS
  # Subset of the Electronics tree.

cls Hobbies(IntEnum): BOOKS
  # Subset of the Hobbies tree.

```

## client.py
```
# Flat ``Client`` facade — every Avito Partner API method bound directly here.

TR = TypeVar('TR')

cls Client(AccountsHierarchyFacade, AdsFacade, AuctionFacade, AuthFacade, AutoloadFacade, AutostrategyFacade, AutotekaFacade, AvitoPromoFacade, CalltrackingFacade, CpaFacade, CpxpromoFacade, DeliveryFacade, ItemsFacade, JobFacade, MessengerFacade, OrderManagementFacade, PromotionFacade, RealtyReportsFacade, ReviewsFacade, ShortTermRentalFacade, SpecialOffersFacade, StockManagementFacade, TariffFacade, TrxpromoFacade, UserFacade)
  __init__() -> None
  async open() -> None
    # Initialise pooled resources. Idempotent.
  async close() -> None
    # Tear down session + storage. Idempotent.
  request_middlewares() -> RequestMiddlewareManager
    # Manager for request-side middlewares (auth, tracing, custom logging).
  oauth() -> OAuthClient
    # Direct access to the OAuth client (for one-off ``authorization_code`` flows).
  async healthcheck() -> HealthStatus
    # Aggregate health: storage round-trip + session liveness.

```

## config.py
```
# Per-client configuration. Strict Pydantic model with ``.from_env()`` loader.

DEFAULT_USER_AGENT = …

cls ClientConfig(BaseModel)
  from_env(prefix: str = 'AVITO_') -> Self
    # Build a config from ``{prefix}*`` env vars (default prefix ``AVITO_``).
  base_url(host: HostKey) -> str
    # Resolve a logical host key to its base URL string (no trailing slash).

_default_hosts() -> dict[HostKey, HttpUrl]

```

## dispatcher.py
```
# Multi-account ``Dispatcher`` — aiogram-style: inherits from :class:`Router`.


cls Dispatcher(Router)
  __init__() -> None
  async feed_event(event: Event) -> bool
  async dispatch(event: Event) -> bool
    # Alias of :meth:`feed_event` — present so app code can read either name.
  async event_entry(event: Event) -> bool
    # Alias of :meth:`feed_event` — used by the webhook adapter.
  async propagate_event(event: Event, ctx: EventContext? = None) -> bool
  async publish(channel: str, event: Event) -> bool
  run_channels() -> None
    # Start a drain worker per registered channel. Idempotent.
  async replay_pending() -> int
  spawn(coro: Awaitable[Any) -> asyncio.Task[Any]
    # Schedule a background task; keep a strong ref so it doesn't get GC'd mid-flight.
  async shutdown() -> None
    # Close channels, then await in-flight tasks; cancel any that overrun. Idempotent.

make_dispatcher() -> Dispatcher

```

## exceptions.py
```
# SDK exception hierarchy. Everything inherits from :class:`SDKError`.


cls ErrorContext: method: str | None, host: str | None, path: str | None, attempt: int, request_id: str, account_id: str | None, breaker_path: str | None, extras: dict[str, object]

cls SDKError(Exception)
  # Root of the SDK exception tree. Subclass for specific failure modes.
  __init__(detail: str? = None) -> None

cls ConfigError(SDKError)

cls MethodDeclarationError(SDKError, TypeError)
  # Raised at import time when a ``BaseMethod`` subclass is malformed.

cls MethodNotBoundError(SDKError, RuntimeError)
  # Awaited a method (or called a bound model action) without binding a client.

cls TransportError(SDKError)

cls AvitoConnectionError(TransportError)

cls AvitoTimeoutError(TransportError)

cls TLSError(TransportError)

cls SessionClosed(TransportError, RuntimeError)

cls ProxyError(TransportError)
  __init__(detail: str? = None) -> None

cls ProxyParseError(ProxyError, ValueError)
  # Raised by :func:`parse_proxy` when the input shape is not recognised.

cls ProxyConnectionError(ProxyError)
  # The proxy refused / dropped the connection (TCP-level).

cls ProxyAuthError(ProxyError)
  # 407 from the proxy, or upstream auth challenge the proxy passed through.

cls ProxyTimeoutError(ProxyError)
  # The proxy did not respond inside the request timeout.

cls ProxyTLSError(ProxyError)
  # TLS handshake to or through the proxy failed.

cls ProxyBanned(ProxyError)
  __init__(detail: str? = None) -> None

cls ProxyExhausted(ProxyError)
  # Every proxy in the pool is banned and none are available right now.

cls HTTPError(SDKError)
  # Raised when the server returns a non-2xx response.
  __init__(detail: str? = None) -> None

cls ClientError(HTTPError)

cls BadRequest(ClientError)

cls UnauthorizedError(ClientError)

cls ForbiddenError(ClientError)

cls NotFoundError(ClientError)

cls ConflictError(ClientError)

cls ValidationFailed(ClientError)

cls RateLimitedError(ClientError)
  __init__(detail: str? = None) -> None

cls ServerError(HTTPError)

cls InternalServerError(ServerError)

cls BadGatewayError(ServerError)

cls ServiceUnavailableError(ServerError)

cls GatewayTimeoutError(ServerError)

cls AuthError(SDKError)

cls TokenExpired(AuthError)

cls TokenIssuanceFailed(AuthError)

cls ProtocolError(SDKError)

cls ResponseDecodingError(ProtocolError)

cls PathResolutionError(ProtocolError)

cls ModelNotBoundError(MethodNotBoundError)
  # Subclass alias so :class:`AvitoObject` callers can catch either name.

cls InvalidStateTransition(SDKError)
  __init__(detail: str? = None) -> None

cls StorageError(SDKError)

cls PaginationError(SDKError)

cls RunawayPagination(PaginationError, RuntimeError)
  # Raised when a paginator exceeds the configured ``max_pages`` guard.

cls AssetTooLargeError(SDKError)
  __init__(detail: str? = None) -> None

http_error_for_status(status: int) -> type[HTTPError]

```

## filters.py
```
# Magic filter ``F`` — attribute/item/comparison capture for event predicates.

F = MagicFilter()

cls MagicFilter
  __init__() -> None
  in_(values: Iterable[object) -> MagicFilter
  contains(value: object) -> MagicFilter
  func(fn: Callable[[object], bool) -> MagicFilter

_safe_index(obj: object, key: object) -> object

_safe_contains(haystack: object, needle: object) -> bool

```

## logging.py
```
# Structlog setup + redaction processor for secrets/tokens.

_REDACT_KEYS = …
_REDACTED = '***'

_redact_processor(_logger: Any, _method_name: str, event_dict: dict[str, Any) -> dict[str, Any]

_walk_redact(value: object) -> object

configure(level: int | str = logging.INFO) -> None

get_logger(name: str? = None) -> BoundLogger
  # Lazily configures structlog on first call; returns a bound logger.

```

## persistent_queue.py
```
# Backward-compatibility shim — moved to :mod:`avitoapi.queue`.


```

## polling.py
```
# Polling feed — a pull-based event source for domains Avito does not push.

_DEFAULT_INTERVAL_S = 5.0
_DEFAULT_BACKOFF_INITIAL_S = 1.0
_DEFAULT_BACKOFF_MAX_S = 60.0

cls PollBatch: events: list[Event], cursor: str | None

cls PollingRunner(ABC)
  __init__(dispatcher: Dispatcher) -> None
  async poll(cursor: str?) -> PollBatch
    # Fetch the next batch from ``cursor``; return the events + advanced cursor.
  async tick() -> int
  async start() -> None
    # Run :meth:`tick` in a loop until :meth:`stop`. Mirrors ``BaseWebhookRunner.start()``.
  async stop() -> None
    # Signal the loop to finish the current cycle and return. Idempotent.
  update_cadence(interval_s: float) -> None
    # Retune the between-cycle delay on the *live* poller — no restart. Next tick picks it up.
  cursor_key() -> str

```

## types.py
```
# Cross-cutting NewType / Enum / lightweight view types used by every layer.

JSONValue: TypeAlias = 'dict[str, JSONValue] | list[JSONValue] | str | int | float | bool | None'
JsonObject: TypeAlias = dict[str, 'JSONValue']

cls HealthState(StrEnum): OK, DEGRADED, DOWN
  # Aggregate state surfaced by ``Client.healthcheck()``.

cls HealthStatus: state: HealthState, storage: bool, sessions: dict[str, bool], breakers_open: tuple[str, ...], detail: str | None
  # Snapshot of all health-relevant subsystems.

```

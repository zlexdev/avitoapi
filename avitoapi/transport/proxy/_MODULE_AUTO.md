# proxy/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

> Proxy transport seam. See ``_MODULE.md``.

## __init__.py
```
# Proxy transport seam. See ``_MODULE.md``.


```

## _base.py
```
# Proxy transport seam. ``NoProxyTransport`` is the default; rotators live in :mod:`.rotating`.


cls Proxy(BaseModel)
  # Single proxy endpoint. ``url`` includes scheme + auth + host + port.

cls ProxyAcquireContext
  __init__(proxy: Proxy?) -> None
  invalid() -> bool
  mark_invalid(error: ProxyError? = None) -> None
    # Record that this proxy attempt failed. Called from the funnel or middleware.

cls BaseProxyTransport(ABC)
  # Abstract per-attempt proxy provider.
  acquire() -> ProxyAcquireContext
    # Return a context that yields one :class:`Proxy` (or ``None``) for this attempt.
  add_invalid_hook(hook: InvalidHook) -> None
    # Register a callable invoked when a proxy is marked invalid. Default: no-op.

cls NoProxyTransport(BaseProxyTransport)
  # Default. Always yields ``None`` — direct connection.
  acquire() -> ProxyAcquireContext

```

## callback.py
```
# Callback-driven proxy transport.

KEEP = _KeepSentinel()

cls _KeepSentinel
  # Singleton sentinel — ``return KEEP`` means "don't replace the proxy".

cls ProxyContext: reason: str, current: Proxy | None, total_requests: int, total_errors: int, current_errors: int, last_error: ProxyError | None, last_error_at: float, account_id: str | None, host: str | None, stats: dict[str, tuple[int, int]]

cls _ProxyStats: requests: int, errors: int

cls CallbackProxyTransport(BaseProxyTransport)
  __init__(callback: ProxyCallback) -> None
  add_invalid_hook(hook: InvalidHook) -> None
  current() -> Proxy | None
  total_requests() -> int
  total_errors() -> int
  acquire() -> ProxyAcquireContext
  set_current(proxy: Proxy | str | dict[str, Any]?) -> None

_is_awaitable(obj: Any) -> bool

```

## parser.py
```
# Flexible proxy parser. Accepts URL strings, ``host:port[:user:pass]`` shorthand, dicts.

_DEFAULT_SCHEME = 'http'

parse_proxy(value: ProxyLike) -> Proxy

parse_proxy_list(values: Iterable[ProxyLike] | str) -> list[Proxy]

_split_lines(text: str) -> list[str]

_from_dict(data: dict[str, Any) -> Proxy

_from_string(value: str) -> Proxy

_from_url(text: str) -> Proxy

_build() -> Proxy

_split_creds(creds: str) -> tuple[str, str | None]

_split_host_port(hostport: str) -> tuple[str, int]

_coerce_port(value: Any) -> int

```

## rotating.py
```
# Rotating proxy transports with cumulative ban tracking.


cls RotationStrategy(StrEnum): ROUND_ROBIN, RANDOM, STICKY
  # How to pick the next proxy across requests.

cls ProxyHealth: failure_count: int, banned: bool, banned_at: float, last_error: str | None, success_count: int
  # Per-proxy failure tally + ban state. Lives inside the transport.

cls ListProxyTransport(BaseProxyTransport)
  __init__(proxies: Iterable[ProxyLike] | str) -> None
  add_invalid_hook(hook: InvalidHook) -> None
  healthy() -> list[Proxy]
    # Snapshot of currently-selectable proxies.
  banned() -> list[Proxy]
    # Snapshot of currently-banned proxies (cooldown not elapsed).
  reset(proxy: Proxy? = None) -> None
    # Clear ban state. ``None`` resets every proxy.
  acquire() -> ProxyAcquireContext
  mark_success(proxy: Proxy) -> None
    # Optional positive signal — callers can let us know a proxy worked.

cls RotatingProxyTransportFactory: proxies: list[ProxyLike], strategy: RotationStrategy, max_failures: int, cooldown_s: float, raise_on_ban: bool
  # Convenience factory — shorthand for the common case.

```

## validator.py
```
# Proxy checker — runs a tiny live request through each proxy and reports the outcome.

_DEFAULT_CHECK_URL = 'https://api.avito.ru/'

cls ProxyCheckResult: proxy: Proxy, ok: bool, status_code: int | None, elapsed_s: float, error: str | None
  # Outcome of one proxy probe.

cls ProxyValidator: check_url: str, http_method: str, timeout_s: float, accept_statuses: frozenset[int], concurrency: int, request_fn: RequestFn | None

_default_request_fn() -> RequestFn

async _curl_request(proxy: Proxy, url: str, method: str, timeout_s: float) -> tuple[int, float]

async _httpx_request(proxy: Proxy, url: str, method: str, timeout_s: float) -> tuple[int, float]

```

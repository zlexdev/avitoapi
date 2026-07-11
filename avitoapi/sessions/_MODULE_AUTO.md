# sessions/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

> Session funnel + concrete backends. See ``_MODULE.md``.

## __init__.py
```
# Session funnel + concrete backends. See ``_MODULE.md``.


create_default_session(config: ClientConfig) -> BaseSession

```

## _models.py
```
# Wire-level dataclasses passed through the session funnel.


cls PreparedRequest: host: str, http_method: str, url: str, headers: dict[str, str], query: dict[str, JSONValue], body: JSONValue | bytes | None, files: list[tuple[str, bytes, str | None]] | None, proxy: str | None, timeout_s: float, method_name: str | None
  # Everything ``BaseSession._send`` needs to perform one HTTP request.

cls RawResponse: status: int, headers: dict[str, str], body: bytes, elapsed_s: float
  # Raw HTTP output, pre-decode and pre-status-mapping.

cls RequestContext: client: Client, method: BaseMethod[object] | None, breaker_path: str | None, workflow_data: dict[str, JSONValue], attempt: int, elapsed_s: float, request_id: str, account_id: str | None, proxy: Proxy | None, proxy_acquire: ProxyAcquireContext | None
  # Per-call mutable bag carried through the middleware chain.

```

## base.py
```
# ``BaseSession`` — the funnel every HTTP call goes through.


cls BaseSession(ABC)
  __init__() -> None
  async open() -> None
    # Initialise pooled resources. Idempotent.
  async close() -> None
    # Release resources. Idempotent.
  async make_request(client: Client, method: BaseMethod[object) -> object
    # Run a method-class through the funnel and return the typed response.

```

## curl.py
```
# ``CurlSession`` — default backend using ``curl_cffi`` for browser-grade TLS fingerprinting.


cls CurlSession(BaseSession)
  __init__() -> None
  async open() -> None
  async close() -> None

```

## headers_middleware.py
```
# ``DefaultHeadersMiddleware`` — inject default request headers into every outbound call.


cls DefaultHeadersMiddleware(RequestMiddleware)
  __init__(config: ClientConfig) -> None

```

## httpx_session.py
```
# ``HttpxSession`` — fallback backend when ``curl_cffi`` is not installable.


cls HttpxSession(BaseSession)
  # Pure-Python fallback. No TLS impersonation — Cloudflare-protected hosts may challenge.
  __init__() -> None
  async open() -> None
  async close() -> None

```

## middleware.py
```
# Request-side middleware ABC + manager. Shared shape between request and dispatch sides.


cls RequestMiddleware(ABC)

cls RequestMiddlewareManager
  # Chain of :class:`RequestMiddleware`. Earlier registrations wrap later ones.
  __init__() -> None
  register(middleware: RequestMiddleware) -> RequestMiddleware
    # Append a middleware. Returns the middleware for fluent chaining.
  async dispatch(terminal: RequestHandler, prepared: PreparedRequest, ctx: RequestContext) -> RawResponse
    # Fold the chain over ``terminal`` and execute.

_wrap(middleware: RequestMiddleware, nxt: RequestHandler) -> RequestHandler

```

## proxy_middleware.py
```
# Proxy-aware request middlewares.


cls ProxyErrorMiddleware(RequestMiddleware)

_translate(exc: TransportError, proxy_url: str) -> ProxyError

```

## rate_limit_middleware.py
```
# Outbound rate-limit middleware — token bucket per ``(account_id, scope)``.


cls TokenBucket
  __init__() -> None
  async acquire(amount: float = 1.0) -> None
    # Block until ``amount`` tokens are available, then consume them.

cls AvitoRateLimitMiddleware(RequestMiddleware)
  __init__() -> None

_make_bucket(rps: float) -> Any

```

## retry_middleware.py
```
# ``RetryMiddleware`` — unified retry for HTTP errors and transport exceptions.


cls RetryMiddleware(RequestMiddleware)
  __init__(policy: RetryPolicy) -> None

_extract_retry_after(raw: RawResponse) -> float | None

_raise_http(raw: RawResponse, ctx: RequestContext, prepared: PreparedRequest) -> None

```

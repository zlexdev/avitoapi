# sessions/

The funnel — every HTTP request the SDK makes lands here. Concrete
backends (`CurlSession`, `HttpxSession`) implement `_send` only;
everything else lives in `BaseSession`.

## Contract — `BaseSession.make_request(client, method)`

1. Instantiate `method.__protocol__()`.
2. Build `RequestContext`: bind `request_id` + `account_id` into
   `structlog.contextvars` for the entire call.
3. `protocol.build_request(method, config, host, ctx)` → `PreparedRequest`.
4. Apply default headers (User-Agent, Accept, …).
5. Dispatch through `request_middlewares` (auth-injector, idempotency
   middleware later) into `_terminal`.
6. `_terminal` runs the retry loop:
   - acquires a proxy from `proxy_transport.acquire`,
   - calls subclass `_send(prepared)`,
   - on transport errors: retry for safe verbs, otherwise re-raise.
   - on non-2xx HTTP: map status → typed exception via
     `http_error_for_status`. Retry GET/HEAD/OPTIONS + 408/429/5xx within
     `RetryPolicy.max_retries`, honour `Retry-After` on 429.
7. `protocol.decode_response(method, raw)` → typed `T`.
8. If `T` is a `AvitoObject`, call `T.as_(client)` so bound methods work.

## Subclass contract

- `async def _send(prepared) -> RawResponse` — only abstract method.
  Translate transport-layer failures (timeout, DNS, TLS, connection
  reset) into `TransportError` subclasses; status-level decisions stay
  in the base.
- `open()` / `close()` — idempotent.

## Backends

- `CurlSession` (default) — lazy-imports `curl_cffi.requests.AsyncSession`,
  impersonates `chrome120` by default. Required for Cloudflare-protected
  Avito hosts.
- `HttpxSession` (fallback) — lazy-imports `httpx.AsyncClient`. No TLS
  spoofing; useful only when `curl_cffi` wheels are unavailable.

## Don'ts

- Don't bypass `make_request` from any method body.
- Don't move `import curl_cffi` / `import httpx` to module top in
  the backends — base install must stay slim.
- Don't add cookie persistence inside `_send` — that's per-backend state
  with a separate `Client.save_session` API (W2+).
- Don't auto-retry POST/PUT/DELETE. Only safe verbs retry. Methods can
  opt in via `__retry_safe__ = True`.

# utils/proxy/

Per-attempt proxy seam consumed by the session funnel.

## Contract

- `BaseProxyTransport.acquire(account_id=..., host=...)` returns a
  `ProxyAcquireContext` (async context manager).
- `async with transport.acquire(...) as proxy: ...` — `proxy` is either
  a `Proxy` instance or `None` (direct connection).
- `ProxyAcquireContext.mark_invalid(error?)` lets the funnel signal that
  a proxy failed mid-request; rotators consume this to advance the
  cumulative failure tally.
- On `__aexit__` the transport's `on_release` callback fires once when
  `mark_invalid` was called — that's where rotators evict / cool down.

## Backends

- `NoProxyTransport` — default. Always yields `None`.
- `ListProxyTransport` — cycle through a static list. Rotation strategies:
  `RotationStrategy.ROUND_ROBIN`, `RANDOM`, `STICKY` (per `account_id`).
  Tracks per-proxy failures; bans a proxy after `max_failures` consecutive
  invalidations and skips it for `cooldown_s`. With `raise_on_ban=True`
  the failing request escapes with a `ProxyBanned` exception so callers
  see the cumulative effect.

## Helpers

- `parse_proxy(...)` / `parse_proxy_list(...)` — accept URL strings,
  `host:port[:user:pass]` shorthand, dicts. Multi-line strings are split
  with `#`-comment lines skipped.
- `ProxyValidator` — async probe; runs a small request through every
  proxy in parallel and returns `ProxyCheckResult` rows (ok / status /
  elapsed / error string). Default backend prefers `curl_cffi`,
  falls back to `httpx`.

## Exception map (see `avitoapi.exceptions`)

| Source                                  | Exception              |
|-----------------------------------------|------------------------|
| Parser refused input                    | `ProxyParseError`      |
| Connection refused / dropped via proxy  | `ProxyConnectionError` |
| TLS through proxy failed                | `ProxyTLSError`        |
| Proxy did not respond in time           | `ProxyTimeoutError`    |
| Proxy returned 407                      | `ProxyAuthError`       |
| `max_failures` threshold crossed        | `ProxyBanned`          |
| Every proxy banned, none selectable    | `ProxyExhausted`       |

`ProxyError` is the common ancestor; all sub-types inherit from
`TransportError`.

## Don'ts

- Don't bake `httpx` / `curl_cffi` proxy syntax into this layer. The
  session backend takes the string from `prepared.proxy` and translates
  it to its own format.
- Don't put rate-limiting logic inside proxy rotation — that's a
  separate layer (`AvitoRateLimitMiddleware`).

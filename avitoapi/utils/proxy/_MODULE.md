# utils/proxy/

Per-attempt proxy seam consumed by the session funnel.

## Contract

- `BaseProxyTransport.acquire(account_id=..., host=...)` returns a
  `ProxyAcquireContext` (async context manager).
- `async with transport.acquire(...) as proxy: ...` — `proxy` is either
  a `Proxy` instance or `None` (direct connection).
- `ProxyAcquireContext.mark_invalid()` lets the funnel signal that a
  proxy failed mid-request; rotators consume this in W2.

## Backends

- `NoProxyTransport` — default. Always yields `None`.
- `ListProxyTransport` / `RotatingProxyTransport` — land in W2 under
  `utils/proxy/list.py`.

## Don'ts

- Don't bake `httpx` / `curl_cffi` proxy syntax into this layer. The
  session backend takes the string from `prepared.proxy` and translates
  it to its own format.
- Don't put rate-limiting logic inside proxy rotation — that's a
  separate layer (`evented.TokenBucket` in W3).

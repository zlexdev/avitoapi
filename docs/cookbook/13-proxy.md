# Proxy transports

The session funnel acquires a proxy per attempt via a
`BaseProxyTransport`. Three backends ship in-tree:

* **`NoProxyTransport`** — direct connection (default).
* **`ListProxyTransport`** — static list with cumulative ban tracking
  + cooldown.
* **`CallbackProxyTransport`** — user-supplied callable decides what
  proxy to use next; great for warming a pool from an external
  rotator.

---

## Direct (default)

```python
from avitoapi import Client, ClientConfig, NoProxyTransport

client = Client(
    config=ClientConfig.from_env(),
    transport=NoProxyTransport(),
)
```

Omitting `transport=` also gets you `NoProxyTransport`.

---

## Parsing proxy strings

`parse_proxy` / `parse_proxy_list` accept everything you'd reasonably
type into a config file. They normalise into a typed `Proxy` model.

```python
from avitoapi import parse_proxy, parse_proxy_list

# Single proxy — any of these
parse_proxy("http://u:p@1.2.3.4:8080")
parse_proxy("1.2.3.4:8080")                              # scheme defaults to http
parse_proxy("1.2.3.4:8080:bob:secret")                   # legacy host:port:user:pass
parse_proxy("user:pass@10.0.0.1:8080")                   # user:pass@host:port
parse_proxy({"host": "11.0.0.1", "port": 8080, "user": "u", "password": "p"})
parse_proxy("socks5://5.6.7.8:1080")

# Multi-line text file (comments stripped, blank lines skipped)
parse_proxy_list("""
# rotating residential
1.2.3.4:8080
socks5://5.6.7.8:1080
user:pass@10.0.0.1:8080
""", skip_invalid=True)
```

`skip_invalid=True` drops malformed lines silently. `False` (default)
raises `ProxyParseError` on the first bad line.

---

## List-based rotation with bans

`ListProxyTransport` cycles through a static pool, tracks per-proxy
failures, and bans a proxy after `max_failures` consecutive errors.

```python
from avitoapi import ListProxyTransport, RotationStrategy

transport = ListProxyTransport(
    [
        "http://user:pass@1.2.3.4:8080",
        "5.6.7.8:8080",
        "9.9.9.9:8080:bob:secret",
        {"host": "11.0.0.1", "port": 8080, "user": "u", "password": "p"},
    ],
    strategy=RotationStrategy.ROUND_ROBIN,    # | RANDOM | STICKY
    max_failures=3,                            # 3 errors → ban
    cooldown_s=300,                            # reactivate after 5 min
    raise_on_ban=True,                         # surface ProxyBanned on threshold
)

client = Client(config=ClientConfig.from_env(), transport=transport)
```

Lifecycle of one proxy:

```
healthy ── failure ──▶ failing ── × max_failures ──▶ banned ── wait cooldown_s ──▶ healthy
   ▲                                                              │
   └──────── successful request (resets failure count) ──────────┘
```

When every proxy is banned, the next acquire raises `ProxyExhausted`.

### Rotation strategies

| Strategy        | Behavior                                                              |
|-----------------|-----------------------------------------------------------------------|
| `ROUND_ROBIN`   | Cycle the list in order; skip banned. Default.                         |
| `RANDOM`        | Random pick from healthy.                                              |
| `STICKY`        | One proxy per `account_id`. Rotates only when that proxy gets banned.  |

### Manual control

```python
healthy = transport.healthy()       # list[Proxy] currently selectable
banned = transport.banned()
transport.reset()                   # clear all bans
transport.reset(specific_proxy)
transport.mark_success(p)           # positive signal — decrements failure count
```

### Subscribe to ban events

```python
def on_invalid(proxy, error):
    log.warning("proxy.invalid", proxy=str(proxy.url), error=str(error))

transport.add_invalid_hook(on_invalid)
```

Hook fires on every failure; check `transport.banned()` for the actual
ban status.

---

## Callback-driven rotation

When the rotation logic isn't a static list (warming a pool, querying
a third-party rotator, sticky-per-region) plug in a callback:

```python
from avitoapi import KEEP, CallbackProxyTransport, ProxyContext

POOL = ["1.2.3.4:8080", "5.6.7.8:8080", "9.9.9.9:8080"]
cursor = 0

def get_next_proxy(ctx: ProxyContext):
    global cursor
    # Stay on the current proxy unless it errored out.
    if ctx.reason == "acquire" and ctx.current is not None:
        return KEEP
    proxy = POOL[cursor % len(POOL)]
    cursor += 1
    return proxy

transport = CallbackProxyTransport(get_next_proxy)
```

The callback receives a rich `ProxyContext`:

| Field             | Meaning                                       |
|-------------------|-----------------------------------------------|
| `reason`          | `"acquire"` or `"error"`                      |
| `current`         | proxy the funnel last used (or `None`)        |
| `total_requests`  | acquire calls served                          |
| `total_errors`    | cumulative invalidations                      |
| `current_errors`  | invalidations of the active proxy             |
| `last_error`      | the latest `ProxyError` (or `None`)           |
| `last_error_at`   | monotonic seconds of the last failure         |
| `account_id`      | label the funnel passed to acquire            |
| `host`            | target host                                   |
| `stats`           | per-proxy `(requests, errors)` snapshot       |

Return:

* `KEEP` — keep the current proxy.
* `None` — direct connection (no proxy).
* a `Proxy`, string, or dict — switch to that proxy.

### Async pool warming

The callback must be **synchronous**. For async rotators, warm the
pool outside the callback and push the result in:

```python
import asyncio
from avitoapi import CallbackProxyTransport, KEEP

class PoolWarmer:
    def __init__(self):
        self.current = None

    async def warm(self):
        while True:
            self.current = await async_rotator.next_proxy()
            await asyncio.sleep(60)

warmer = PoolWarmer()
asyncio.create_task(warmer.warm())

transport = CallbackProxyTransport(lambda ctx: warmer.current or KEEP)
```

Or even more direct: use `transport.set_current(proxy)` from your
async rotator and have the callback always return `KEEP`.

---

## Validating a pool before use

```python
from avitoapi import ProxyValidator

validator = ProxyValidator(
    check_url="https://api.avito.ru/",
    timeout_s=5,
    concurrency=16,
)

results = await validator.validate_many(["1.2.3.4:8080", "5.6.7.8:8080", "broken:1"])

healthy = [r.proxy for r in results if r.ok]
broken = [(r.proxy, r.error) for r in results if not r.ok]

log.info("validated", healthy=len(healthy), broken=len(broken))
```

Default backend is `curl_cffi` (already a dep) with fallback to
`httpx`. Bring your own via `request_fn=`.

---

## Proxy-aware session middleware

Install on the session funnel for sharper retry / error mapping:

```python
from avitoapi import ProxyErrorMiddleware, RetryMiddleware

client.request_middlewares.register(ProxyErrorMiddleware())
client.request_middlewares.register(RetryMiddleware(
    max_retries=3,
    initial_s=0.25,
    max_s=5.0,
))
```

* `ProxyErrorMiddleware` translates generic `TransportError` into
  specific `ProxyConnectionError` / `ProxyTimeoutError` / `ProxyTLSError`
  and marks the proxy invalid through the acquire context so rotators
  advance their failure tally.
* `RetryMiddleware` catches `ProxyError` (any subclass) and retries —
  each retry triggers a fresh acquire so the request rotates away from
  the failing proxy. `ProxyExhausted` is a hard give-up.

---

## Catching specific failures

```python
from avitoapi import (
    ProxyAuthError, ProxyBanned, ProxyConnectionError,
    ProxyError, ProxyExhausted, ProxyTimeoutError, ProxyTLSError,
)

try:
    await client.get_self()
except ProxyBanned as exc:
    log.warning("proxy banned", url=exc.proxy_url, count=exc.failure_count)
except ProxyExhausted:
    log.error("every proxy exhausted; pausing the worker")
except ProxyTimeoutError as exc:
    log.warning("proxy timeout", url=exc.proxy_url)
except ProxyError as exc:           # catch-all
    log.error("proxy failure", url=exc.proxy_url, detail=exc.detail)
```

Inheritance: `ProxyError → TransportError → SDKError`. Catch wide for
generic handling, narrow for specific recovery.

---

## Custom transport

`BaseProxyTransport` is one method (`acquire`) returning a
`ProxyAcquireContext`. Build your own for exotic shapes (per-host
pools, A/B-test rotation, paid-pool-then-free-pool fallback):

```python
from avitoapi.utils.proxy import BaseProxyTransport, Proxy, ProxyAcquireContext

class MyTransport(BaseProxyTransport):
    def acquire(self, *, account_id=None, host=None) -> ProxyAcquireContext:
        proxy = pick_proxy_for(host)              # your logic
        def on_release(p: Proxy, err): mark_failure_if(err)
        return ProxyAcquireContext(proxy, on_release=on_release)
```

The funnel handles the rest — middleware, retry, breaker — uniformly.

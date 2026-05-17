# Circuit breaker

Per-endpoint breaker that opens after N consecutive failures, stays
open for M seconds, then probes once. Built-in: the session funnel
wraps every request through `BreakerRegistry`.

---

## Default behavior

Just set thresholds on `ClientConfig`:

```python
from avitoapi import Client, ClientConfig

config = ClientConfig(
    client_id="int-abc",
    client_secret="shhh",
    user_id=12345,
    breaker_fail_threshold=5,        # 5 consecutive failures → open
    breaker_open_seconds=30.0,       # stays open 30 s, then half-open probe
    breaker_per_account=False,       # share breaker across all accounts on same endpoint
)
```

The funnel calls `record_failure()` on 5xx / transport errors and
`record_success()` on 2xx. When a breaker is `OPEN`, the funnel raises
`CircuitOpenError` immediately — no request leaves the box.

---

## Per-account isolation

A single slow seller shouldn't trip the breaker for every other seller
hitting the same endpoint. Flip the flag:

```python
config = ClientConfig(
    ...,
    breaker_per_account=True,        # breaker key = (host, path, account_id)
)
```

Now each account's failures are tallied separately.

---

## Lifecycle

```
CLOSED ─ record_failure() ×N ──▶ OPEN ─ wait open_seconds ──▶ HALF_OPEN
   ▲                                                            │
   └──────────── record_success() ─────────────────────────────┘
                                                                │
                          record_failure() ──────────────────▶ OPEN
```

* `CLOSED` — normal traffic.
* `OPEN` — every call fails fast with `CircuitOpenError`.
* `HALF_OPEN` — the next call is the probe. Success → `CLOSED`, failure
  → `OPEN` again (fresh `open_seconds` countdown).

---

## Inspecting state

The registry is reachable via the client's session — useful for
ops dashboards / `/healthz` endpoints:

```python
registry = client.session.breaker_registry
print("breakers:", len(registry))
```

Add health snapshots by extending the registry yourself — the registry
itself is a thin lazy cache, so building a `health()` helper that walks
`_breakers.items()` is a 5-liner.

---

## Catch + handle

`CircuitOpenError` is just an exception — catch it where it surfaces:

```python
from avitoapi.breaker import CircuitOpenError

try:
    await client.send_text_message(chat.id, "hello")
except CircuitOpenError:
    await schedule_retry_later(chat.id)        # queue + try again post-cooldown
```

Pair this with the persistent queue + `enqueue_later` to bounce
messages forward when the breaker is open — see [08-queue.md](08-queue.md).

---

## Manual reset

If you fixed the upstream out-of-band and want to re-enable the
endpoint immediately:

```python
breaker = await registry.for_key("api.avito.ru", "/messenger/v3/...")
await breaker.reset()                # force CLOSED
```

---

## Trade-off vs retries

Retries handle **transient** failures (one bad packet, one slow node).
Breakers handle **persistent** failures (upstream is down for 30 s).
They compose: retry → on exhaustion the breaker counts a failure → on
threshold the breaker opens → subsequent calls fail fast without
burning retry budget.

The session's retry middleware already plays well with the breaker —
just don't disable both.

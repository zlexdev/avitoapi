# avitoapi.breaker

Per-endpoint circuit breaker registry. Keyed by `(host, path)` or
`(host, path, account_id)` depending on
`ClientConfig.breaker_per_account`.

## Surface

- `BreakerRegistry(config)` — lazy per-key map of breakers; `await reg.for_key(host, path, account_id)`.
- `CircuitBreaker` — in-package fallback breaker with `record_success()`,
  `record_failure()`, `is_open()`, `reset()`, `.state` (BreakerState).
- `BreakerState` — `CLOSED`, `OPEN`, `HALF_OPEN`.
- `CircuitOpenError` — raised by callers that catch the open state.

## Backend selection

If the optional `evented` package is importable, `BreakerRegistry` delegates
to `evented.CircuitBreaker` and inherits all of its features (metrics, hooks,
custom probes). Without `evented`, the in-package `CircuitBreaker` (closed →
N consecutive failures → open → wait `open_seconds` → half_open → success
→ closed | failure → open) is used.

## Files

- `registry.py` — `BreakerRegistry`, `CircuitBreaker`, `BreakerState`, `CircuitOpenError`.
- `__init__.py` — public re-exports.

## Wiring

The registry is constructed alongside the `Client` (or shared across `Client`
instances for multi-account deployments). HTTP middleware checks `is_open()`
before a request and records success/failure based on the response status.

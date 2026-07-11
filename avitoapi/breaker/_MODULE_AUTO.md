# breaker/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

> Circuit breaker registry — keyed by ``(host, path, account_id)``.

## __init__.py
```
# Circuit breaker registry — keyed by ``(host, path, account_id)``.


```

## registry.py
```
# Per-endpoint circuit breaker registry.

_PATH_TEMPLATE_RE = …

cls CircuitOpenError(Exception)
  # Raised when an operation is attempted against an open breaker.

cls BreakerState(StrEnum): CLOSED, OPEN, HALF_OPEN
  # Lifecycle of a single circuit breaker.

cls CircuitBreaker
  __init__() -> None
  state() -> BreakerState
    # Current lifecycle phase (without performing the OPEN→HALF_OPEN time check).
  is_open() -> bool
  async record_success() -> None
    # Reset failure counters and close the breaker.
  async record_failure() -> None
    # Increment failures; open the breaker once the threshold is crossed.
  async reset() -> None
    # Force-close the breaker regardless of current state.

cls BreakerRegistry
  __init__(config: ClientConfig) -> None
  async for_key(host: str, path: str, account_id: str? = None) -> Any
    # Return (or lazily create) the breaker for ``(host, path[, account_id])``.

```

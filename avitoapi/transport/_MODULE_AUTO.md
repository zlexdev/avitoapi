# transport/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

> Transport-layer helpers (headers, retry policy). See ``_MODULE.md``.

## Submodules

- [`proxy/`](proxy\_MODULE_AUTO.md) — Proxy transport seam. See ``_MODULE.md``. (5 py, 14 cls, 14 fn)

## headers.py
```
# Default header builder for outbound requests.


build_default_headers(config: ClientConfig) -> dict[str, str]
  # Build the headers every request inherits — User-Agent, Accept, Accept-Language.

```

## retry.py
```
# Frozen :class:`RetryPolicy` with exponential backoff + jitter.


cls RetryPolicy: max_retries: int, initial_s: float, max_s: float, jitter_ratio: float, retry_statuses: frozenset[int]

```

# transport/

Tiny utility layer between the session funnel and the network: default
headers + retry policy. Intentionally framework-agnostic — nothing here
imports `curl_cffi` or `httpx`.

## Pieces

- `headers.build_default_headers(config)` — `User-Agent`, `Accept`,
  `Accept-Language`. Per-request `Authorization` lives in middleware.
- `transport.retry.RetryPolicy` — frozen dataclass with `max_retries`,
  `initial_s`, `max_s`, `jitter_ratio`, `retry_statuses`.
  - `delay_for(attempt, retry_after_s=...)` — uses `retry_after_s` if
    server sent one (429), otherwise exponential + symmetric jitter.
  - `should_retry_status(status)` — true for 408 / 429 / 5xx by default.

## Don'ts

- Don't put backoff *loops* here — `RetryPolicy` only describes timing.
  The loop itself lives in `sessions/base.py:BaseSession.make_request`.
- Don't add `requests.Session`-style helpers; this layer is intentionally
  stateless.

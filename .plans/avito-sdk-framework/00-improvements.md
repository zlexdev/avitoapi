# 00 — Improvements

Greenfield — no tech debt to fix. This file is the future-proofing scout's
output: structural improvements the project should absorb cheaply now vs.
later.

## Tech debt to fix in this plan
None. New repo.

## Future-proofing proposals
| ID | Proposal | Pays off when | Cost | Tag |
|---|---|---|---|---|
| FP-1 | Vendor `evented` from `github.com/zlexdev/evented` rather than rolling Dispatcher/Router/FSM/Web | every multi-account / FSM / webhook need from day one | S (one `pyproject.toml` dep + 1 `dispatcher.py` factory) | must-include |
| FP-2 | `Protocol` ABC even though only `RestProtocol` ships | Avito ever adds GraphQL (unlikely) OR we extend to scraping `m.avito.ru` JSON-RPC | S (1 file, 30 LOC) | must-include |
| FP-3 | `BaseProxyTransport` + `ProxyAcquireContext` ABCs even though no rotation needed for partner API | multi-account SaaS users want per-account egress IPs | S (~80 LOC ABC) | must-include |
| FP-4 | `ChallengeSolver` ABC + `NullSolver` only — no concrete solvers | downstream user adds SmartCaptcha for mobile scrape (out of scope here) | S (1 file, 40 LOC) | must-include |
| FP-5 | Per-domain mixin split of `client.py` from Wave 2 onwards | once `client.py` crosses ~1500 LOC | M (refactor split) | optional-include (decide at Wave 3 — defer if file still readable) |
| FP-6 | Persistent storage backends (`redis.py`, `mongo.py`) lazy-loaded under extras | multi-process / multi-instance deployments | M (2 backend files + extras config) | must-include at Wave 2 |
| FP-7 | `FakeSession` + JSON-fixture loader from Wave 1 | Every test needs it; Avito has no sandbox | S (~100 LOC) | must-include |
| FP-8 | Idempotency key on every mutating method-class via base-class hook | Avito dedups on `Idempotency-Key`; webhook redelivery + bot retry both rely on this | S (~30 LOC in `_base.py` + injection in `RestProtocol`) | must-include |
| FP-9 | `categories/` static module pre-populated with top-level Avito categories from public catalogue | item-creation flows + filtering UIs the SDK consumer will build | M (research + transcribe; can grow incrementally) | optional-include (Wave 5; not blocking earlier waves) |
| FP-10 | Versioned public API via `__version__` + `experimental` decorator from skill `utils.py` | any breaking change to method signatures | S (1 file) | must-include |
| FP-11 | OpenTelemetry hooks via `structlog.contextvars` + optional `otel` exporter middleware | downstream consumer ships in a traced env | M (instrumentation + extras) | optional-include (Wave 4 if room; otherwise defer) |
| FP-12 | `examples/` directory with one canonical bot (echo via webhook + polling fallback) | every new user reads it before writing code | S (~150 LOC) | must-include at Wave 4 |

## Deferred (logged for next plan)
- FP-13: GraphQL protocol implementation — only when Avito adds a GraphQL
  surface (not on the roadmap as of 2026-05).
- FP-14: SmartCaptcha / Cloudflare solver for `m.avito.ru` — separate
  riskier project; needs its own ToS analysis.
- FP-15: `asyncbus` integration for outbound at-least-once event emission
  to consumer's bus — wait until a real consumer asks.
- FP-16: Auto-generated method classes from a published OpenAPI spec — would
  reduce hand-typing for waves 5–6, but `developers.avito.ru` blocks
  programmatic fetch (Cloudflare 403), so impractical until that changes.

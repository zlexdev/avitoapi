# 05 — Cross-wave risks + remaining open questions

## Cross-wave risks

### R1 — `developers.avito.ru` is bot-protected
Cannot pull the OpenAPI spec programmatically (Cloudflare 403). Every
endpoint shape is hand-transcribed from third-party clients (covox,
DUB1401, n8n-nodes, Postman). Mitigation: cross-verify each endpoint
against **at least two** independent third-party sources before shipping
it. Each method-class docstring includes the source citation.

**Impact:** if Avito changes a schema and our model lags, decoding
breaks at runtime. Defence in W6: `ResponseDecodingError` carries the
raw body, the method-class name, and the diff between expected/actual
fields — debuggable from a single log line.

### R2 — Avito has no sandbox environment
Every live test runs on real accounts + real items. Mitigation:
`FakeSession` + JSON fixtures captured from real responses (recorded
via `AVITOAPI_RECORD=1` runs). Live tests gated on `AVITOAPI_LIVE=1`,
skipped in CI by default. Devs run them manually with a throwaway
account.

### R3 — `evented` is a private dependency
Pulled via `git+https://${GH_TOKEN}@github.com/zlexdev/evented.git@<TAG>`.
CI needs `GH_TOKEN` configured as a secret. Documented in W4
`README.md`. Local-dev fallback: clone `evented` next to `avitoapi`,
install editable.

### R4 — OAuth 403 on token expiry (not 401)
A real Avito footgun. SDK detects `403 + body contains "token_expired"`
and re-auths. Mitigation: explicit test in W1 covers this branch,
runs on every CI pass.

### R5 — Webhook 2-second timeout
Avito waits 2 seconds for `200 OK` on a webhook delivery. Heavy
handler work blocks the 200, triggers retry storm. Mitigation: W4 docs
explicitly tell users to enqueue work via `evented.TaskTracker` and
return immediately. Example bot demonstrates the pattern.

### R6 — Rate-limit numbers are field-observed defaults
~5 rps global, ~1 rps per chat — observed by other third-party clients,
not officially published. Tune on first real prod traffic. SDK ships
defaults; `ClientConfig.rate_limit_*` knobs let users override.

### R7 — Idempotency-Key on `messenger/v1/send` is dedup-window dependent
Avito's dedup window is observed at ~24h but undocumented. SDK
generates one key per logical mutation, reuses across retries within
same Python process. After process restart, the key is regenerated —
acceptable risk.

### R8 — `curl_cffi` Windows install
Wheels exist for win_amd64 on Python 3.11/3.12 but not for ARM/3.13
yet. `[httpx]` extra is the fallback. W1 mentions in README install
section.

### R9 — Multipart upload across protocols
`RestProtocol` switches to `multipart/form-data` when it sees `bytes` or
`PathLike` field values. Slightly fragile — explicit `__multipart__ =
True` ClassVar override available on method-class for ambiguous cases.

### R10 — Discriminated union on `Message.type` lags new types
Avito occasionally adds message types. `UnknownMessage` fallback +
WARNING log + recorded in `_research/raw/avito-api-surface.md` so the
next wave can backfill.

### R11 — `categories/` UUID maps are snapshots
Avito rotates category UUIDs occasionally. SDK ships the snapshot date
in each file's docstring. Consumers can override via
`ClientConfig.category_overrides: dict[str, UUID]`.

### R12 — `mypy --strict` + Pydantic v2 discriminated unions are finicky
Need correct `Annotated[Union[...], Field(discriminator="type")]` shape
and matching `Literal` discriminators on subclasses. Documented in
`_MODULE.md` for `models/messenger.py`.

### R13 — Storage backend pluggability vs. type narrowness
`BaseStorage[TDoc, TId]` is generic but the codebase uses
`BaseStorage[Any, str]` in most places. Acceptable — `# type: ignore[type-arg]`
not needed since `BaseStorage` defaults to `Any` for `TDoc` when
unparameterised.

### R14 — Public API surface stability across waves (library tier risk)
A method renamed between W1 and W4 breaks downstream code. Mitigation:
W4 doc-snapshot the public API into `docs/api-reference-v0.1.md`. W5/W6
additions are pure adds (semver MINOR). Any rename to an already-shipped
method-class requires a deprecation cycle with `@experimental` warning
in the prior MINOR.

## Open questions for the user (none blocking)
1. **License?** Plan defaults to MIT. Override at W4 (`LICENSE` file is
   generated then).
2. **PyPI publish?** Out of W4 scope. Add a `release.yml` workflow in
   a follow-up if/when the user wants this on PyPI.
3. **`asyncbus` integration** for outbound at-least-once events? Logged
   in `00-improvements.md` FP-15. Wait for a real downstream consumer ask.

Every other potentially-blocking question is answered in
`00-decisions.md` and the user reviews at the very end.

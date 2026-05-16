# Plan Checker Review — avito-sdk-framework

> Captured inline; subagent ran in read-only mode and could not write the file directly.

## Internal Contradictions

| # | Sev | File | Problem | Fix |
|---|---|---|---|---|
| C1 | critical | wave-03 vs wave-04 | W3 ships `fsm/` re-exports `evented.*` but `evented` only added to `pyproject.toml` in W4-T1. W3-T7 ("FSM round-trip test green") can't even import. | Move `evented` dep install into W1-T1 (or a W3-T0). Pin tag in W4 before release. |
| C2 | high | decisions §34 vs wave-04 | Decision says `breaker/` registry shim (package). W4 file tree ships single-file `avitoapi/breaker.py`. Skill `layout.md` is a package. | Make it a package: `avitoapi/breaker/{__init__.py, registry.py, _MODULE.md}`. |
| C3 | high | overview / improvements / audit vs all waves | `ChallengeSolver` + `BaseProxyTransport` ABCs (FP-3/FP-4 "must-include", audit S10/S11 "follow") never appear in any wave's Files. | Add to W1-T6 (transport+proxy stubs) and W4-T3 (solver ABC + NullSolver). |
| C4 | medium | waves doc vs W4 | W4 acceptance requires `docs/load-baseline.md` but W4-T9 doesn't create it. | Add `docs/load-baseline.md` to W4-T9 Files. |
| C5 | medium | decisions §21 vs wave-03 | "Pin tag in Wave 4" but W3 needs `evented` working. | Pin loose `@master` in W1, pin to tag in W4. |
| C6 | low | wave-02 DAG | W2-T1/T2 `depends_on: []` but actual prereq is "W1 complete". | Document at top of each wave-NN: "Wave-prereq: all prior waves complete". |

## Layer Violations

| # | Sev | File | Problem | Fix |
|---|---|---|---|---|
| L1 | medium | wave-04 | Flat `avitoapi/middlewares/` mixes HTTP-side (rate-limit) + webhook-side (HMAC, idempotency). Skill splits: `sessions/middleware.py` vs `dispatcher/middlewares/`. | Move HMAC + idempotency under `web/middlewares/` (webhook-side); rate-limit lives in `sessions/middleware/avito.py` if outbound. |
| L2 | medium | wave-03 | RestProtocol auto-detects multipart on bytes/PathLike. R9 notes this is fragile; W3 doesn't add the documented `__multipart__: ClassVar[bool]` override. | Add `__multipart__` override to `BaseMethod` ClassVars in W3-T3. |
| L3 | low | wave-04 | `events/orders.py:OrderStatusChanged` ships in W4 but `Order` model lands in W5. Forward-ref to undefined symbol. | Move `events/orders.py` to W5, or stub payload as `dict[str, Any]` + TODO note. |

## DRY Failures

| # | Sev | Problem | Fix |
|---|---|---|---|
| D1 | medium | `evented` decision appears in overview / audit S8 / improvements FP-1 / decisions §21 / wave-03 / wave-04 / risks R3. | Single source = decisions §21; everywhere else: "see decisions §21". |
| D2 | low | "5 rps global + 1 rps per chat" appears in overview / decisions §13 / w4 (×2). | Same: decide once in decisions §13. |

## Tier Mismatch

| # | Sev | Problem | Fix |
|---|---|---|---|
| T1 | critical | Declared `library` tier but W4 ships systemd install, nginx, certbot, `/healthz`, mkdocs, Locust, full ops scripts, example bot w/ `--register` CLI. These are app-tier concerns. | Split repo into `avitoapi/` (pure library) + `examples/echo_bot/` (subproject with all the ops). Or formally re-tier the plan to `application` and own it. **Recommended:** split — keep library pure, move ops/Locust/install scripts into `examples/echo_bot/`. |
| T2 | high | LOC estimate (~12–15K) vs sum of waves (~18.5K). | Either revise overview estimate to ~18K, or trim W6 (autoteka/calltracking) to extras. |
| T3 | medium | `make_dispatcher()` pre-wires 5 specific middlewares. Library exposes building blocks. | Make `make_dispatcher()` thin (no pre-wired); the pre-wired bundle moves to `examples/echo_bot/dispatcher_factory.py`. |

## Missing Contracts

| # | Sev | Problem | Fix |
|---|---|---|---|
| M1 | critical | wave-04 `make_dispatcher()` — no signature, no return type, no defaults. | `def make_dispatcher(*, accounts: list[Client], fsm_storage: BaseStorage | None = None, idempotency_storage: BaseStorage | None = None, dlq: DeadLetterQueue | None = None, web: WebApp | None = None) -> Dispatcher` |
| M2 | critical | wave-04 `HMACSignatureMiddleware` — no `__init__` signature, no per-webhook-secret lookup. | `class HMACSignatureMiddleware(__init__(self, secret_provider: Callable[[str], Awaitable[str | None]], header_name: str = "x-avito-messenger-signature"))`. |
| M3 | high | wave-01 `OAuthClient` + `TokenCache` — prose only. | Spell out methods: `issue_client_credentials() -> Token`, `issue_authorization_code(...)`, `refresh_if_needed(...)`. |
| M4 | high | wave-01 `ClientConfig` fields — only env-loader subset enumerated. | Enumerate every field + type + default in W1-T2. |
| M5 | high | wave-03 `AvitoStorageKeyBuilder` + `StorageKey` shape unspecified. | Add signatures. |
| M6 | high | wave-04 `AvitoWebhookHandler` mentioned, no signature, no mount path, no error semantics. | Add. |
| M7 | medium | wave-02 `Item.archive()` listed but no `ArchiveItem` method-class. | Drop or add. |
| M8 | medium | wave-03 `Message.reply()` semantics across non-text variants. | Specify: always sends `TextMessage` reply; subclasses do NOT override. |
| M9 | medium | wave-05 `assert_order_transition(current, target, strict)` `strict` semantics. | Specify per skill `models.md`. |

## Missing Cheap Guards

| # | Sev | Problem | Fix |
|---|---|---|---|
| G1 | high | R5 (webhook 2s) only documented, not enforced. | W4 middleware `WebhookFastReturnMiddleware` wraps every handler in `evented.TaskTracker.spawn(...)` by default. |
| G2 | high | R6 rate-limit knobs not in W1 config. | Add to `ClientConfig` in W1: `rate_limit_global_rps: float = 5.0`, `rate_limit_per_chat_rps: float = 1.0`. |
| G3 | high | R11 category overrides config knob deferred. | `ClientConfig.category_overrides: dict[str, int] = {}` in W1. |
| G4 | high | R7 idempotency key doesn't survive process restart. | Persist key in `storage.namespaced("idempotency")` with 24h TTL keyed by `(method_class_name, body_hash)`. 5 lines in RestProtocol in W1. |
| G5 | high | R10 (unknown message type) — no regression test. | W3 fixture `unknown.json` + caplog assertion. |
| G6 | medium | R12 mypy + discriminated union gate. | W3-T1 acceptance: `mypy --strict` on `models/messenger.py`. |
| G7 | medium | R8 curl_cffi Windows fallback. | `sessions/__init__.py` factory: lazy curl → httpx fallback with WARNING. |
| G8 | medium | R1 webhook header name unverified. | Make `webhook_signature_header` a `ClientConfig` field, default `"x-avito-messenger-signature"`. |
| G9 | medium | client.py mixin split trigger not enforced. | W6 acceptance line: "if client.py >1500 LOC, split per FP-5". |
| G10 | low | factual: category ID type. | Avito uses **integer** category_id, not UUID. Fix `category_overrides` type in decisions §27, risk R11. |

---

**Verdict:** doctrine pages coherent; 4 buckets to fix before W1 implementation —
(a) `evented` install moved to W1, (b) ChallengeSolver/Proxy ABCs assigned to a wave,
(c) tier-vs-deliverables split (library vs ops), (d) load-bearing class signatures
(make_dispatcher, HMACSignatureMiddleware, OAuthClient).

# protocol/

Decouples *intent* (what the method-class declares) from *wire encoding*
(how the bytes leave the box). REST is the default and the only concrete
implementation in W1.

## Contract — `Protocol` ABC

- `validate_subclass(method_cls)` — called by `BaseMethod.__init_subclass__`
  at import time. Each protocol enforces its own required class-vars
  here (REST: `__http_method__`, `__endpoint__`, `__pre_encoded_fields__`
  must have matching validators).
- `build_request(method, config, host, ctx) -> PreparedRequest` — async to
  allow storage I/O (idempotency-key lookup).
- `decode_response(method, raw) -> T` — JSON-decode + `model_validate`
  into `__returning__`. Returns `raw.body` when `__binary_response__`.
- `is_idempotent(method) -> bool` — REST: GET/HEAD/OPTIONS true, plus
  `__retry_safe__ = True` opt-in.

## RestProtocol specifics

- `__path_fields__` fills `{name}` placeholders.
- Default routing: GET/HEAD/DELETE/OPTIONS → query. POST/PUT/PATCH → body.
- Explicit `__query_fields__` / `__body_fields__` overrides default.
- Auto-injects `Idempotency-Key` header for `__idempotent_mutation__=True`:
  - Key = `sha256(model_dump_json)[..16]` cached in
    `storage.namespaced("idempotency")` for 24h.
  - First retry of the same payload reuses the cached UUID — server
    deduplication works across process restarts.

## Don'ts

- Don't put encoding into the method-class; it just declares.
- Don't hardcode `Authorization` in the protocol layer — auth lives in
  middleware (see `auth/oauth.py:OAuthInjectorMiddleware`).
- Don't catch `ResponseDecodingError` inside the protocol; let it bubble
  to the funnel so it can be wrapped with `ErrorContext`.

# avitoapi/

Aiogram-style async SDK over the Avito Partner API. Public surface lives in
`avitoapi/__init__.py`; internals are organised per package.

## Top-level packages

| Package | Owns |
|---|---|
| `client.py` | Flat `Client` facade, lifecycle, universal `__call__`, public methods. |
| `config.py` | `ClientConfig` (Pydantic, strict, `.from_env()` loader). |
| `types.py` | `HostKey`, `HealthState`, `HealthStatus` value objects. |
| `logging.py` | Structlog config + redaction processor for secrets / tokens. |
| `exceptions.py` | One tree of SDK errors + `http_error_for_status`. |
| `methods/` | `BaseMethod[T]` + per-domain method-classes (W1: `accounts.py`). |
| `models/` | `AvitoObject` + per-domain Pydantic DTOs (W1: `accounts.py`, `common.py`). |
| `protocol/` | `Protocol` ABC + `RestProtocol` concrete. |
| `sessions/` | `BaseSession` funnel + `CurlSession` / `HttpxSession` backends. |
| `transport/` | `RetryPolicy` + default header builder. |
| `auth/` | `OAuthClient` + `OAuthInjectorMiddleware`. |
| `storage/` | `BaseStorage[TDoc, TId]` ABC + `MemoryStorage` (W1 only backend). |
| `transport/proxy/` | `BaseProxyTransport` ABC + `NoProxyTransport` (real rotators in W2). |

## Funnel — what a request goes through

```
await client.get_self()
  → Client.__call__(GetSelf())
  → method.as_(client).emit(client)
  → client.session.make_request(client, method)
      → protocol.build_request(method, config, host, ctx)
      → request_middlewares.dispatch(_terminal, prepared, ctx)
          → OAuthInjectorMiddleware (Authorization header, 403-token-expired refresh)
          → _terminal (retry loop, proxy acquire, _send → RawResponse, status mapping)
      → protocol.decode_response(method, raw)
      → AvitoObject.as_(client) if result is AvitoObject
  → typed Account
```

## Conventions

- Python 3.11+. Modern syntax (`X | None`, `Self`, `match`).
- Pydantic v2 strict everywhere (`ConfigDict(strict=True)`).
- One concept per file. `client.py` is the only file allowed ~300 LOC.
- Public surface gets docstrings; private helpers don't.
- `_MODULE.md` per package (this file is the top-level summary).
- No `print()`, no sync I/O in `async def`, no bare `except`.

# auth/

OAuth2 client for the Avito Partner API + the middleware that injects the
bearer token onto every request.

## Pieces

- `Token` — Pydantic model. `access_token: SecretStr`, absolute
  `expires_at: datetime` (UTC), optional `refresh_token`, `scope`.
- `TokenCache` — wraps a `BaseStorage` namespaced as `oauth:*` with
  token-shaped serialisation. TTL = remaining lifetime.
- `OAuthClient` — issues tokens via `client_credentials` (W1 path) and
  `authorization_code` (multi-tenant). `refresh_if_needed(token)` returns
  a fresh token when ≤60 s remain.
- `is_token_expired_403(body)` — Avito quirk detector. Returns `True`
  when the 403 body contains `token_expired` (case-insensitive, also
  `token-expired` / `token expired`).
- `OAuthInjectorMiddleware` — request-side middleware. Adds
  `Authorization: Bearer …` header. On 403 + `token_expired`: invalidate
  the cache, refresh, retry once. Holds a per-cache-key `asyncio.Lock`
  to prevent thundering-herd refresh on cold start.

## Storage layout

`storage.namespaced("oauth").get("acc:<client_id>:<user_id>")` →
serialised token. `OAuthInjectorMiddleware` builds the key via the
`cache_key_builder` callable passed at construction.

## Grant flavor knob

`ClientConfig.oauth_grant_endpoint` toggles between `post_form` (default,
matches `avito-api` 0.5.0) and `get_query` (matches older third-party
clients). Wire form differs but the endpoint URL (`/token`) is the same.

## Don'ts

- Don't log the token. The redaction processor in `logging.py` strips
  `access_token` / `authorization` / `cookie` automatically — keep it
  that way.
- Don't refresh inside `OAuthClient.refresh_if_needed` while holding a
  lock outside it; the middleware's `_ensure_token` does the locking.
- Don't store the token in process-local memory — always go through
  `TokenCache`. SaaS deployments share storage across clients but
  namespace per account.

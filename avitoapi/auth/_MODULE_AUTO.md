# auth/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

> Authentication helpers. See ``_MODULE.md``.

## oauth.py
```
# OAuth2 client for the Avito Partner API + bearer-token injector middleware.

_TOKEN_PATH = '/token'
_TOKEN_EXPIRED_RE = …
_REFRESH_LEEWAY = timedelta(seconds=60)

cls Token(BaseModel)
  # OAuth2 access token plus absolute expiry.
  is_expired() -> bool

cls TokenCache
  # Wraps :class:`BaseStorage` with token-shaped serialisation.
  __init__(storage: BaseStorage[object, str) -> None
  async get(key: str) -> Token | None
  async put(key: str, token: Token) -> None
  async invalidate(key: str) -> None

cls OAuthClient
  __init__(config: ClientConfig, http: BaseSession, cache: TokenCache) -> None
  async issue_client_credentials() -> Token
    # Exchange (client_id, client_secret) for a bearer token and cache it.
  async issue_authorization_code(code: str) -> Token
    # Exchange an authorization code (from the OAuth redirect) for a bearer token.
  cache_key_for() -> str
  async refresh_if_needed(token: Token) -> Token
    # Refresh when ≤60 s remaining or already expired; else return ``token`` as-is.
  is_token_expired_403(body: bytes | str?) -> bool
    # Match Avito's 403 + ``token_expired`` body heuristic. Case-insensitive.

cls OAuthInjectorMiddleware(RequestMiddleware)
  __init__(oauth: OAuthClient, cache_key_builder: Callable[[Any], str) -> None

_form_quote(value: str) -> str

```

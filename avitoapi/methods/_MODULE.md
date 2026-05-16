# methods/

One method-class per Avito endpoint, grouped per domain.

## Contract — `BaseMethod[T]`

- Pydantic v2 `BaseModel`, strict.
- Declares wire intent via ClassVars (see `_base.py` docstring for the full
  list). REST-specific: `__http_method__`, `__endpoint__`, `__path_fields__`,
  `__query_fields__`, `__body_fields__`, `__pre_encoded_fields__`,
  `__idempotent_mutation__`, `__retry_safe__`, `__multipart__`,
  `__binary_response__`. Universal: `__host__`, `__returning__`,
  `__protocol__`, `__breaker_path__`.
- Auto-binds the Generic param to `__returning__` — `BaseMethod[Account]`
  sets `__returning__ = Account` unless explicitly overridden. Mismatch
  between the Generic param and an explicit `__returning__` → import-time
  `MethodDeclarationError`.
- `__init_subclass__` runs `cls.__protocol__.validate_subclass(cls)` and
  refuses `__path__` (collides with Python package path attribute).
- `_client = PrivateAttr(default=None)`; set via `.as_(client)` or by
  `Client.__call__`.
- `await method` requires a bound client; otherwise raises
  `MethodNotBoundError`.

## Files (W1)

- `_base.py` — `BaseMethod[T]`.
- `accounts.py` — `GetSelf`.

W2 adds `items.py`, `balance.py`, `stats.py`. W3 adds `messenger.py`.
W5 adds `orders.py`, `reviews.py`, `promotion.py`, `cpa.py`.
W6 closes the surface with `autoload.py`, `calltracking.py`, `job.py`,
`realty.py`, `autoteka.py`.

`calltracking.GetCallRecording` sets `__binary_response__ = True`; the
awaited result is raw `bytes`, not a Pydantic model.

## Don'ts

- Don't use `__path__`. Use `__endpoint__`.
- Don't return `dict` from `__returning__`. Define a model or set
  `__returning__ = None`.
- Don't bypass `client.session.make_request()` from a method body.
- Don't await a naked method-class without binding. Use
  `await client(method)` or `await method.as_(client)`.

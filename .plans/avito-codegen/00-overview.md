# Plan — Avito SDK auto-builder (OpenAPI codegen)

**Goal.** A codegen ("auto-builder") that fetches the official Avito OpenAPI specs
from `developers.avito.ru` and regenerates `avitoapi/methods/*.py` + `avitoapi/models/*.py`
in the current house style — method-as-class with wire ClassVars, per-domain Pydantic
models, `Field(...)` constraints, `StrEnum`s, `AvitoObject` binding, and **auto-generated
bound methods** — fully automatically. Plus: remove `__path_fields__` (protocol derives
path fields from `{...}` placeholders in `__endpoint__`).

Analogous to lztforge: generated surface (methods / models / enums / bound facades) +
stable hand-written machinery (base classes, protocol, transport, client, pools,
pagination, events) that codegen never touches.

## Spec source (verified live 2026-07)

- `GET https://developers.avito.ru/web/1/openapi/list` → `[{slug,title,description}, …]` — 25 domains.
- `GET https://developers.avito.ru/web/1/openapi/info/{slug}` → `{"swagger": "<stringified OpenAPI 3.0 JSON>", "md": "…"}`.
- Spec is OpenAPI **3.0.0**; single server `https://api.avito.ru/`.
- 25 slugs: accounts-hierarchy, ads, auction, auth, autoload, autostrategy, autoteka,
  avito-promo, calltracking, cpa, cpxpromo, delivery-sandbox, item, job, messenger,
  order-management, promotion, ratings, realty-reports, sbc-gateway, stock-management,
  str, tariff, trxpromo, user.

## Mapping rules (derived from live spec analysis)

### Parameters
- Shared params live in `components/parameters/*` and are referenced by `$ref` — **resolve**.
- **Header params dropped**: `Content-Type` / `Authorization` are set by the transport; never emitted as method fields.
- `in: path` / `in: query` → method fields. Names snake_cased (`userId`→`user_id`, `itemId`→`item_id`).
- Path placeholders in `__endpoint__` are rewritten to the snake_cased field name so the
  protocol can `format_map` them with no `__path_fields__`.

### Schema → Pydantic (models codegen)
- `components/schemas/<Name>` (type object) → one model class, name = sanitized PascalCase.
- Response/nested models extend **`AvitoObject`** (binding + `populate_by_name`, `strict`,
  `extra="allow"`). Body payloads are flattened onto the method (no separate request model).
- Property type map: `string`→`str`; `string+date-time`→`datetime` (aware); `string+date`→`date`;
  `integer`→`int`; `number/float`→`float`; `boolean`→`bool`; `array`→`list[T]`; `object` inline→nested model;
  `$ref`→referenced model name.
- `enum` on a property → generated `StrEnum` (dedup by value-set; name `<Model><Prop>` or shared).
- `required` → `Field(...)`; otherwise `T | None = Field(default=None)`.
- Constraints: `minLength→min_length`, `maxLength→max_length`, `minimum→ge`, `maximum→le`,
  `exclusiveMinimum→gt`, `exclusiveMaximum→lt`, `pattern`, `default`, `description`/`title`→`description`.

### Operation → method-class (methods codegen)
- One class per `(path, verb)` with an `operationId`. Class name = `PascalCase(operationId)`.
  Skip `x-rate-limiter` / non-verb keys.
- `__http_method__ = verb.upper()`, `__endpoint__ = <snake-cased path template>`.
- `__returning__` via Generic: `BaseMethod[<200-schema-model>]`. Inline-object 200 →
  generated `<OpId>Response` model. Empty/204 → `BaseMethod[None]`. `application/pdf` or
  binary → `__binary_response__ = True` (returns `bytes`).
- requestBody `$ref` → the referenced schema's properties are flattened as **body fields**
  on the method (protocol routes non-path/non-query → body). `multipart/form-data` →
  `__multipart__ = True`, binary field → `Media`.
- `__idempotent_mutation__ = True` for write verbs (`PUT`/`PATCH`/`DELETE`; `POST` mutations
  that Avito marks idempotent) so retries auto-carry `Idempotency-Key`.

### Bound methods (auto-built — the new part)
- **Entity registry**: scan every path placeholder `{<noun>_id}` → tokens (`item_id`,
  `chat_id`, `order_id`, `review_id`, …). Each token binds to an *entity model* — a response
  model with an `id` field whose class name contains the noun — via heuristic + a curated
  override table in codegen config (Avito schema names are inconsistent, so overrides are the
  reliability net).
- **Binding rule**: an operation becomes a bound method on entity `E` iff its endpoint
  contains `{<E>_id}` and `E` is a registered entity. Collection/list endpoints (only
  `{user_id}`, or no entity id) stay top-level method-classes on the client only.
- **Generated body** (matches the current hand-written shape exactly):
  ```python
  def update_price(self, price: int) -> UpdatePrice:
      from ..methods.item import UpdatePrice
      client = self._require_client()
      return UpdatePrice(user_id=_resolve_user_id(client), item_id=self.id, price=price).as_(client)
  ```
  args = method fields minus auto-filled path fields; `{item_id}`←`self.id`,
  `{user_id}`←`_resolve_user_id(client)`. Name = `snake_case(operationId)`.
- Regen-safe: bound methods are part of the generated model file (like lztforge facades) —
  no preserved-region needed.

## `__path_fields__` removal (surgical)

- `methods/_base.py`: drop the `__path_fields__` ClassVar + its docstring bullet.
- `protocol/rest.py`: `_render_path` + `_route_fields` derive path field names from the
  endpoint via `re.findall(r"{(\w+)}", endpoint)` (cached per class). `validate_subclass`
  gains a check: every `{placeholder}` must have a matching model field.
- All method files: strip `__path_fields__ = frozenset({…})` (regenerated anyway).
- Tests referencing `__path_fields__` updated; `methods/_MODULE.md` doc updated.

## Layout

```
avitoapi/codegen/
  __init__.py
  __main__.py          # `python -m avitoapi.codegen [--slug item] [--all] [--dry-run]`
  fetch.py             # spec list + per-slug fetch (+ on-disk cache)
  spec.py              # OpenAPI IR: resolve $ref, normalize params, snake_case
  naming.py            # slug→module, operationId→ClassName, prop→field, StrEnum names
  types.py             # OpenAPI schema → python type + Field(...) constraints
  entities.py          # entity registry + bound-method binding rules (+ overrides table)
  emit_models.py       # models/<domain>.py renderer
  emit_methods.py      # methods/<domain>.py renderer
  render.py            # shared code-emit helpers (imports, headers, formatting)
  config.py            # slug↔file aliases, entity overrides, host, skip-lists
```

- Generated files carry a header: `# AUTO-GENERATED by avitoapi.codegen — regenerate, do not hand-edit.`
- Output is run through `ruff format` + `ruff --fix` as a final pass.

## NON-generated (stable machinery, never touched by codegen)

`methods/_base.py`, `models/_base.py`, `models/common.py` (`Money`, `Page`, `TZDatetime`,
`AvitoErrorBody`), `protocol/`, `transport/`, `client.py`, `dispatcher.py`, `events/`,
`routers/`, `pagination/`, `storage/`, `sessions/`, `fsm/`, `breaker/`, `exceptions.py`,
`logging.py`, `types.py`, plus the shared `_resolve_user_id` account-context helper.

## Known losses vs current hand-tuned code (flagged)

Codegen cannot infer semantics that were hand-added: `Money`/`Decimal` (spec says
`number`→`float`), state machines (`ORDER_TRANSITIONS`), curated class names
(`ListItems`/`GetItem` vs `GetItemsInfo`/`GetItemInfo`), PII markers, `PageMethod`
pagination wiring. All of it is preserved in `avitoapi/_backup_handwritten/`. Post-regen we
re-layer the high-value ones (Money, pagination base, state tables) as small curated
overrides on top of the generated surface.

## Build order

1. `__path_fields__` removal + protocol placeholder-derivation (behaviour-preserving; tests green).
2. Codegen package (fetch → IR → naming/types → entities → emit).
3. **Pilot**: generate `item` domain only, diff against current hand-written `items.py` /
   `models/items.py`, show output — gate before mass regen.
4. On go: regenerate all 25 domains, wire slug→file aliases, re-layer curated overrides.
5. Tail: ruff/mypy/pytest, `_MODULE.md` sync, review passes.

## Tests

- Codegen unit tests: `$ref` resolution, snake_case, constraint mapping, one golden
  `item`-domain snapshot (spec fixture → expected emitted module).
- Existing SDK tests must stay green after `__path_fields__` removal.

# Wave 02 — Items + Stats + Balance + Pagination + Storage backends

## Delivers
Items domain (read + price/VAS mutate), stats domain (bulk shallow + per-
item), balance domain (real + bonus + history), two paginators, two
additional storage backends.

## Releasable definition
- [ ] `client.list_items()` returns async-iterable paginator yielding `Item` models.
- [ ] `client.get_item(item_id)`, `client.update_item_price(...)`,
      `client.apply_vas(...)`, `client.apply_vas_package(...)`.
- [ ] `client.item_stats_shallow(item_ids=[...])` enforces ≤200 ids client-side.
- [ ] `client.get_balance()`, `client.get_balance_bonus()`,
      `client.iter_operations_history()`.
- [ ] `await item.update_price(123)`, `await item.apply_vas("premium")` — bound methods.
- [ ] `pip install -e .[redis]` + `RedisStorage` round-trips a token under `fakeredis`.
- [ ] `pip install -e .[mongo]` + `MongoStorage` round-trips a token under `mongomock`.
- [ ] `IndexPaginator` and `TimeWindowPaginator` unit tests green incl. runaway-guard.
- [ ] `ruff` + `mypy --strict` clean.

## Logic
- New `methods/items.py`, `methods/stats.py`, `methods/balance.py`.
- New `models/items.py`, `models/stats.py`, `models/balance.py`.
- New `pagination/` package: `base.py` (BasePaginator + runaway-guard +
  state cache), `index.py` (IndexPaginator[T] for page/per_page),
  `time_window.py` (TimeWindowPaginator[T] for date_time_from/to + offset).
- New `storage/redis.py` (lazy `import redis.asyncio`), `storage/mongo.py`
  (lazy `import motor.motor_asyncio`). Both implement `BaseStorage[TDoc, TId]`
  + `namespaced()`.
- `Item.update_price` / `Item.apply_vas` use `_require_client()` and call
  back through `await self._client(UpdateItemPrice(item_id=self.id, ...))`.
- `client.py` gains 12 new methods, grouped under `# --- ITEMS ---`,
  `# --- STATS ---`, `# --- BALANCE ---` section headers. File still
  single-class (well under 1500-LOC mixin trigger).
- Hard-cap `item_stats_shallow.item_ids` at 200 with a Pydantic validator
  on the method-class (matches Avito documented limit).

## Files (additions)
```
avitoapi/
├── methods/items.py            ← ListItems, GetItem, UpdateItemPrice, ApplyVas,
│                                  ApplyVasPackage, ApplyVasV2, ArchiveItem
├── methods/stats.py            ← ItemStatsShallow, ItemStatsDeep, CallStats, Spendings
├── methods/balance.py          ← GetBalance, GetBalanceBonus, OperationsHistory
├── models/items.py             ← Item, ItemStatus(StrEnum), ItemCategory,
│                                  VasService(StrEnum), VasOrderResult
├── models/stats.py             ← ItemViewStats, ItemContactStats, CallStat
├── models/balance.py           ← Balance, BalanceBonus, Operation, OperationType(StrEnum)
├── pagination/__init__.py
├── pagination/_MODULE.md
├── pagination/base.py          ← BasePaginator + max_pages guard + state cache
├── pagination/index.py         ← IndexPaginator[T]
├── pagination/time_window.py   ← TimeWindowPaginator[T]
├── storage/redis.py            ← RedisStorage (lazy redis import; raises clear error
│                                  if extras not installed)
└── storage/mongo.py            ← MongoStorage (lazy motor import)
tests/
├── unit/test_paginator_index.py
├── unit/test_paginator_time_window.py
├── unit/test_storage_redis.py  ← uses fakeredis
├── unit/test_storage_mongo.py  ← uses mongomock
└── fixtures/
    ├── items_list_p1.json
    ├── items_list_p2.json
    ├── items_single.json
    ├── item_stats_shallow.json
    ├── balance.json
    └── operations_history.json
```

## Types
- `Item(BoundModel)` — `id`, `status: ItemStatus`, `title`, `price: Money`,
  `category: ItemCategory`, `url: HttpUrl`, `created_at: datetime`,
  `vas: list[VasService]`, etc. Bound methods: `update_price(amount)`,
  `apply_vas(name)`, `archive()`.
- `ItemStatus`: `active | archived | blocked | removed | rejected | old`.
- `Balance` — `real: Money`, `as_of: datetime`. `BalanceBonus` — `bonus: Money`.
- `Operation` — `id`, `kind: OperationType`, `amount: Money`,
  `created_at: datetime`, `meta: dict[str, str]`.

## Tasks (DAG)
```yaml
- id: W2-T1
  title: "pagination/ package (base, index, time_window)"
  files: [avitoapi/pagination/*]
  depends_on: []
  parallelizable: true

- id: W2-T2
  title: "storage/redis.py + storage/mongo.py (lazy)"
  files: [avitoapi/storage/redis.py, avitoapi/storage/mongo.py]
  depends_on: []
  parallelizable: true

- id: W2-T3
  title: "models/items.py + methods/items.py"
  files: [avitoapi/models/items.py, avitoapi/methods/items.py]
  depends_on: [W2-T1]
  parallelizable: true

- id: W2-T4
  title: "models/stats.py + methods/stats.py"
  files: [avitoapi/models/stats.py, avitoapi/methods/stats.py]
  depends_on: []
  parallelizable: true

- id: W2-T5
  title: "models/balance.py + methods/balance.py"
  files: [avitoapi/models/balance.py, avitoapi/methods/balance.py]
  depends_on: [W2-T1]
  parallelizable: true

- id: W2-T6
  title: "Client public methods + bound-method wiring on Item"
  files: [avitoapi/client.py]
  depends_on: [W2-T3, W2-T4, W2-T5]
  parallelizable: false

- id: W2-T7
  title: "Unit tests for paginators, storage backends, items/stats/balance fixtures"
  files: [tests/unit/test_paginator_*.py, tests/unit/test_storage_*.py,
          tests/unit/test_items.py, tests/unit/test_stats.py,
          tests/unit/test_balance.py, tests/fixtures/*.json]
  depends_on: [W2-T6]
  parallelizable: false
```

## Risks
- Avito's `items` response shape varies by category (Realty has extra
  fields, Job too). Strategy: model the shared subset strictly + accept
  unknown fields via `model_config = ConfigDict(extra="allow")` on `Item`
  with a `raw: dict[str, Any] | None = None` escape hatch. Specialised
  subtypes can ship in wave-05/06 if demand emerges.
- Page numbers start at 1 (not 0) per covox docs. IndexPaginator default
  `start_page = 1`, configurable.

## Hardcodes introduced
None.

## Hardcodes replaced
| What | Was in wave | Now backed by |
|---|---|---|
| `MemoryStorage` is the only storage backend | wave-01 | `[redis]` extra → `RedisStorage`; `[mongo]` extra → `MongoStorage` (opt-in via extras) |

## Acceptance checklist
- [ ] All 7 tasks land
- [ ] Unit tests for all new methods green
- [ ] `[redis]` and `[mongo]` extras install cleanly
- [ ] Bound methods on Item work
- [ ] `_MODULE.md` exists in `pagination/`

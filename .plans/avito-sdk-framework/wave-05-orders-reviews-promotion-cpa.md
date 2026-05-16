# Wave 05 — Orders + Reviews + Promotion + CPA + Categories (post-release)

## Delivers
Order lifecycle (DBS), reviews, promotion v1 (bids + BBIP + forecast),
CPA v3 (balance, calls/chats by time, complaints), pre-populated
`categories/` static module.

## Releasable definition
- [ ] All listed methods work end-to-end vs. FakeSession fixtures.
- [ ] `Order` state-machine test covers documented transition table:
      `new → confirmed → shipped → delivered → completed` + cancel/refund
      branches. Invalid transitions raise `InvalidStateTransition`.
- [ ] `await order.refund(reason=...)` bound method.
- [ ] `await review.reply("Спасибо!")` bound method.
- [ ] CPA balance + calls-by-time round-trip.
- [ ] `categories.Realty.MOSCOW_FLATS_BUY` resolves to its UUID.
- [ ] `ruff` + `mypy --strict` clean. Minor version bump to `v0.2.0`.

## Files (additions)
```
avitoapi/
├── methods/orders.py           ← ListOrders, GetOrder, ChangeOrderStatus,
│                                  TransferDeliveryTerms, TransferTrackNumber,
│                                  RefundOrder
├── methods/reviews.py          ← ListReviews, GetReviewInfo, ReplyToReview,
│                                  DeleteReviewReply
├── methods/promotion.py        ← ListActivePromotions, DropPromotion,
│                                  ListBids, CreateBbipOrder, BbipForecast
├── methods/cpa.py              ← CpaBalance, CallsByTime, ChatsByTime,
│                                  ChatByActionId, ListComplaints, CreateComplaint,
│                                  CancelComplaint
├── models/orders.py            ← Order, OrderStatus(StrEnum), OrderTransition table,
│                                  assert_order_transition, DeliveryTerm, TrackInfo
├── models/reviews.py           ← Review, ReviewReply, Rating
├── models/promotion.py         ← Promotion, Bid, BbipOrder, BbipForecast
├── models/cpa.py               ← CpaBalanceInfo, CallByTime, ChatByTime, Complaint
├── categories/
│   ├── __init__.py
│   ├── _MODULE.md
│   ├── vehicles.py             ← Cars, Motorcycles, Trucks, … UUID maps
│   ├── realty.py               ← Flats, Houses, Commercial, … UUID maps
│   ├── job.py                  ← VacanciesByIndustry, CvsByIndustry
│   ├── services.py
│   ├── electronics.py
│   └── hobbies.py
tests/
├── unit/test_orders.py
├── unit/test_order_state_machine.py
├── unit/test_reviews.py
├── unit/test_promotion.py
├── unit/test_cpa.py
└── fixtures/
    ├── orders/*.json
    ├── reviews/*.json
    ├── promotion/*.json
    └── cpa/*.json
```

## Types
- `Order(BoundModel)` — `id`, `status: OrderStatus`, `item_id`, `buyer_id`,
  `seller_id`, `total: Money`, `delivery: DeliveryTerm | None`,
  `track: TrackInfo | None`, `created_at`, `updated_at`. Bound:
  `change_status(new)`, `transfer_delivery_terms(...)`,
  `transfer_track_number(carrier, code)`, `refund(reason)`.
- `OrderStatus`: `new | confirmed | shipped | delivered | completed |
  cancelled | refunded`.
- `ORDER_TRANSITIONS: dict[OrderStatus, frozenset[OrderStatus]]` — transition
  table. `assert_order_transition(current, target, strict)` per skill `models.md`.

## Tasks
```yaml
- id: W5-T1
  title: "models/orders.py + state machine"
  files: [avitoapi/models/orders.py]
  depends_on: []
  parallelizable: true

- id: W5-T2
  title: "methods/orders.py + Client public methods + bound methods"
  files: [avitoapi/methods/orders.py, avitoapi/client.py]
  depends_on: [W5-T1]
  parallelizable: false

- id: W5-T3
  title: "models/reviews.py + methods/reviews.py + Client + bound methods"
  files: [avitoapi/models/reviews.py, avitoapi/methods/reviews.py, avitoapi/client.py]
  depends_on: []
  parallelizable: true

- id: W5-T4
  title: "models/promotion.py + methods/promotion.py + Client"
  files: [avitoapi/models/promotion.py, avitoapi/methods/promotion.py, avitoapi/client.py]
  depends_on: []
  parallelizable: true

- id: W5-T5
  title: "models/cpa.py + methods/cpa.py + Client"
  files: [avitoapi/models/cpa.py, avitoapi/methods/cpa.py, avitoapi/client.py]
  depends_on: []
  parallelizable: true

- id: W5-T6
  title: "categories/ — populate top-level Avito category UUID maps"
  files: [avitoapi/categories/**]
  depends_on: []
  parallelizable: true

- id: W5-T7
  title: "Tests for all new domains incl. state machine + fixtures"
  files: [tests/unit/test_orders*.py, tests/unit/test_reviews.py,
          tests/unit/test_promotion.py, tests/unit/test_cpa.py,
          tests/fixtures/orders/**, tests/fixtures/reviews/**,
          tests/fixtures/promotion/**, tests/fixtures/cpa/**]
  depends_on: [W5-T2, W5-T3, W5-T4, W5-T5, W5-T6]
  parallelizable: false

- id: W5-T8
  title: "Bump version to 0.2.0; update CHANGELOG"
  files: [pyproject.toml, CHANGELOG.md, avitoapi/__init__.py]
  depends_on: [W5-T7]
  parallelizable: false
```

## Risks
- DBS order surface is documented unevenly across third-party clients;
  some endpoints are platform-specific (Avito Доставка vs. self-pickup).
  Strategy: ship the union of documented endpoints behind a single
  domain; mark less-tested ones `@experimental` per skill `utils.py`.
- Categories UUID map is a moving target — Avito rotates categories
  occasionally. Ship the snapshot, document the source URL + date in
  each file's `_MODULE.md`, and accept that consumers may need to
  override.

## Hardcodes introduced
| What | Where | Replaced in wave |
|---|---|---|
| Order state names + transitions snapshot from Avito docs as of 2026-05 | `models/orders.py` | none — updates via subsequent minor versions when Avito changes the spec |
| Category UUIDs snapshot | `categories/` | none — same approach, doc snapshot date in each file |

## Hardcodes replaced
None.

## Acceptance checklist
- [ ] All 8 tasks land
- [ ] Order state-machine test covers full transition matrix
- [ ] CHANGELOG `v0.2.0`
- [ ] `_MODULE.md` exists in `categories/`

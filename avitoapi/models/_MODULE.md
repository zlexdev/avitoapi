# models/

Per-domain Pydantic v2 DTOs. Each file owns its enums, value objects,
response shapes, state-machine table, and bound action methods.

## Contract

- All response models extend `AvitoObject` (`models/_base.py`).
  - `model_config = ConfigDict(populate_by_name=True, strict=True)`.
  - Private `_client` is set by `as_(client)` after decode.
  - `as_(client)` recursively binds nested `AvitoObject` children
    (inside `list` and `dict` containers too).
  - `_require_client()` raises `ModelNotBoundError` when bound methods
    fire on a hand-built instance.
- Request payload models extend plain `BaseModel` with strict config —
  they don't need binding.
- `models/common.py` ships cross-domain primitives: `Money` (always
  `Decimal`), `Currency`, `Page[T]`, `AvitoErrorBody`.
- Files: `accounts.py` ships `Account` (W1). Items, messenger, orders,
  reviews, etc. land in W2–W6.
- **W5 ships:** `orders.py` (`Order`, `OrderStatus`, `ORDER_TRANSITIONS`,
  `assert_order_transition`, `DeliveryTerm`, `TrackInfo`, `OrderList`),
  `reviews.py` (`Rating`, `RatingInfo`, `Review`, `ReviewReply`,
  `ReviewList`), `promotion.py` (`Promotion`, `Bid`, `BbipOrder`,
  `BbipForecast`, `PromotionList`, `BidList`), `cpa.py`
  (`CpaBalanceInfo`, `CallByTime`, `ChatByTime`, `Complaint`,
  `ComplaintStatus`, `CallList`, `ChatList`, `ComplaintList`). List
  envelopes that hold AvitoObject children (`OrderList`, `ReviewList`,
  `ChatList`, `ComplaintList`) inherit `AvitoObject` so the funnel
  cascades the client into nested rows — enabling `order.refund()`,
  `review.reply_to(...)`, `complaint.cancel()` after a paginated fetch.

## State machines

- Order lifecycle is a declared transition table:
  `ORDER_TRANSITIONS: dict[OrderStatus, frozenset[OrderStatus]]` in
  `orders.py`. `assert_order_transition(current, target, strict)` raises
  `InvalidStateTransition` on an illegal jump when `strict=True`, or
  logs a warning when `strict=False` (used when Avito ships a new state
  before the SDK table is refreshed).
- **PII fields (W6 `job.py`):** `ResumeContact.email` / `ResumeContact.phone`
  carry candidate PII. The project's `logging.py` redactor MUST mask them in
  any structured-log binding that includes a `ResumeContact` instance. The
  redactor consumes the marker `_resume_pii_fields()` from `models/job.py`
  when it lifts the dependency; today the function is a no-op marker so the
  dependency is import-pinnable without further wiring.

## Don'ts

- Don't use `float` for money. `Money.amount` is `Decimal`.
- Don't compare enum members to raw strings — `order.state is OrderState.PAID`.
- Don't make bound methods `async def`. They return a method-class
  instance with the client attached; the caller awaits it. That preserves
  the "method-class is an awaitable wire spec" mental model and lets
  callers wrap the method in middleware before awaiting.
- Don't surface `_client` to user code; access via `_require_client()`.

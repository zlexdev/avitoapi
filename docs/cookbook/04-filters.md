# Filters (`F`, `MagicFilter`, custom callables)

Every observer accepts zero or more predicates — the handler fires only
when **every** predicate returns truthy.

---

## Magic filter (`F`)

`F` captures attribute / item access and turns them into a callable
predicate that takes one event and returns `bool`.

```python
from avitoapi import F

# attribute chain
@router.new_message(F.message.type == "text")
async def text(event, ctx): ...

# nested attribute, comparison
@router.order_created(F.amount > 100_000)
async def big_order(event, ctx): ...

# index access
@router.new_message(F.payload["chat_id"] == "c-42")
async def specific_chat(event, ctx): ...
```

Operators supported: `==`, `!=`, `<`, `<=`, `>`, `>=`, `&` (and), `|`
(or), `~` (not).

---

## Combinations

Boolean operators build composite predicates without runtime cost:

```python
# AND
@router.new_message(
    (F.message.type == "text") & ~F.message.text.contains("spam")
)
async def clean_text(event, ctx): ...

# OR
@router.new_message(
    (F.message.type == "image") | (F.message.type == "video")
)
async def media(event, ctx): ...

# Multiple positional predicates = implicit AND
@router.order_created(
    F.amount > 1000,
    F.currency == "RUB",
    F.payment_method == "card",
)
async def big_card(event, ctx): ...
```

---

## Built-in helpers

```python
# set membership — snapshot taken at decoration time
@router.order_status_changed(
    F.status.in_({OrderStatus.SHIPPED, OrderStatus.DELIVERED})
)
async def shipped(event, ctx): ...

# substring / element check
@router.new_message(F.message.text.contains("/start"))
async def start(event, ctx): ...

# arbitrary predicate (gives you back a MagicFilter for chaining)
@router.order_created(F.amount.func(lambda v: v > 1000 and v < 5000))
async def mid_range(event, ctx): ...
```

`.func(fn)` wraps any callable into the chain — use it for predicates
the built-ins can't express. The function gets the resolved value
(`event.amount` in the example), not the whole event.

---

## Plain callables (no `F`)

Any `Callable[[Event], bool]` is a valid filter. Useful for predicates
that need outside state (config, time, async lookups that you've
pre-warmed).

```python
def is_business_hours(event) -> bool:
    from datetime import UTC, datetime
    hour = datetime.now(UTC).hour
    return 9 <= hour < 21

@router.new_message(is_business_hours)
async def daytime_only(event, ctx): ...
```

Filter exceptions are caught — a predicate that raises is treated as
"didn't match", never as a propagation error. Good for safety;
inconvenient when you want loud failures. Prefer pure predicates and
log inside, if at all.

---

## Re-using a filter

Predicates are plain objects — bind once, reuse anywhere:

```python
is_text = F.message.type == "text"
is_image = F.message.type == "image"
not_spam = ~F.message.text.contains("spam")

@router.new_message(is_text & not_spam)
async def clean_text(event, ctx): ...

@router.new_message(is_image)
async def image(event, ctx): ...
```

This is the recommended shape for filters used across multiple modules
— define them once next to the event types and import.

---

## Pipeline-stage filters (`when=`)

The same predicate shape gates individual pipeline stages — see
[09-pipeline.md](09-pipeline.md):

```python
from avitoapi import Pipeline, F

pipeline = Pipeline(name="ship-order")

@pipeline.stage("notify-sms", when=F.preferences.sms == True)
async def sms(event, ctx): ...

@pipeline.stage("notify-email", when=F.preferences.email == True)
async def email(event, ctx): ...
```

Stages whose `when` returns `False` are marked complete (skipped) and
the pipeline advances — no exception, no replay.

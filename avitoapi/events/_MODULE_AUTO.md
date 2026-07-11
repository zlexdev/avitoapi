# events/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

> Typed Avito events flowing through the Dispatcher.

## __init__.py
```
# Typed Avito events flowing through the Dispatcher.


```

## _base.py
```
# ``Event`` — root of the typed Pydantic event hierarchy.


cls Event(BaseModel)
  dedup_key() -> str
    # Stable idempotency key — event name + scalar id-fields, timestamps excluded.

cls RawWebhookEvent(Event)
  dedup_key() -> str

```

## autoload.py
```
# Autoload-domain events — XML feed pipeline lifecycle.


cls AutoloadEvent(BaseEvent)
  # Common ancestor of every autoload-domain event.

cls AutoloadReportReady(AutoloadEvent)
  # A processed feed report is ready for download.

cls AutoloadFailed(AutoloadEvent)
  # The feed run terminated with fatal errors and no items processed.

```

## balance.py
```
# Balance-domain events — emitted by the balance/operations poller.


cls BalanceEvent(BaseEvent)
  # Common ancestor of every balance/billing event.

cls BalanceChanged(BalanceEvent)
  # The real-money balance changed (any direction).

cls BalanceToppedUp(BalanceEvent)
  # An operation of type ``top_up`` (or equivalent) was observed.

cls BalanceLow(BalanceEvent)
  # The current balance crossed the configured low-watermark threshold.

cls BonusReceived(BalanceEvent)
  # A bonus credit landed on the account (separate sub-balance).

```

## calltracking.py
```
# Calltracking-domain events — emitted by the calls poller.


cls CalltrackingEvent(BaseEvent)
  # Common ancestor of every calltracking event.

cls CallReceived(CalltrackingEvent)
  # A new call landed against one of the seller's items.

cls CallEnded(CalltrackingEvent)
  # The call finished — duration + answered flag are final.

cls CallRecordingReady(CalltrackingEvent)
  # A recording URL is now downloadable for the call.

```

## delivery.py
```
# Delivery / parcel lifecycle events.


cls DeliveryEvent(BaseEvent)
  # Common ancestor of every delivery-domain event.

cls ParcelStatusChanged(DeliveryEvent)
  # A parcel transitioned to a new tracking state (in-transit, delivered, etc.).

cls ParcelHandedOver(DeliveryEvent)
  # The seller handed the parcel to the carrier (first physical scan).

cls ParcelDelivered(DeliveryEvent)
  # Terminal happy-path: the buyer received the parcel.

cls ParcelReturned(DeliveryEvent)
  # The parcel was returned to the seller (refund / no-show / refused).

cls AnnouncementTracked(DeliveryEvent)
  # A delivery announcement has a new tracking event.

```

## items.py
```
# Item-listing lifecycle events — emitted by the items poller.


cls ItemStatus(StrEnum): ACTIVE, ARCHIVED, BLOCKED, REMOVED, REJECTED, OLD, UNKNOWN

cls ItemEvent(BaseEvent)
  # Common ancestor of every item-domain event.

cls ItemStatusChanged(ItemEvent)
  # An item moved between two lifecycle states.

cls ItemPublished(ItemEvent)
  # An item became active and is now visible on the site.

cls ItemBlocked(ItemEvent)
  # Moderation blocked the item.

cls ItemUnblocked(ItemEvent)
  # A previously blocked item came back to active.

cls ItemSold(ItemEvent)
  # The seller marked the item as sold.

cls ItemArchived(ItemEvent)
  # An item was removed from public surface and moved to archive.

```

## lifecycle.py
```
# SDK lifecycle events — emitted by the Dispatcher / Client itself.


cls LifecycleEvent(BaseEvent)
  # Common ancestor of every SDK-internal lifecycle event.

cls Startup(LifecycleEvent)
  # The Dispatcher finished wiring accounts and is ready to accept events.

cls Shutdown(LifecycleEvent)
  # Graceful shutdown started — handlers should finalise side effects.

cls TokenRefreshed(LifecycleEvent)
  # An OAuth token was refreshed for one of the bound accounts.

cls AuthFailed(LifecycleEvent)
  # OAuth refresh failed — the account is now in a degraded state.

cls WebhookError(LifecycleEvent)
  # An inbound webhook failed to parse / verify (bad signature, malformed body).

cls PollError(LifecycleEvent)
  # A poller (orders / items / reviews / ...) crashed mid-iteration.

```

## messenger.py
```
# Messenger domain events.


cls MessageType(StrEnum): TEXT, IMAGE, LINK, ITEM, LOCATION, VOICE, CALL, FILE, SYSTEM, APP_CALL, DELETED, UNKNOWN

cls Message(AvitoObject)

cls MessengerEvent(BaseEvent)
  # Common ancestor of every messenger-domain event.

cls NewMessage(MessengerEvent)
  dedup_key() -> str

cls MessageRead(MessengerEvent)
  # The counterparty marked a message as read.

cls ChatArchived(MessengerEvent)
  # A chat was archived (by the user or by the system).

cls ChatBlacklisted(MessengerEvent)
  # The counterparty was added to the account blacklist.

cls VoiceFileResolved(MessengerEvent)

```

## orders.py
```
# Order-domain events — emitted by SDK pollers around DBS/CPA order lifecycle.


cls OrderStatus(StrEnum): NEW, CONFIRMED, SHIPPED, DELIVERED, COMPLETED, CANCELLED, REFUNDED, UNKNOWN

cls OrderEvent(BaseEvent)
  # Common ancestor of every order-domain event.

cls OrderStatusChanged(OrderEvent)
  # An order moved between two lifecycle states.

cls OrderCreated(OrderEvent)
  # A new order was created on the seller's account.

cls OrderConfirmed(OrderEvent)
  # The seller (or Avito on auto-rules) confirmed the order.

cls OrderShipped(OrderEvent)
  # A track number was attached and the order entered shipping.

cls OrderDelivered(OrderEvent)
  # The carrier reported successful delivery.

cls OrderCompleted(OrderEvent)
  # The buyer accepted the order — terminal happy-path state.

cls OrderCancelled(OrderEvent)
  # The order was cancelled before delivery.

cls OrderRefunded(OrderEvent)
  # An order entered the refunded terminal state.

```

## reviews.py
```
# Review-domain events — emitted by the reviews poller.


cls ReviewEvent(BaseEvent)
  # Common ancestor of every review-domain event.

cls ReviewReceived(ReviewEvent)
  # A buyer left a new review on one of the seller's items.

cls ReviewAnswered(ReviewEvent)
  # The seller answered a review (or had one auto-answered).

```

"""Domain routers — one ``evented.Router`` subclass per event-bearing domain.

Each router exposes typed ``HandlerManager`` (== ``evented.EventObserver``)
attributes named after the events the domain emits. Aiogram-style usage:

    @router.new_message()
    async def handle(event: NewMessage) -> None: ...

    @router.text_message()
    async def handle_text(event: NewMessage) -> None: ...

Routers are stitched together by :class:`avitoapi.Dispatcher` (or
``evented.Dispatcher`` directly) — ``dispatcher.include_router(router)``.

Each observer is a *named manager* under the router, pre-filtered on the
event class (and, for messenger sub-types, on the message's
``MessageType``). Filter evaluation is done by ``evented`` itself when
``dispatcher.event_entry(event)`` fans the event out.

Requires ``evented`` (private dep at ``github.com/zlexdev/evented``); install
via ``pip install 'git+https://${GH_TOKEN}@github.com/zlexdev/evented.git'``.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

import evented

from ..events.autoload import AutoloadFailed, AutoloadReportReady
from ..events.balance import (
    BalanceChanged,
    BalanceLow,
    BalanceToppedUp,
    BonusReceived,
)
from ..events.calltracking import CallEnded, CallReceived, CallRecordingReady
from ..events.delivery import (
    AnnouncementTracked,
    ParcelDelivered,
    ParcelHandedOver,
    ParcelReturned,
    ParcelStatusChanged,
)
from ..events.items import (
    ItemArchived,
    ItemBlocked,
    ItemPublished,
    ItemSold,
    ItemStatusChanged,
    ItemUnblocked,
)
from ..events.lifecycle import (
    AuthFailed,
    PollError,
    Shutdown,
    Startup,
    TokenRefreshed,
    WebhookError,
)
from ..events.messenger import (
    ChatArchived,
    ChatBlacklisted,
    MessageRead,
    NewMessage,
    VoiceFileResolved,
)
from ..events.orders import (
    OrderCancelled,
    OrderCompleted,
    OrderConfirmed,
    OrderCreated,
    OrderDelivered,
    OrderRefunded,
    OrderShipped,
    OrderStatusChanged,
)
from ..events.reviews import ReviewAnswered, ReviewReceived

if TYPE_CHECKING:
    from ..models.messenger import MessageType

Router = evented.Router
EventObserver = evented.EventObserver  # alias of evented.HandlerManager


def _isinst(cls: type) -> Any:
    """Build an ``event_filter`` callable that matches ``isinstance(event, cls)``."""

    return lambda ev: isinstance(ev, cls)


def _msg_of(kind: MessageType) -> Any:
    """``NewMessage`` filter narrowing to one ``MessageType`` variant."""

    return lambda ev: isinstance(ev, NewMessage) and getattr(ev.message, "type", None) == kind


class MessengerRouter(Router):
    """Inbound messenger surface.

    Observers split ``NewMessage`` by ``MessageType`` so handlers don't
    have to write the ``isinstance``/``F.message.type == ...`` boilerplate.
    """

    def __init__(self) -> None:
        super().__init__(name="messenger")
        from ..models.messenger import MessageType  # noqa: PLC0415 — lazy to avoid cycle

        self.new_message = self.manager("messenger.new_message", event_filter=_isinst(NewMessage))
        self.message_read = self.manager("messenger.message_read", event_filter=_isinst(MessageRead))
        self.chat_archived = self.manager("messenger.chat_archived", event_filter=_isinst(ChatArchived))
        self.chat_blacklisted = self.manager("messenger.chat_blacklisted", event_filter=_isinst(ChatBlacklisted))
        self.voice_file_resolved = self.manager(
            "messenger.voice_file_resolved", event_filter=_isinst(VoiceFileResolved),
        )

        self.text_message = self.manager("messenger.text_message", event_filter=_msg_of(MessageType.TEXT))
        self.image_message = self.manager("messenger.image_message", event_filter=_msg_of(MessageType.IMAGE))
        self.link_message = self.manager("messenger.link_message", event_filter=_msg_of(MessageType.LINK))
        self.item_message = self.manager("messenger.item_message", event_filter=_msg_of(MessageType.ITEM))
        self.location_message = self.manager(
            "messenger.location_message", event_filter=_msg_of(MessageType.LOCATION),
        )
        self.voice_message = self.manager("messenger.voice_message", event_filter=_msg_of(MessageType.VOICE))
        self.call_message = self.manager("messenger.call_message", event_filter=_msg_of(MessageType.CALL))
        self.file_message = self.manager("messenger.file_message", event_filter=_msg_of(MessageType.FILE))
        self.system_message = self.manager("messenger.system_message", event_filter=_msg_of(MessageType.SYSTEM))
        self.app_call_message = self.manager(
            "messenger.app_call_message", event_filter=_msg_of(MessageType.APP_CALL),
        )
        self.deleted_message = self.manager(
            "messenger.deleted_message", event_filter=_msg_of(MessageType.DELETED),
        )
        self.unknown_message = self.manager(
            "messenger.unknown_message", event_filter=_msg_of(MessageType.UNKNOWN),
        )


class OrdersRouter(Router):
    """DBS / CPA order lifecycle. One observer per transition + a coarse status feed."""

    def __init__(self) -> None:
        super().__init__(name="orders")
        self.order_status_changed = self.manager(
            "orders.status_changed", event_filter=_isinst(OrderStatusChanged),
        )
        self.order_created = self.manager("orders.created", event_filter=_isinst(OrderCreated))
        self.order_confirmed = self.manager("orders.confirmed", event_filter=_isinst(OrderConfirmed))
        self.order_shipped = self.manager("orders.shipped", event_filter=_isinst(OrderShipped))
        self.order_delivered = self.manager("orders.delivered", event_filter=_isinst(OrderDelivered))
        self.order_completed = self.manager("orders.completed", event_filter=_isinst(OrderCompleted))
        self.order_cancelled = self.manager("orders.cancelled", event_filter=_isinst(OrderCancelled))
        self.order_refunded = self.manager("orders.refunded", event_filter=_isinst(OrderRefunded))


class DeliveryRouter(Router):
    """Parcel tracking surface — carrier-status driven."""

    def __init__(self) -> None:
        super().__init__(name="delivery")
        self.parcel_status_changed = self.manager(
            "delivery.parcel_status_changed", event_filter=_isinst(ParcelStatusChanged),
        )
        self.parcel_handed_over = self.manager(
            "delivery.parcel_handed_over", event_filter=_isinst(ParcelHandedOver),
        )
        self.parcel_delivered = self.manager(
            "delivery.parcel_delivered", event_filter=_isinst(ParcelDelivered),
        )
        self.parcel_returned = self.manager(
            "delivery.parcel_returned", event_filter=_isinst(ParcelReturned),
        )
        self.announcement_tracked = self.manager(
            "delivery.announcement_tracked", event_filter=_isinst(AnnouncementTracked),
        )


class ReviewsRouter(Router):
    """Customer review surface."""

    def __init__(self) -> None:
        super().__init__(name="reviews")
        self.review_received = self.manager("reviews.received", event_filter=_isinst(ReviewReceived))
        self.review_answered = self.manager("reviews.answered", event_filter=_isinst(ReviewAnswered))


class AutoloadRouter(Router):
    """XML feed autoload pipeline events."""

    def __init__(self) -> None:
        super().__init__(name="autoload")
        self.report_ready = self.manager("autoload.report_ready", event_filter=_isinst(AutoloadReportReady))
        self.failed = self.manager("autoload.failed", event_filter=_isinst(AutoloadFailed))


class CalltrackingRouter(Router):
    """Calltracking call records (received / ended / recording-ready)."""

    def __init__(self) -> None:
        super().__init__(name="calltracking")
        self.call_received = self.manager("calltracking.received", event_filter=_isinst(CallReceived))
        self.call_ended = self.manager("calltracking.ended", event_filter=_isinst(CallEnded))
        self.recording_ready = self.manager(
            "calltracking.recording_ready", event_filter=_isinst(CallRecordingReady),
        )


class BalanceRouter(Router):
    """Balance / operations / bonus surface."""

    def __init__(self) -> None:
        super().__init__(name="balance")
        self.balance_changed = self.manager("balance.changed", event_filter=_isinst(BalanceChanged))
        self.balance_topped_up = self.manager("balance.topped_up", event_filter=_isinst(BalanceToppedUp))
        self.balance_low = self.manager("balance.low", event_filter=_isinst(BalanceLow))
        self.bonus_received = self.manager("balance.bonus_received", event_filter=_isinst(BonusReceived))


class ItemsRouter(Router):
    """Item-listing lifecycle (published / blocked / sold / ...)."""

    def __init__(self) -> None:
        super().__init__(name="items")
        self.item_status_changed = self.manager(
            "items.status_changed", event_filter=_isinst(ItemStatusChanged),
        )
        self.item_published = self.manager("items.published", event_filter=_isinst(ItemPublished))
        self.item_blocked = self.manager("items.blocked", event_filter=_isinst(ItemBlocked))
        self.item_unblocked = self.manager("items.unblocked", event_filter=_isinst(ItemUnblocked))
        self.item_sold = self.manager("items.sold", event_filter=_isinst(ItemSold))
        self.item_archived = self.manager("items.archived", event_filter=_isinst(ItemArchived))


class LifecycleRouter(Router):
    """SDK-internal lifecycle (Dispatcher startup, OAuth, poller failures)."""

    def __init__(self) -> None:
        super().__init__(name="lifecycle")
        self.startup = self.manager("lifecycle.startup", event_filter=_isinst(Startup))
        self.shutdown = self.manager("lifecycle.shutdown", event_filter=_isinst(Shutdown))
        self.token_refreshed = self.manager(
            "lifecycle.token_refreshed", event_filter=_isinst(TokenRefreshed),
        )
        self.auth_failed = self.manager("lifecycle.auth_failed", event_filter=_isinst(AuthFailed))
        self.webhook_error = self.manager("lifecycle.webhook_error", event_filter=_isinst(WebhookError))
        self.poll_error = self.manager("lifecycle.poll_error", event_filter=_isinst(PollError))


__all__ = [
    "AutoloadRouter",
    "BalanceRouter",
    "CalltrackingRouter",
    "DeliveryRouter",
    "EventObserver",
    "ItemsRouter",
    "LifecycleRouter",
    "MessengerRouter",
    "OrdersRouter",
    "ReviewsRouter",
    "Router",
]

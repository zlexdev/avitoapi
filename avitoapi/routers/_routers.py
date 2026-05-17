"""Single aiogram-style ``Router`` — every domain's observers as attributes.

Mirrors the aiogram convention: one ``Router`` class, one instance per
logical scope (the bot / a sub-feature / a plugin), every event the SDK
emits exposed as one named ``EventObserver`` attribute. Sub-routers
compose via ``parent.include_router(child)`` (inherited from
:class:`evented.Router`).

    from avitoapi import Router, F
    router = Router()

    @router.new_message(F.message.type == "text")
    async def handle_text(event, ctx): ...

    @router.order_created()
    async def handle_order(event, ctx): ...

The same observer surface is also reachable directly on
:class:`avitoapi.Dispatcher` — the dispatcher multiply-inherits from
``Router`` so app-level handlers can attach without a separate routing
layer.

Observers are *named managers* under the router, pre-filtered on the
event class (and, for messenger sub-types, on the message's
``MessageType``). Filter evaluation is done by ``evented`` itself when
``dispatcher.event_entry(event)`` fans the event out.

Requires ``evented`` (private dep at ``github.com/zlexdev/evented``); install
via ``pip install 'git+https://${GH_TOKEN}@github.com/zlexdev/evented.git'``.
"""
from __future__ import annotations

from typing import Any

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

EventObserver = evented.EventObserver  # alias of evented.HandlerManager


def _isinst(cls: type) -> Any:
    """Build an ``event_filter`` callable that matches ``isinstance(event, cls)``."""

    return lambda ev: isinstance(ev, cls)


def _msg_of(kind: Any) -> Any:
    """``NewMessage`` filter narrowing to one ``MessageType`` variant."""

    return lambda ev: isinstance(ev, NewMessage) and getattr(ev.message, "type", None) == kind


def install_observers(router_like: Any) -> None:  # noqa: PLR0915 — flat by design
    """Attach every SDK observer as a named manager on ``router_like``.

    ``router_like`` must be any ``evented.Router`` subclass — this includes
    both :class:`Router` and :class:`avitoapi.Dispatcher` (which inherits
    from ``Router``). Splitting this out as a free function keeps both
    inheritance paths sharing one source of truth.

    Kept as one flat function on purpose: the observer wiring is a single
    declarative manifest, splitting it into per-domain helpers would hide
    the surface behind indirection without buying clarity.
    """

    from ..models.messenger import MessageType  # noqa: PLC0415 — lazy to avoid cycle

    r = router_like
    r.new_message = r.manager("messenger.new_message", event_filter=_isinst(NewMessage))
    r.text_message = r.manager("messenger.text_message", event_filter=_msg_of(MessageType.TEXT))
    r.image_message = r.manager("messenger.image_message", event_filter=_msg_of(MessageType.IMAGE))
    r.link_message = r.manager("messenger.link_message", event_filter=_msg_of(MessageType.LINK))
    r.item_message = r.manager("messenger.item_message", event_filter=_msg_of(MessageType.ITEM))
    r.location_message = r.manager(
        "messenger.location_message", event_filter=_msg_of(MessageType.LOCATION),
    )
    r.voice_message = r.manager("messenger.voice_message", event_filter=_msg_of(MessageType.VOICE))
    r.call_message = r.manager("messenger.call_message", event_filter=_msg_of(MessageType.CALL))
    r.file_message = r.manager("messenger.file_message", event_filter=_msg_of(MessageType.FILE))
    r.system_message = r.manager("messenger.system_message", event_filter=_msg_of(MessageType.SYSTEM))
    r.app_call_message = r.manager(
        "messenger.app_call_message", event_filter=_msg_of(MessageType.APP_CALL),
    )
    r.deleted_message = r.manager(
        "messenger.deleted_message", event_filter=_msg_of(MessageType.DELETED),
    )
    r.unknown_message = r.manager(
        "messenger.unknown_message", event_filter=_msg_of(MessageType.UNKNOWN),
    )
    r.message_read = r.manager("messenger.message_read", event_filter=_isinst(MessageRead))
    r.chat_archived = r.manager("messenger.chat_archived", event_filter=_isinst(ChatArchived))
    r.chat_blacklisted = r.manager(
        "messenger.chat_blacklisted", event_filter=_isinst(ChatBlacklisted),
    )
    r.voice_file_resolved = r.manager(
        "messenger.voice_file_resolved", event_filter=_isinst(VoiceFileResolved),
    )

    r.order_status_changed = r.manager(
        "orders.status_changed", event_filter=_isinst(OrderStatusChanged),
    )
    r.order_created = r.manager("orders.created", event_filter=_isinst(OrderCreated))
    r.order_confirmed = r.manager("orders.confirmed", event_filter=_isinst(OrderConfirmed))
    r.order_shipped = r.manager("orders.shipped", event_filter=_isinst(OrderShipped))
    r.order_delivered = r.manager("orders.delivered", event_filter=_isinst(OrderDelivered))
    r.order_completed = r.manager("orders.completed", event_filter=_isinst(OrderCompleted))
    r.order_cancelled = r.manager("orders.cancelled", event_filter=_isinst(OrderCancelled))
    r.order_refunded = r.manager("orders.refunded", event_filter=_isinst(OrderRefunded))

    r.parcel_status_changed = r.manager(
        "delivery.parcel_status_changed", event_filter=_isinst(ParcelStatusChanged),
    )
    r.parcel_handed_over = r.manager(
        "delivery.parcel_handed_over", event_filter=_isinst(ParcelHandedOver),
    )
    r.parcel_delivered = r.manager(
        "delivery.parcel_delivered", event_filter=_isinst(ParcelDelivered),
    )
    r.parcel_returned = r.manager(
        "delivery.parcel_returned", event_filter=_isinst(ParcelReturned),
    )
    r.announcement_tracked = r.manager(
        "delivery.announcement_tracked", event_filter=_isinst(AnnouncementTracked),
    )

    r.review_received = r.manager("reviews.received", event_filter=_isinst(ReviewReceived))
    r.review_answered = r.manager("reviews.answered", event_filter=_isinst(ReviewAnswered))

    r.autoload_report_ready = r.manager(
        "autoload.report_ready", event_filter=_isinst(AutoloadReportReady),
    )
    r.autoload_failed = r.manager("autoload.failed", event_filter=_isinst(AutoloadFailed))

    r.call_received = r.manager("calltracking.received", event_filter=_isinst(CallReceived))
    r.call_ended = r.manager("calltracking.ended", event_filter=_isinst(CallEnded))
    r.call_recording_ready = r.manager(
        "calltracking.recording_ready", event_filter=_isinst(CallRecordingReady),
    )

    r.balance_changed = r.manager("balance.changed", event_filter=_isinst(BalanceChanged))
    r.balance_topped_up = r.manager("balance.topped_up", event_filter=_isinst(BalanceToppedUp))
    r.balance_low = r.manager("balance.low", event_filter=_isinst(BalanceLow))
    r.bonus_received = r.manager("balance.bonus_received", event_filter=_isinst(BonusReceived))

    r.item_status_changed = r.manager(
        "items.status_changed", event_filter=_isinst(ItemStatusChanged),
    )
    r.item_published = r.manager("items.published", event_filter=_isinst(ItemPublished))
    r.item_blocked = r.manager("items.blocked", event_filter=_isinst(ItemBlocked))
    r.item_unblocked = r.manager("items.unblocked", event_filter=_isinst(ItemUnblocked))
    r.item_sold = r.manager("items.sold", event_filter=_isinst(ItemSold))
    r.item_archived = r.manager("items.archived", event_filter=_isinst(ItemArchived))

    # Lifecycle observers carry an ``on_`` prefix to avoid colliding with
    # ``evented.Dispatcher.shutdown()`` (an async method on the dispatcher).
    r.on_startup = r.manager("lifecycle.startup", event_filter=_isinst(Startup))
    r.on_shutdown = r.manager("lifecycle.shutdown", event_filter=_isinst(Shutdown))
    r.on_token_refreshed = r.manager(
        "lifecycle.token_refreshed", event_filter=_isinst(TokenRefreshed),
    )
    r.on_auth_failed = r.manager("lifecycle.auth_failed", event_filter=_isinst(AuthFailed))
    r.on_webhook_error = r.manager("lifecycle.webhook_error", event_filter=_isinst(WebhookError))
    r.on_poll_error = r.manager("lifecycle.poll_error", event_filter=_isinst(PollError))


class Router(evented.Router):
    """SDK-wide aiogram-style Router exposing every event as a named observer.

    One instance per scope. Compose hierarchies with :meth:`include_router`
    inherited from the base evented Router for plugin / sub-feature
    isolation. :class:`avitoapi.Dispatcher` is itself a ``Router``, so
    handlers can attach to the dispatcher directly when you don't need a
    separate routing layer.
    """

    new_message: EventObserver
    text_message: EventObserver
    image_message: EventObserver
    link_message: EventObserver
    item_message: EventObserver
    location_message: EventObserver
    voice_message: EventObserver
    call_message: EventObserver
    file_message: EventObserver
    system_message: EventObserver
    app_call_message: EventObserver
    deleted_message: EventObserver
    unknown_message: EventObserver
    message_read: EventObserver
    chat_archived: EventObserver
    chat_blacklisted: EventObserver
    voice_file_resolved: EventObserver

    order_status_changed: EventObserver
    order_created: EventObserver
    order_confirmed: EventObserver
    order_shipped: EventObserver
    order_delivered: EventObserver
    order_completed: EventObserver
    order_cancelled: EventObserver
    order_refunded: EventObserver

    parcel_status_changed: EventObserver
    parcel_handed_over: EventObserver
    parcel_delivered: EventObserver
    parcel_returned: EventObserver
    announcement_tracked: EventObserver

    review_received: EventObserver
    review_answered: EventObserver

    autoload_report_ready: EventObserver
    autoload_failed: EventObserver

    call_received: EventObserver
    call_ended: EventObserver
    call_recording_ready: EventObserver

    balance_changed: EventObserver
    balance_topped_up: EventObserver
    balance_low: EventObserver
    bonus_received: EventObserver

    item_status_changed: EventObserver
    item_published: EventObserver
    item_blocked: EventObserver
    item_unblocked: EventObserver
    item_sold: EventObserver
    item_archived: EventObserver

    on_startup: EventObserver
    on_shutdown: EventObserver
    on_token_refreshed: EventObserver
    on_auth_failed: EventObserver
    on_webhook_error: EventObserver
    on_poll_error: EventObserver

    def __init__(self, name: str = "avito") -> None:
        super().__init__(name=name)
        install_observers(self)


__all__ = ["EventObserver", "Router", "install_observers"]

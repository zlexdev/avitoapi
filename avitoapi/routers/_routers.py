"""Single aiogram-style ``Router`` — every domain's observers as attributes.

Mirrors the aiogram convention: one ``Router`` class, one instance per
logical scope (the bot / a sub-feature / a plugin), every event the SDK
emits exposed as one named :class:`EventObserver` attribute. Sub-routers
compose via ``parent.include_router(child)``.

    from avitoapi import Router, F
    router = Router()

    @router.new_message(F.message.type == "text")
    async def handle_text(event, ctx): ...

    @router.order_created()
    async def handle_order(event, ctx): ...

The same observer surface is also reachable directly on
:class:`avitoapi.Dispatcher` — the dispatcher inherits from
:class:`Router` so app-level handlers can attach without a separate routing
layer.

Observers are *named managers* under the router, pre-filtered on the
event class (and, for messenger sub-types, on the message's
:class:`MessageType`). Filter evaluation happens inside :meth:`Router.propagate`.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

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
from ..logging import get_logger
from .context import EventContext
from .middleware import MiddlewareChain
from .observer import EventObserver, Filter, Handler, HandlerManager

log = get_logger(__name__)


def _isinst(cls: type) -> Filter:
    """Build an ``event_filter`` callable that matches ``isinstance(event, cls)``."""

    return lambda ev: isinstance(ev, cls)


def _msg_of(kind: Any) -> Filter:
    """``NewMessage`` filter narrowing to one :class:`MessageType` variant."""

    return lambda ev: isinstance(ev, NewMessage) and getattr(ev.message, "type", None) == kind


def install_observers(router_like: Router) -> None:  # noqa: PLR0915 — flat by design
    """Attach every SDK observer as a named manager on ``router_like``.

    Kept as one flat function on purpose: the observer wiring is a single
    declarative manifest, splitting it into per-domain helpers would hide
    the surface behind indirection without buying clarity.
    """

    from ..models.messenger import MessageType  # noqa: PLC0415 — lazy to avoid cycle

    r = router_like
    r.new_message = r._manager("messenger.new_message", _isinst(NewMessage))
    r.text_message = r._manager("messenger.text_message", _msg_of(MessageType.TEXT))
    r.image_message = r._manager("messenger.image_message", _msg_of(MessageType.IMAGE))
    r.link_message = r._manager("messenger.link_message", _msg_of(MessageType.LINK))
    r.item_message = r._manager("messenger.item_message", _msg_of(MessageType.ITEM))
    r.location_message = r._manager("messenger.location_message", _msg_of(MessageType.LOCATION))
    r.voice_message = r._manager("messenger.voice_message", _msg_of(MessageType.VOICE))
    r.call_message = r._manager("messenger.call_message", _msg_of(MessageType.CALL))
    r.file_message = r._manager("messenger.file_message", _msg_of(MessageType.FILE))
    r.system_message = r._manager("messenger.system_message", _msg_of(MessageType.SYSTEM))
    r.app_call_message = r._manager("messenger.app_call_message", _msg_of(MessageType.APP_CALL))
    r.deleted_message = r._manager("messenger.deleted_message", _msg_of(MessageType.DELETED))
    r.unknown_message = r._manager("messenger.unknown_message", _msg_of(MessageType.UNKNOWN))
    r.message_read = r._manager("messenger.message_read", _isinst(MessageRead))
    r.chat_archived = r._manager("messenger.chat_archived", _isinst(ChatArchived))
    r.chat_blacklisted = r._manager("messenger.chat_blacklisted", _isinst(ChatBlacklisted))
    r.voice_file_resolved = r._manager(
        "messenger.voice_file_resolved",
        _isinst(VoiceFileResolved),
    )

    r.order_status_changed = r._manager("orders.status_changed", _isinst(OrderStatusChanged))
    r.order_created = r._manager("orders.created", _isinst(OrderCreated))
    r.order_confirmed = r._manager("orders.confirmed", _isinst(OrderConfirmed))
    r.order_shipped = r._manager("orders.shipped", _isinst(OrderShipped))
    r.order_delivered = r._manager("orders.delivered", _isinst(OrderDelivered))
    r.order_completed = r._manager("orders.completed", _isinst(OrderCompleted))
    r.order_cancelled = r._manager("orders.cancelled", _isinst(OrderCancelled))
    r.order_refunded = r._manager("orders.refunded", _isinst(OrderRefunded))

    r.parcel_status_changed = r._manager(
        "delivery.parcel_status_changed",
        _isinst(ParcelStatusChanged),
    )
    r.parcel_handed_over = r._manager(
        "delivery.parcel_handed_over",
        _isinst(ParcelHandedOver),
    )
    r.parcel_delivered = r._manager("delivery.parcel_delivered", _isinst(ParcelDelivered))
    r.parcel_returned = r._manager("delivery.parcel_returned", _isinst(ParcelReturned))
    r.announcement_tracked = r._manager(
        "delivery.announcement_tracked",
        _isinst(AnnouncementTracked),
    )

    r.review_received = r._manager("reviews.received", _isinst(ReviewReceived))
    r.review_answered = r._manager("reviews.answered", _isinst(ReviewAnswered))

    r.autoload_report_ready = r._manager(
        "autoload.report_ready",
        _isinst(AutoloadReportReady),
    )
    r.autoload_failed = r._manager("autoload.failed", _isinst(AutoloadFailed))

    r.call_received = r._manager("calltracking.received", _isinst(CallReceived))
    r.call_ended = r._manager("calltracking.ended", _isinst(CallEnded))
    r.call_recording_ready = r._manager(
        "calltracking.recording_ready",
        _isinst(CallRecordingReady),
    )

    r.balance_changed = r._manager("balance.changed", _isinst(BalanceChanged))
    r.balance_topped_up = r._manager("balance.topped_up", _isinst(BalanceToppedUp))
    r.balance_low = r._manager("balance.low", _isinst(BalanceLow))
    r.bonus_received = r._manager("balance.bonus_received", _isinst(BonusReceived))

    r.item_status_changed = r._manager("items.status_changed", _isinst(ItemStatusChanged))
    r.item_published = r._manager("items.published", _isinst(ItemPublished))
    r.item_blocked = r._manager("items.blocked", _isinst(ItemBlocked))
    r.item_unblocked = r._manager("items.unblocked", _isinst(ItemUnblocked))
    r.item_sold = r._manager("items.sold", _isinst(ItemSold))
    r.item_archived = r._manager("items.archived", _isinst(ItemArchived))

    r.on_startup = r._manager("lifecycle.startup", _isinst(Startup))
    r.on_shutdown = r._manager("lifecycle.shutdown", _isinst(Shutdown))
    r.on_token_refreshed = r._manager("lifecycle.token_refreshed", _isinst(TokenRefreshed))
    r.on_auth_failed = r._manager("lifecycle.auth_failed", _isinst(AuthFailed))
    r.on_webhook_error = r._manager("lifecycle.webhook_error", _isinst(WebhookError))
    r.on_poll_error = r._manager("lifecycle.poll_error", _isinst(PollError))


class Router:
    """Aiogram-style router with named observers, sub-router composition, and middlewares.

    One instance per scope. Compose hierarchies with :meth:`include_router` for
    plugin / sub-feature isolation. :class:`avitoapi.Dispatcher` is itself a
    :class:`Router`, so handlers can attach to the dispatcher directly when
    you don't need a separate routing layer.
    """

    # Observer attributes (populated by ``install_observers``). Declared as
    # class-level type hints so IDEs offer completion before construction runs.
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
        self.name = name
        self.parent: Router | None = None
        self.sub_routers: list[Router] = []
        self._managers: dict[str, HandlerManager] = {}
        self.outer_middleware = MiddlewareChain()
        self.inner_middleware = MiddlewareChain()
        install_observers(self)

    # ---- composition -------------------------------------------------------

    def include_router(self, router: Router) -> Router:
        """Attach a sub-router; events propagate to children after the parent's own handlers."""

        if router.parent is not None:
            raise RuntimeError(
                f"Router {router.name!r} already has parent {router.parent.name!r}",
            )
        router.parent = self
        self.sub_routers.append(router)
        return router

    def include_routers(self, *routers: Router) -> None:
        for r in routers:
            self.include_router(r)

    def iter_routers(self) -> Iterable[Router]:
        """Depth-first walk: self → every descendant."""

        yield self
        for child in self.sub_routers:
            yield from child.iter_routers()

    # ---- handler API ------------------------------------------------------

    def _manager(self, name: str, event_filter: Filter | None) -> HandlerManager:
        manager = HandlerManager(name=name, event_filter=event_filter)
        self._managers[name] = manager
        return manager

    def manager(self, name: str, *, event_filter: Filter | None = None) -> HandlerManager:
        """Public alias — create / fetch a manager by route name."""

        existing = self._managers.get(name)
        if existing is not None:
            return existing
        return self._manager(name, event_filter)

    def on(self, name: str, *filters: Filter) -> Callable[[Handler], Handler]:
        """Imperative shortcut: ``@router.on("orders.created")``."""

        return self.manager(name)(*filters)

    # ---- propagation ------------------------------------------------------

    async def propagate(self, event: Any, ctx: EventContext) -> bool:
        """Walk every manager (self → children); return ``True`` if any handler fired."""

        async def _run(_event: Any, _ctx: EventContext) -> bool:
            fired = False
            for manager in self._managers.values():
                if not manager.applies(_event):
                    continue
                inner = self.inner_middleware.wrap(self._call_one(manager))
                if await inner(_event, _ctx):
                    fired = True
            for child in self.sub_routers:
                if await child.propagate(_event, _ctx):
                    fired = True
            return fired

        wrapped = self.outer_middleware.wrap(_run)  # type: ignore[arg-type]
        result = await wrapped(event, ctx)
        if result:
            ctx.handled = True
        return bool(result)

    @staticmethod
    def _call_one(manager: HandlerManager):  # noqa: ANN205 — closure helper
        async def _terminal(event: Any, ctx: EventContext) -> bool:
            return await manager.trigger(event, ctx)

        return _terminal


__all__ = ["EventObserver", "Router", "install_observers"]

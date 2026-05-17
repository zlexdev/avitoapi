"""Typed Avito events flowing through the Dispatcher."""

from __future__ import annotations

from .autoload import AutoloadEvent, AutoloadFailed, AutoloadReportReady
from .balance import (
    BalanceChanged,
    BalanceEvent,
    BalanceLow,
    BalanceToppedUp,
    BonusReceived,
)
from .calltracking import (
    CallEnded,
    CallReceived,
    CallRecordingReady,
    CalltrackingEvent,
)
from .delivery import (
    AnnouncementTracked,
    DeliveryEvent,
    ParcelDelivered,
    ParcelHandedOver,
    ParcelReturned,
    ParcelStatusChanged,
)
from .items import (
    ItemArchived,
    ItemBlocked,
    ItemEvent,
    ItemPublished,
    ItemSold,
    ItemStatusChanged,
    ItemUnblocked,
)
from .lifecycle import (
    AuthFailed,
    LifecycleEvent,
    PollError,
    Shutdown,
    Startup,
    TokenRefreshed,
    WebhookError,
)
from .messenger import (
    BaseEvent,
    ChatArchived,
    ChatBlacklisted,
    MessageRead,
    MessengerEvent,
    NewMessage,
    VoiceFileResolved,
)
from .orders import (
    OrderCancelled,
    OrderCompleted,
    OrderConfirmed,
    OrderCreated,
    OrderDelivered,
    OrderEvent,
    OrderRefunded,
    OrderShipped,
    OrderStatusChanged,
)
from .reviews import ReviewAnswered, ReviewEvent, ReviewReceived

__all__ = [
    "AnnouncementTracked",
    "AuthFailed",
    "AutoloadEvent",
    "AutoloadFailed",
    "AutoloadReportReady",
    "BalanceChanged",
    "BalanceEvent",
    "BalanceLow",
    "BalanceToppedUp",
    "BaseEvent",
    "BonusReceived",
    "CallEnded",
    "CallReceived",
    "CallRecordingReady",
    "CalltrackingEvent",
    "ChatArchived",
    "ChatBlacklisted",
    "DeliveryEvent",
    "ItemArchived",
    "ItemBlocked",
    "ItemEvent",
    "ItemPublished",
    "ItemSold",
    "ItemStatusChanged",
    "ItemUnblocked",
    "LifecycleEvent",
    "MessageRead",
    "MessengerEvent",
    "NewMessage",
    "OrderCancelled",
    "OrderCompleted",
    "OrderConfirmed",
    "OrderCreated",
    "OrderDelivered",
    "OrderEvent",
    "OrderRefunded",
    "OrderShipped",
    "OrderStatusChanged",
    "ParcelDelivered",
    "ParcelHandedOver",
    "ParcelReturned",
    "ParcelStatusChanged",
    "PollError",
    "ReviewAnswered",
    "ReviewEvent",
    "ReviewReceived",
    "Shutdown",
    "Startup",
    "TokenRefreshed",
    "VoiceFileResolved",
    "WebhookError",
]

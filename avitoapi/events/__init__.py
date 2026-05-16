"""Typed Avito events flowing through the Dispatcher."""
from __future__ import annotations

from .delivery import AnnouncementTracked, DeliveryEvent, ParcelStatusChanged
from .messenger import (
    BaseEvent,
    ChatArchived,
    MessageRead,
    MessengerEvent,
    NewMessage,
)
from .orders import OrderEvent, OrderRefunded, OrderStatusChanged

__all__ = [
    "AnnouncementTracked",
    "BaseEvent",
    "ChatArchived",
    "DeliveryEvent",
    "MessageRead",
    "MessengerEvent",
    "NewMessage",
    "OrderEvent",
    "OrderRefunded",
    "OrderStatusChanged",
    "ParcelStatusChanged",
]

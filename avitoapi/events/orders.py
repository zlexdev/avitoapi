"""Order-domain events — emitted by SDK pollers around DBS/CPA order lifecycle.

Avito has no native order webhook surface — these events are synthesised by
a polling loop that diffs ``GET /order-management/v1/orders`` snapshots.
Each transition (`NEW -> CONFIRMED`, `SHIPPED -> DELIVERED`, ...) is emitted
as both a coarse :class:`OrderStatusChanged` *and* a phase-specific event
(:class:`OrderShipped`, :class:`OrderDelivered`, ...) so handlers can either
subscribe to the lifecycle or a single transition.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from .messenger import BaseEvent


class OrderStatus(StrEnum):
    """DBS order lifecycle status.

    Minimal local enum: ``models/orders.py`` (the old DBS Order model) was
    dropped as a codegen orphan, and the generated ``enums.order_management.Status``
    uses an unrelated vocabulary (``ready_to_ship``/``in_transit``/...) for a
    different order surface — it shares no values with the 7 states this
    module's phase-specific events (:class:`OrderShipped`, :class:`OrderCompleted`, ...)
    are keyed on.
    """

    NEW = "new"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    UNKNOWN = "unknown"  # unmapped upstream status — never silently coerced to a real state


class OrderEvent(BaseEvent, event_name="orders"):
    """Common ancestor of every order-domain event."""

    account_id: str
    order_id: str


class OrderStatusChanged(OrderEvent, event_name="orders.status_changed"):
    """An order moved between two lifecycle states."""

    previous: OrderStatus
    current: OrderStatus
    occurred_at: datetime


class OrderCreated(OrderEvent, event_name="orders.created"):
    """A new order was created on the seller's account."""

    created_at: datetime


class OrderConfirmed(OrderEvent, event_name="orders.confirmed"):
    """The seller (or Avito on auto-rules) confirmed the order."""

    confirmed_at: datetime


class OrderShipped(OrderEvent, event_name="orders.shipped"):
    """A track number was attached and the order entered shipping."""

    shipped_at: datetime
    track_number: str | None = None


class OrderDelivered(OrderEvent, event_name="orders.delivered"):
    """The carrier reported successful delivery."""

    delivered_at: datetime


class OrderCompleted(OrderEvent, event_name="orders.completed"):
    """The buyer accepted the order — terminal happy-path state."""

    completed_at: datetime


class OrderCancelled(OrderEvent, event_name="orders.cancelled"):
    """The order was cancelled before delivery."""

    cancelled_at: datetime
    reason: str | None = None


class OrderRefunded(OrderEvent, event_name="orders.refunded"):
    """An order entered the refunded terminal state."""

    refunded_at: datetime
    reason: str | None = None


__all__ = [
    "OrderCancelled",
    "OrderCompleted",
    "OrderConfirmed",
    "OrderCreated",
    "OrderDelivered",
    "OrderEvent",
    "OrderRefunded",
    "OrderShipped",
    "OrderStatusChanged",
]

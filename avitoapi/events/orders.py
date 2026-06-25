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
from typing import TYPE_CHECKING

from .messenger import BaseEvent

if TYPE_CHECKING:
    from ..models.orders import OrderStatus


class OrderEvent(BaseEvent, event_name="orders"):
    """Common ancestor of every order-domain event."""

    account_id: str
    order_id: str

    def __init__(self, *, account_id: str, order_id: str, **kwargs: object) -> None:
        super().__init__()
        self.account_id = account_id
        self.order_id = order_id
        for k, v in kwargs.items():
            setattr(self, k, v)


class OrderStatusChanged(OrderEvent, event_name="orders.status_changed"):
    """An order moved between two lifecycle states."""

    previous: OrderStatus
    current: OrderStatus
    occurred_at: datetime

    def __init__(
        self,
        *,
        account_id: str,
        order_id: str,
        previous: OrderStatus,
        current: OrderStatus,
        occurred_at: datetime,
    ) -> None:
        super().__init__(account_id=account_id, order_id=order_id)
        self.previous = previous
        self.current = current
        self.occurred_at = occurred_at


class OrderCreated(OrderEvent, event_name="orders.created"):
    """A new order was created on the seller's account."""

    created_at: datetime

    def __init__(self, *, account_id: str, order_id: str, created_at: datetime) -> None:
        super().__init__(account_id=account_id, order_id=order_id)
        self.created_at = created_at


class OrderConfirmed(OrderEvent, event_name="orders.confirmed"):
    """The seller (or Avito on auto-rules) confirmed the order."""

    confirmed_at: datetime

    def __init__(self, *, account_id: str, order_id: str, confirmed_at: datetime) -> None:
        super().__init__(account_id=account_id, order_id=order_id)
        self.confirmed_at = confirmed_at


class OrderShipped(OrderEvent, event_name="orders.shipped"):
    """A track number was attached and the order entered shipping."""

    track_number: str | None
    shipped_at: datetime

    def __init__(
        self,
        *,
        account_id: str,
        order_id: str,
        shipped_at: datetime,
        track_number: str | None = None,
    ) -> None:
        super().__init__(account_id=account_id, order_id=order_id)
        self.shipped_at = shipped_at
        self.track_number = track_number


class OrderDelivered(OrderEvent, event_name="orders.delivered"):
    """The carrier reported successful delivery."""

    delivered_at: datetime

    def __init__(self, *, account_id: str, order_id: str, delivered_at: datetime) -> None:
        super().__init__(account_id=account_id, order_id=order_id)
        self.delivered_at = delivered_at


class OrderCompleted(OrderEvent, event_name="orders.completed"):
    """The buyer accepted the order — terminal happy-path state."""

    completed_at: datetime

    def __init__(self, *, account_id: str, order_id: str, completed_at: datetime) -> None:
        super().__init__(account_id=account_id, order_id=order_id)
        self.completed_at = completed_at


class OrderCancelled(OrderEvent, event_name="orders.cancelled"):
    """The order was cancelled before delivery."""

    cancelled_at: datetime
    reason: str | None

    def __init__(
        self,
        *,
        account_id: str,
        order_id: str,
        cancelled_at: datetime,
        reason: str | None = None,
    ) -> None:
        super().__init__(account_id=account_id, order_id=order_id)
        self.cancelled_at = cancelled_at
        self.reason = reason


class OrderRefunded(OrderEvent, event_name="orders.refunded"):
    """An order entered the refunded terminal state."""

    reason: str | None
    refunded_at: datetime

    def __init__(
        self,
        *,
        account_id: str,
        order_id: str,
        refunded_at: datetime,
        reason: str | None = None,
    ) -> None:
        super().__init__(account_id=account_id, order_id=order_id)
        self.reason = reason
        self.refunded_at = refunded_at


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

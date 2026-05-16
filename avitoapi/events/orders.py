"""Order-domain events — emitted by pollers around DBS/CPA order lifecycle."""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from .messenger import BaseEvent

if TYPE_CHECKING:
    from ..models.orders import OrderStatus


class OrderEvent(BaseEvent, event_name="orders"):  # type: ignore[call-arg,misc]
    """Common ancestor of every order-domain event."""

    account_id: str
    order_id: str

    def __init__(self, *, account_id: str, order_id: str, **kwargs: Any) -> None:
        self.account_id = account_id
        self.order_id = order_id
        for k, v in kwargs.items():
            setattr(self, k, v)


class OrderStatusChanged(OrderEvent, event_name="orders.status_changed"):  # type: ignore[call-arg,misc]
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


class OrderRefunded(OrderEvent, event_name="orders.refunded"):  # type: ignore[call-arg,misc]
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
    "OrderEvent",
    "OrderRefunded",
    "OrderStatusChanged",
]

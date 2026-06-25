"""Orders domain — DBS order lifecycle, transition table, bound actions."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from ..exceptions import InvalidStateTransition
from ..logging import get_logger
from ._base import AvitoObject
from .common import Money, TZDatetime

if TYPE_CHECKING:
    from ..methods.orders import (
        ChangeOrderStatus,
        RefundOrder,
        TransferDeliveryTerms,
        TransferTrackNumber,
    )

log = get_logger(__name__)


class OrderStatus(StrEnum):
    """DBS order lifecycle states as documented on developers.avito.ru (snapshot 2026-05)."""

    NEW = "new"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


ORDER_TRANSITIONS: dict[OrderStatus, frozenset[OrderStatus]] = {
    OrderStatus.NEW: frozenset({OrderStatus.CONFIRMED, OrderStatus.CANCELLED}),
    OrderStatus.CONFIRMED: frozenset({OrderStatus.SHIPPED, OrderStatus.CANCELLED}),
    OrderStatus.SHIPPED: frozenset({OrderStatus.DELIVERED, OrderStatus.CANCELLED}),
    OrderStatus.DELIVERED: frozenset({OrderStatus.COMPLETED, OrderStatus.REFUNDED}),
    OrderStatus.COMPLETED: frozenset({OrderStatus.REFUNDED}),
    OrderStatus.CANCELLED: frozenset(),
    OrderStatus.REFUNDED: frozenset(),
}


def assert_order_transition(
    current: OrderStatus,
    target: OrderStatus,
    *,
    strict: bool,
) -> None:
    """Verify ``current -> target`` against :data:`ORDER_TRANSITIONS`.

    Args:
        current: The order's present status.
        target: The status the caller wants to move to.
        strict: When ``True``, raise :class:`InvalidStateTransition` on an
            illegal transition. When ``False``, log a warning and let the
            mutation through — useful when Avito ships a new status before
            the SDK's table is refreshed.
    """

    if current == target:
        return
    allowed = ORDER_TRANSITIONS.get(current, frozenset())
    if target in allowed:
        return
    if strict:
        raise InvalidStateTransition(
            f"Order cannot move {current.value} -> {target.value}; "
            f"allowed from {current.value}: {sorted(s.value for s in allowed)}",
            current=current,
            target=target,
        )
    log.warning(
        "order.transition.unknown",
        current=current.value,
        target=target.value,
        allowed=sorted(s.value for s in allowed),
    )


class DeliveryTerm(BaseModel):
    """Seller-supplied delivery terms attached to an order."""

    model_config = ConfigDict(populate_by_name=True, strict=True, extra="allow")

    term_days: int = Field(..., ge=0, description="Promised delivery window in calendar days.")
    note: str | None = Field(default=None, description="Optional free-form note for the buyer.")


class TrackInfo(BaseModel):
    """Carrier + tracking code returned by the order details endpoint."""

    model_config = ConfigDict(populate_by_name=True, strict=True, extra="allow")

    carrier: str = Field(
        ..., min_length=1, description="Carrier slug (Avito Доставка, CDEK, Pochta…)."
    )
    code: str = Field(..., min_length=1, description="Carrier tracking code.")
    updated_at: TZDatetime | None = Field(
        default=None,
        description="Last time the carrier reported a status update (UTC).",
    )


class Order(AvitoObject):
    """DBS order DTO returned by ``GET /orders/list`` and per-order endpoints.

    Forward-compatible: extra fields land via ``ConfigDict(extra="allow")``
    so DBS / self-pickup / Avito-Доставка quirks don't break callers.

    Bound methods are not ``async def``: they return an awaitable method-class
    with the client pre-attached, mirroring the items domain pattern.
    """

    model_config = ConfigDict(populate_by_name=True, strict=True, extra="allow")

    id: str = Field(..., description="Avito order id (string — Avito uses opaque ids on DBS).")
    status: OrderStatus = Field(..., description="Current lifecycle status.")
    item_id: int | None = Field(default=None, description="Item the order was placed against.")
    buyer_id: int | None = Field(default=None, description="Buyer's Avito user id, when surfaced.")
    seller_id: int | None = Field(
        default=None, description="Seller's Avito user id, when surfaced."
    )
    total: Money | None = Field(
        default=None, description="Order total; absent on some DBS responses."
    )
    delivery: DeliveryTerm | None = Field(
        default=None, description="Seller-supplied delivery terms."
    )
    track: TrackInfo | None = Field(
        default=None, description="Carrier tracking info, when shipped."
    )
    created_at: TZDatetime | None = Field(default=None, description="Creation timestamp (UTC).")
    updated_at: TZDatetime | None = Field(default=None, description="Last update timestamp (UTC).")

    def change_status(
        self,
        new: OrderStatus,
        *,
        strict: bool = True,
    ) -> ChangeOrderStatus:
        """Build a status-change method-class bound to this order.

        Guards the transition against :data:`ORDER_TRANSITIONS` before
        constructing the wire call so an illegal jump fails fast client-side.

        Args:
            new: Target status.
            strict: When ``True`` (default), raise :class:`InvalidStateTransition`
                on illegal transitions; when ``False`` only log a warning.
        """

        from ..methods.orders import ChangeOrderStatus

        client = self._require_client()
        assert_order_transition(self.status, new, strict=strict)
        return ChangeOrderStatus(order_id=self.id, status=new).as_(client)

    def transfer_delivery_terms(
        self,
        term_days: int,
        note: str | None = None,
    ) -> TransferDeliveryTerms:
        """Build a delivery-terms transfer method-class bound to this order."""

        from ..methods.orders import TransferDeliveryTerms

        client = self._require_client()
        return TransferDeliveryTerms(
            order_id=self.id,
            term_days=term_days,
            note=note,
        ).as_(client)

    def transfer_track_number(
        self,
        carrier: str,
        code: str,
    ) -> TransferTrackNumber:
        """Build a track-number transfer method-class bound to this order."""

        from ..methods.orders import TransferTrackNumber

        client = self._require_client()
        return TransferTrackNumber(
            order_id=self.id,
            carrier=carrier,
            code=code,
        ).as_(client)

    def refund(self, reason: str | None = None) -> RefundOrder:
        """Build a refund method-class bound to this order."""

        from ..methods.orders import RefundOrder

        client = self._require_client()
        return RefundOrder(order_id=self.id, reason=reason).as_(client)


class OrderList(AvitoObject):
    """List envelope for ``GET /orders/list``.

    Avito's DBS docs are uneven across third-party clients on the exact
    shape; the union model here accepts the canonical `{"orders": [...]}`
    payload and tolerates unknown extra keys via ``extra="allow"``.

    Inherits :class:`AvitoObject` so the funnel cascades the client into
    each contained :class:`Order` (so bound actions like ``order.refund()``
    work after a paginated fetch).
    """

    model_config = ConfigDict(populate_by_name=True, strict=True, extra="allow")

    orders: list[Order] = Field(default_factory=list, description="Order rows in the current page.")
    total: int | None = Field(
        default=None, ge=0, description="Server-reported total count, when present."
    )

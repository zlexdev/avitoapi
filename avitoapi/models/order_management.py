"""Order-management domain — DBS order management lifecycle DTOs.

Distinct from :mod:`avitoapi.models.orders` — this is the
``/order-management/1/*`` surface (markings, transitions, courier ranges,
labels). Each :class:`ManagedOrder` exposes bound actions so chains like
``order.apply_transition(...)`` work after a list call.

Schema is fluid: ``ConfigDict(strict=False, extra="allow")`` everywhere so
new fields don't break decoding.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field, RootModel

from ._base import BoundModel

if TYPE_CHECKING:
    from ..methods.order_management import (
        AcceptReturnOrder,
        ApplyOrderTransition,
        DownloadOrderLabels,
        SetOrderTrackingNumber,
    )


_OM_CFG = ConfigDict(populate_by_name=True, strict=False, extra="allow")


class ManagedOrderStatus(StrEnum):
    """Managed-order lifecycle states (parallel to the DBS table)."""

    NEW = "new"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RETURNED = "returned"


class OrderTransition(StrEnum):
    """Transition verbs accepted by ``/order/applyTransition``."""

    CONFIRM = "confirm"
    SHIP = "ship"
    DELIVER = "deliver"
    COMPLETE = "complete"
    CANCEL = "cancel"
    RETURN = "return"


class OrderMarking(BaseModel):
    """One marking (mark code / serial) attached to an order line."""

    model_config = _OM_CFG

    code: str = Field(..., min_length=1, description="Mark code (UIN / DataMatrix payload).")
    item_id: int | None = Field(
        default=None, ge=1, description="Item the marking belongs to, when present."
    )
    quantity: int | None = Field(
        default=None, ge=1, description="Quantity covered by this marking, when present."
    )


class CourierDeliveryRange(BoundModel):
    """Buyer-facing courier delivery window."""

    model_config = _OM_CFG

    date_from: datetime | None = Field(default=None, description="Earliest courier slot (UTC).")
    date_to: datetime | None = Field(default=None, description="Latest courier slot (UTC).")
    comment: str | None = Field(default=None, description="Free-form note shown to the buyer.")


class LabelTaskResult(BoundModel):
    """Async-task envelope returned by label-generation endpoints."""

    model_config = _OM_CFG

    task_id: str | None = Field(
        default=None, alias="taskID", description="Task id for polling / download."
    )
    status: str | None = Field(
        default=None, description="Task status (queued / running / done / failed)."
    )
    order_ids: list[str] = Field(
        default_factory=list, description="Order ids included in the batch."
    )


class ManagedOrder(BoundModel):
    """A managed order row returned by ``GET /order-management/1/orders``.

    Bound methods are not ``async def``: they return an awaitable method-class
    with the client pre-attached, mirroring the items / orders pattern.
    """

    model_config = _OM_CFG

    id: str = Field(..., min_length=1, description="Order id (string — Avito uses opaque ids).")
    status: ManagedOrderStatus | str | None = Field(
        default=None,
        description="Lifecycle status (string fallback when Avito ships a new value).",
    )
    item_id: int | None = Field(default=None, description="Item the order was placed against.")
    buyer_id: int | None = Field(default=None, description="Buyer's Avito user id.")
    seller_id: int | None = Field(default=None, description="Seller's Avito user id.")
    created_at: datetime | None = Field(default=None, description="Creation timestamp (UTC).")
    updated_at: datetime | None = Field(default=None, description="Last update timestamp (UTC).")
    markings: list[OrderMarking] = Field(
        default_factory=list, description="Marking codes attached to the order."
    )

    def accept_return(self) -> AcceptReturnOrder:
        """Build an ``AcceptReturnOrder`` method-class bound to this order."""

        from ..methods.order_management import AcceptReturnOrder

        client = self._require_client()
        return AcceptReturnOrder(order_id=self.id).as_(client)

    def apply_transition(self, target: OrderTransition | str) -> ApplyOrderTransition:
        """Build an ``ApplyOrderTransition`` method-class bound to this order.

        Args:
            target: Either an :class:`OrderTransition` enum or the raw verb
                string when Avito ships a new transition before the SDK
                catches up.
        """

        from ..methods.order_management import ApplyOrderTransition

        client = self._require_client()
        transition = target if isinstance(target, OrderTransition) else OrderTransition(target)
        return ApplyOrderTransition(order_id=self.id, transition=transition).as_(client)

    def set_tracking_number(self, carrier: str, code: str) -> SetOrderTrackingNumber:
        """Build a ``SetOrderTrackingNumber`` method-class bound to this order."""

        from ..methods.order_management import SetOrderTrackingNumber

        client = self._require_client()
        return SetOrderTrackingNumber(order_id=self.id, carrier=carrier, code=code).as_(client)

    def download_labels(self, taskID: str) -> DownloadOrderLabels:  # noqa: N803 — Avito uses ``taskID`` verbatim
        """Build a ``DownloadOrderLabels`` method-class bound to this client.

        The label task is global (not order-scoped), but the call is exposed
        here for fluency after a ``CreateOrderLabels`` round-trip.
        """

        from ..methods.order_management import DownloadOrderLabels

        client = self._require_client()
        return DownloadOrderLabels(taskID=taskID).as_(client)


class ManagedOrderList(BoundModel, RootModel[list[ManagedOrder]]):
    """Root-array envelope for ``GET /order-management/1/orders``.

    Inherits :class:`BoundModel` so the session funnel binds it; the custom
    :meth:`as_` cascades the client into each contained :class:`ManagedOrder`
    so chains like ``orders.root[0].apply_transition(...)`` work after a
    list call.
    """

    root: list[ManagedOrder] = Field(default_factory=list)

    def __iter__(self) -> object:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)

    def as_(self, client: object) -> ManagedOrderList:  # type: ignore[override]
        self._client = client
        for item in self.root:
            item.as_(client)
        return self


class MarkingResult(BoundModel):
    """Result of ``POST /order-management/1/markings``."""

    model_config = _OM_CFG

    ok: bool | None = Field(default=None, description="High-level success flag.")
    accepted: list[str] = Field(
        default_factory=list, description="Mark codes accepted by the server."
    )
    rejected: list[str] = Field(
        default_factory=list, description="Mark codes rejected; inspect ``reasons``."
    )
    reasons: dict[str, str] = Field(
        default_factory=dict, description="Rejection reasons keyed by mark code."
    )


class OrderConfirmationCheck(BoundModel):
    """Result of ``POST /order-management/1/order/checkConfirmationCode``."""

    model_config = _OM_CFG

    ok: bool | None = Field(default=None, description="Whether the confirmation code matched.")
    reason: str | None = Field(default=None, description="Failure reason when ``ok`` is False.")


class CncDetailsResult(BoundModel):
    """Result of ``POST /order-management/1/order/cncSetDetails`` (click-and-collect)."""

    model_config = _OM_CFG

    ok: bool | None = Field(default=None, description="High-level success flag.")
    order_id: str | None = Field(default=None, description="Order touched by the call.")

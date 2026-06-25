"""Order-management domain — DBS order lifecycle (``/order-management/1/*``).

Distinct from :mod:`avitoapi.methods.orders` (the legacy DBS surface) and
from :mod:`avitoapi.methods.cpa` (CPA / messenger).

Every mutating call sets ``__idempotent_mutation__ = True`` so the protocol
auto-injects an ``Idempotency-Key`` header. The label-download endpoint
declares ``__binary_response__ = True`` because the wire returns raw bytes
(PDF / ZIP), not JSON.
"""

from __future__ import annotations

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field

from ..models.order_management import (
    CncDetailsResult,
    CourierDeliveryRange,
    LabelTaskResult,
    ManagedOrderList,
    MarkingResult,
    OrderConfirmationCheck,
    OrderMarking,
    OrderTransition,
)
from ._base import BaseMethod


class _BytesEnvelope(BaseModel):
    """Sentinel returning-type for binary downloads (raw bytes flow back).

    The actual response decoded by :class:`RestProtocol` when
    ``__binary_response__`` is True is ``bytes`` — this class is never
    instantiated but satisfies the import-time check that
    ``__returning__`` is a ``BaseModel`` subclass.
    """

    model_config = ConfigDict(strict=True)


class SetOrderMarkings(BaseMethod[MarkingResult]):
    """Attach markings to an order via ``POST /order-management/1/markings``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/order-management/1/markings"
    __idempotent_mutation__: ClassVar[bool] = True

    order_id: str = Field(..., min_length=1)
    markings: list[OrderMarking] = Field(..., min_length=1)


class AcceptReturnOrder(BaseMethod[CncDetailsResult]):
    """Accept a return via ``POST /order-management/1/order/acceptReturnOrder``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/order-management/1/order/acceptReturnOrder"
    __idempotent_mutation__: ClassVar[bool] = True

    order_id: str = Field(..., min_length=1)
    comment: str | None = Field(default=None, description="Optional seller note.")


class ApplyOrderTransition(BaseMethod[CncDetailsResult]):
    """Apply a lifecycle transition via ``POST /order-management/1/order/applyTransition``.

    Idempotent — the protocol injects an ``Idempotency-Key`` derived from
    the (order_id, transition) pair so a retried call doesn't trigger a
    second state-machine move.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/order-management/1/order/applyTransition"
    __idempotent_mutation__: ClassVar[bool] = True

    order_id: str = Field(..., min_length=1)
    transition: OrderTransition = Field(..., description="Target transition verb.")


class CheckOrderConfirmationCode(BaseMethod[OrderConfirmationCheck]):
    """Validate the buyer's confirmation code via ``POST /order-management/1/order/checkConfirmationCode``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/order-management/1/order/checkConfirmationCode"
    __idempotent_mutation__: ClassVar[bool] = True

    order_id: str = Field(..., min_length=1)
    code: str = Field(..., min_length=1)


class CncSetOrderDetails(BaseMethod[CncDetailsResult]):
    """Set click-and-collect order details via ``POST /order-management/1/order/cncSetDetails``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/order-management/1/order/cncSetDetails"
    __idempotent_mutation__: ClassVar[bool] = True

    order_id: str = Field(..., min_length=1)
    details: dict[str, Any] = Field(  # typed-Any: pydantic invariant dict field
        default_factory=dict, description="CnC details payload (free-form)."
    )


class GetCourierDeliveryRange(BaseMethod[CourierDeliveryRange]):
    """Fetch the courier delivery range via ``GET /order-management/1/order/getCourierDeliveryRange``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/order-management/1/order/getCourierDeliveryRange"

    order_id: str = Field(..., min_length=1)


class SetCourierDeliveryRange(BaseMethod[CourierDeliveryRange]):
    """Set the courier delivery range via ``POST /order-management/1/order/setCourierDeliveryRange``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/order-management/1/order/setCourierDeliveryRange"
    __idempotent_mutation__: ClassVar[bool] = True

    order_id: str = Field(..., min_length=1)
    date_from: str = Field(
        ..., min_length=1, description="ISO datetime — lower bound of courier window."
    )
    date_to: str = Field(
        ..., min_length=1, description="ISO datetime — upper bound of courier window."
    )
    comment: str | None = Field(default=None, description="Optional buyer-facing note.")


class SetOrderTrackingNumber(BaseMethod[CncDetailsResult]):
    """Set the carrier tracking number via ``POST /order-management/1/order/setTrackingNumber``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/order-management/1/order/setTrackingNumber"
    __idempotent_mutation__: ClassVar[bool] = True

    order_id: str = Field(..., min_length=1)
    carrier: str = Field(..., min_length=1)
    code: str = Field(..., min_length=1)


class ListManagedOrders(BaseMethod[ManagedOrderList]):
    """List managed orders via ``GET /order-management/1/orders``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/order-management/1/orders"

    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=25, ge=1, le=100)
    status: str | None = Field(
        default=None, description="Optional status filter (free-form string)."
    )


class CreateOrderLabels(BaseMethod[LabelTaskResult]):
    """Create order labels (async task) via ``POST /order-management/1/orders/labels``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/order-management/1/orders/labels"
    __idempotent_mutation__: ClassVar[bool] = True

    order_ids: list[str] = Field(
        ..., min_length=1, description="Orders to include in the label batch."
    )


class CreateOrderLabelsExtended(BaseMethod[LabelTaskResult]):
    """Create extended order labels via ``POST /order-management/1/orders/labels/extended``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/order-management/1/orders/labels/extended"
    __idempotent_mutation__: ClassVar[bool] = True

    order_ids: list[str] = Field(
        ..., min_length=1, description="Orders to include in the extended-label batch."
    )
    options: dict[str, Any] = Field(  # typed-Any: pydantic invariant dict field
        default_factory=dict,
        description="Extended label options (format, size, …).",
    )


class DownloadOrderLabels(BaseMethod[bytes]):
    """Download generated labels via ``GET /order-management/1/orders/labels/{taskID}/download``.

    Sets ``__binary_response__ = True`` so :class:`RestProtocol.decode_response`
    returns the raw bytes (PDF / ZIP) verbatim — no JSON decode, no model
    validation. The awaited result is ``bytes``.
    """

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/order-management/1/orders/labels/{taskID}/download"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"taskID"})
    __binary_response__: ClassVar[bool] = True

    taskID: str = Field(..., min_length=1)  # noqa: N815 — Avito uses ``taskID`` verbatim

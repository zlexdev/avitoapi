"""Orders domain — DBS lifecycle endpoints (list, get, status, terms, track, refund)."""
from __future__ import annotations

from typing import ClassVar

from pydantic import Field

from ..models.orders import Order, OrderList, OrderStatus
from ..pagination import PageMethod
from ._base import BaseMethod


class ListOrders(PageMethod[OrderList]):
    """List DBS orders via ``GET /orders/list`` (paginated).

    The DBS surface is documented unevenly across third-party clients;
    consult ``models/orders.py`` ``_MODULE.md`` for the path uncertainty
    note. Defaults follow Avito's ``page`` / ``per_page`` convention.
    """

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/orders/list"
    __items_attr__: ClassVar[str | None] = "orders"

    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=25, ge=1, le=100)


class GetOrder(BaseMethod[Order]):
    """Fetch a single order via ``GET /orders/{order_id}``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/orders/{order_id}"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"order_id"})

    order_id: str = Field(..., min_length=1)


class ChangeOrderStatus(BaseMethod[Order]):
    """Move an order to a new status via ``POST /orders/{order_id}/status``.

    Idempotent mutation — the protocol auto-injects ``Idempotency-Key`` so
    retries don't accidentally trigger a second state-machine transition.
    Client-side guards live on :meth:`Order.change_status` and on the
    Client mixin so the wire call only fires after the transition table
    accepted the move.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/orders/{order_id}/status"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"order_id"})
    __idempotent_mutation__: ClassVar[bool] = True

    order_id: str = Field(..., min_length=1)
    status: OrderStatus = Field(..., description="Target status.")


class TransferDeliveryTerms(BaseMethod[Order]):
    """Transfer delivery terms via ``POST /orders/{order_id}/delivery_terms``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/orders/{order_id}/delivery_terms"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"order_id"})
    __idempotent_mutation__: ClassVar[bool] = True

    order_id: str = Field(..., min_length=1)
    term_days: int = Field(..., ge=0, description="Promised delivery window in days.")
    note: str | None = Field(default=None, description="Optional buyer-facing note.")


class TransferTrackNumber(BaseMethod[Order]):
    """Transfer a carrier tracking number via ``POST /orders/{order_id}/track``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/orders/{order_id}/track"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"order_id"})
    __idempotent_mutation__: ClassVar[bool] = True

    order_id: str = Field(..., min_length=1)
    carrier: str = Field(..., min_length=1)
    code: str = Field(..., min_length=1)


class RefundOrder(BaseMethod[Order]):
    """Refund an order via ``POST /orders/{order_id}/refund``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/orders/{order_id}/refund"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"order_id"})
    __idempotent_mutation__: ClassVar[bool] = True

    order_id: str = Field(..., min_length=1)
    reason: str | None = Field(default=None, description="Free-form refund reason.")

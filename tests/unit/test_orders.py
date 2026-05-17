"""Orders domain — method-class fixture round-trips + bound action wiring."""

from __future__ import annotations

import json
from typing import Any

import pytest
from avitoapi.client import Client
from avitoapi.exceptions import ModelNotBoundError
from avitoapi.methods.orders import (
    ChangeOrderStatus,
    GetOrder,
    ListOrders,
    RefundOrder,
    TransferDeliveryTerms,
    TransferTrackNumber,
)
from avitoapi.models.orders import Order, OrderList, OrderStatus

from tests._fake_session import FakeSession

# ---- get_order round-trip --------------------------------------------------


async def test_get_order_returns_typed_order(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(GetOrder, "orders/get_order.json")

    order = await client(GetOrder(order_id="ord_abc123"))

    assert isinstance(order, Order)
    assert order.id == "ord_abc123"
    assert order.status is OrderStatus.NEW
    assert order.total is not None
    assert str(order.total.amount) == "1500.00"
    assert order.delivery is not None
    assert order.delivery.term_days == 3


# ---- list_orders -----------------------------------------------------------


async def test_list_orders_returns_envelope_with_two_rows(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(ListOrders, "orders/list_orders.json")

    envelope = await client(ListOrders(page=1, per_page=10))

    assert isinstance(envelope, OrderList)
    assert envelope.total == 2
    assert len(envelope.orders) == 2
    assert envelope.orders[0].status is OrderStatus.NEW
    assert envelope.orders[1].status is OrderStatus.SHIPPED
    assert envelope.orders[1].track is not None
    assert envelope.orders[1].track.carrier == "cdek"


# ---- change_order_status mutation -----------------------------------------


async def test_change_order_status_round_trip(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(ChangeOrderStatus, "orders/change_status.json")

    updated = await client(
        ChangeOrderStatus(order_id="ord_abc123", status=OrderStatus.CONFIRMED),
    )

    assert isinstance(updated, Order)
    assert updated.status is OrderStatus.CONFIRMED


async def test_change_order_status_emits_post_with_idempotency_key(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(ChangeOrderStatus, "orders/change_status.json")

    await client(ChangeOrderStatus(order_id="ord_abc123", status=OrderStatus.CONFIRMED))

    prepared = fake_session.sent[-1]
    assert prepared.http_method == "POST"
    assert prepared.url.endswith("/orders/ord_abc123/status")
    assert "Idempotency-Key" in prepared.headers


# ---- delivery / track / refund -------------------------------------------


async def test_transfer_delivery_terms_carries_body_fields(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(TransferDeliveryTerms, "orders/get_order.json")

    await client(
        TransferDeliveryTerms(order_id="ord_abc123", term_days=5, note="Самовывоз"),
    )

    prepared = fake_session.sent[-1]
    assert prepared.http_method == "POST"
    assert prepared.url.endswith("/orders/ord_abc123/delivery_terms")
    assert prepared.body is not None
    body = prepared.body if isinstance(prepared.body, dict) else json.loads(prepared.body)
    assert body["term_days"] == 5
    assert body["note"] == "Самовывоз"


async def test_transfer_track_number_routes_correctly(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(TransferTrackNumber, "orders/get_order.json")

    await client(
        TransferTrackNumber(order_id="ord_abc123", carrier="cdek", code="TR12345"),
    )

    prepared = fake_session.sent[-1]
    assert prepared.url.endswith("/orders/ord_abc123/track")
    body = prepared.body if isinstance(prepared.body, dict) else json.loads(prepared.body)
    assert body["carrier"] == "cdek"
    assert body["code"] == "TR12345"


async def test_refund_order_round_trip(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(RefundOrder, "orders/refund_order.json")

    refunded = await client(RefundOrder(order_id="ord_abc123", reason="defect"))

    assert isinstance(refunded, Order)
    assert refunded.status is OrderStatus.REFUNDED


# ---- bound methods ---------------------------------------------------------


async def test_order_bound_change_status_builds_method_with_client(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(GetOrder, "orders/get_order.json")
    fake_session.bind_fixture(ChangeOrderStatus, "orders/change_status.json")
    order = await client(GetOrder(order_id="ord_abc123"))

    updated = await order.change_status(OrderStatus.CONFIRMED)

    assert isinstance(updated, Order)
    assert updated.status is OrderStatus.CONFIRMED


async def test_order_bound_refund_builds_method(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(GetOrder, "orders/get_order.json")
    fake_session.bind_fixture(RefundOrder, "orders/refund_order.json")
    order = await client(GetOrder(order_id="ord_abc123"))
    # walk to delivered then refund
    order.status = OrderStatus.DELIVERED

    refunded = await order.refund(reason="defect")

    assert refunded.status is OrderStatus.REFUNDED


async def test_order_bound_method_without_client_raises(
    accounts_self_payload: dict[str, Any],  # noqa: ARG001 — just for fixture pattern parity
) -> None:
    order = Order(id="ord_x", status=OrderStatus.NEW)

    with pytest.raises(ModelNotBoundError):
        order.change_status(OrderStatus.CONFIRMED)

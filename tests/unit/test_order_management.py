"""Order-management domain — representative round-trips + bound actions + binary download."""

from __future__ import annotations

import json

import pytest
from avitoapi.client import Client
from avitoapi.exceptions import ModelNotBoundError
from avitoapi.methods.order_management import (
    AcceptReturnOrder,
    ApplyOrderTransition,
    CheckOrderConfirmationCode,
    CreateOrderLabels,
    DownloadOrderLabels,
    GetCourierDeliveryRange,
    ListManagedOrders,
    SetOrderMarkings,
)
from avitoapi.models.order_management import (
    CncDetailsResult,
    CourierDeliveryRange,
    LabelTaskResult,
    ManagedOrder,
    ManagedOrderList,
    ManagedOrderStatus,
    MarkingResult,
    OrderConfirmationCheck,
    OrderMarking,
    OrderTransition,
)

from tests._fake_session import FakeSession

# ---- list managed orders --------------------------------------------------


async def test_list_managed_orders_returns_root_envelope(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(ListManagedOrders, "order_management/list_managed_orders.json")

    orders = await client(ListManagedOrders(page=1, per_page=25))

    assert isinstance(orders, ManagedOrderList)
    assert len(orders) == 2
    assert orders.root[0].id == "om_001"
    # Status field accepts enum-or-string for forward-compat; compare by value.
    assert orders.root[0].status == ManagedOrderStatus.NEW.value
    assert orders.root[1].status == ManagedOrderStatus.SHIPPED.value
    assert len(orders.root[1].markings) == 1


# ---- apply_transition (state-machine-like) -------------------------------


async def test_apply_order_transition_idempotency_key_injected(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(ApplyOrderTransition, "order_management/apply_transition.json")

    result = await client(
        ApplyOrderTransition(order_id="om_001", transition=OrderTransition.CONFIRM),
    )

    assert isinstance(result, CncDetailsResult)
    assert result.ok is True
    prepared = fake_session.sent[-1]
    assert prepared.http_method == "POST"
    assert prepared.url.endswith("/order-management/1/order/applyTransition")
    assert "Idempotency-Key" in prepared.headers
    body = prepared.body if isinstance(prepared.body, dict) else json.loads(prepared.body)
    assert body["transition"] == "confirm"


async def test_apply_transition_serializes_each_verb(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(ApplyOrderTransition, "order_management/apply_transition.json")

    for verb in (
        OrderTransition.SHIP,
        OrderTransition.DELIVER,
        OrderTransition.COMPLETE,
        OrderTransition.CANCEL,
    ):
        await client(ApplyOrderTransition(order_id="om_001", transition=verb))
        prepared = fake_session.sent[-1]
        body = prepared.body if isinstance(prepared.body, dict) else json.loads(prepared.body)
        assert body["transition"] == verb.value


# ---- accept_return --------------------------------------------------------


async def test_accept_return_order_round_trip(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(AcceptReturnOrder, "order_management/accept_return.json")

    result = await client(AcceptReturnOrder(order_id="om_002", comment="OK"))

    assert isinstance(result, CncDetailsResult)
    assert result.order_id == "om_002"


# ---- markings -------------------------------------------------------------


async def test_set_order_markings_routes_post_with_body(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(SetOrderMarkings, "order_management/markings.json")

    result = await client(
        SetOrderMarkings(
            order_id="om_001",
            markings=[OrderMarking(code="0104603726000000215Q1A1B2C", item_id=9001, quantity=1)],
        ),
    )

    assert isinstance(result, MarkingResult)
    assert result.ok is True
    assert "0104603726000000215Q1A1B2C" in result.accepted


# ---- courier range (GET) --------------------------------------------------


async def test_get_courier_delivery_range_routes_get(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(GetCourierDeliveryRange, "order_management/courier_range.json")

    range_ = await client(GetCourierDeliveryRange(order_id="om_001"))

    assert isinstance(range_, CourierDeliveryRange)
    assert range_.comment == "Доставка курьером"
    prepared = fake_session.sent[-1]
    assert prepared.http_method == "GET"


# ---- confirmation code ----------------------------------------------------


async def test_check_order_confirmation_code_returns_check(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(
        CheckOrderConfirmationCode,
        "order_management/confirmation_check.json",
    )

    check = await client(CheckOrderConfirmationCode(order_id="om_001", code="1234"))

    assert isinstance(check, OrderConfirmationCheck)
    assert check.ok is True


# ---- create labels --------------------------------------------------------


async def test_create_order_labels_returns_task(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(CreateOrderLabels, "order_management/labels_task.json")

    task = await client(CreateOrderLabels(order_ids=["om_001", "om_002"]))

    assert isinstance(task, LabelTaskResult)
    assert task.task_id == "labels_task_001"
    assert task.order_ids == ["om_001", "om_002"]


# ---- download labels (binary response) ------------------------------------


async def test_download_order_labels_returns_raw_bytes(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_payload = b"%PDF-1.4\nfakelabelbytes\n"
    fake_session.register(DownloadOrderLabels, body=fake_payload)

    blob = await client(DownloadOrderLabels(taskID="labels_task_001"))

    assert isinstance(blob, bytes)
    assert blob.startswith(b"%PDF")
    prepared = fake_session.sent[-1]
    assert prepared.http_method == "GET"
    assert prepared.url.endswith("/order-management/1/orders/labels/labels_task_001/download")


def test_download_order_labels_declares_binary_response() -> None:
    assert DownloadOrderLabels.__binary_response__ is True


# ---- bound methods --------------------------------------------------------


async def test_managed_order_bound_apply_transition_builds_method(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(ListManagedOrders, "order_management/list_managed_orders.json")
    fake_session.bind_fixture(ApplyOrderTransition, "order_management/apply_transition.json")

    orders = await client(ListManagedOrders())
    first = orders.root[0]

    result = await first.apply_transition(OrderTransition.CONFIRM)

    assert isinstance(result, CncDetailsResult)
    assert result.ok is True


async def test_managed_order_bound_accept_return(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(ListManagedOrders, "order_management/list_managed_orders.json")
    fake_session.bind_fixture(AcceptReturnOrder, "order_management/accept_return.json")

    orders = await client(ListManagedOrders())
    second = orders.root[1]

    result = await second.accept_return()

    assert isinstance(result, CncDetailsResult)


def test_managed_order_bound_method_without_client_raises() -> None:
    order = ManagedOrder(id="om_x", status=ManagedOrderStatus.NEW)

    with pytest.raises(ModelNotBoundError):
        order.apply_transition(OrderTransition.CONFIRM)

"""Delivery-sandbox domain — representative method-class round-trips.

The surface is 31 endpoints — this file samples ~10 covering happy paths,
idempotency injection, path templating, and list envelopes.
"""
from __future__ import annotations

import json

from avitoapi.client import Client
from avitoapi.methods.delivery import (
    CancelParcel,
    CreateParcel,
    GetDeliveryTask,
    GetParcelInfoV1,
    ListTariffAreas,
    ListTariffsV2,
    ListTariffTerminals,
    SetAreaCustomSchedule,
    TrackAnnouncementV1,
)
from avitoapi.models.delivery import (
    DeliveryTask,
    GenericDeliveryResult,
    Parcel,
    ParcelChangeResult,
    ParcelInfo,
    TariffAreaList,
    TariffList,
    TerminalList,
)

from tests._fake_session import FakeSession

# ---- create_parcel round-trip ---------------------------------------------


async def test_create_parcel_returns_parcel(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(CreateParcel, "delivery/create_parcel.json")

    parcel = await client(CreateParcel(payload={"item_id": 9001, "weight_kg": 1.2}))

    assert isinstance(parcel, Parcel)
    assert parcel.id == "parcel_001"
    assert parcel.external_id == "ext_42"


async def test_create_parcel_injects_idempotency_key(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(CreateParcel, "delivery/create_parcel.json")

    await client(CreateParcel(payload={"item_id": 9001}))

    prepared = fake_session.sent[-1]
    assert prepared.http_method == "POST"
    assert prepared.url.endswith("/createParcel")
    assert "Idempotency-Key" in prepared.headers


# ---- cancel_parcel --------------------------------------------------------


async def test_cancel_parcel_returns_change_result(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(CancelParcel, "delivery/cancel_parcel.json")

    result = await client(CancelParcel(parcel_id="parcel_001", reason="buyer_request"))

    assert isinstance(result, ParcelChangeResult)
    assert result.ok is True
    assert result.parcel_id == "parcel_001"


# ---- tariff list (root array envelope) ------------------------------------


async def test_list_tariffs_v2_returns_root_envelope(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(ListTariffsV2, "delivery/tariffs_v2.json")

    tariffs = await client(ListTariffsV2(filters={"carrier": "cdek"}))

    assert isinstance(tariffs, TariffList)
    assert len(tariffs) == 2
    assert tariffs.root[0].carrier == "cdek"


# ---- path templating: tariff areas ---------------------------------------


async def test_list_tariff_areas_renders_tariff_id_in_path(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(ListTariffAreas, "delivery/tariff_areas.json")

    areas = await client(ListTariffAreas(tariff_id="tariff_cdek"))

    assert isinstance(areas, TariffAreaList)
    assert len(areas) == 2
    prepared = fake_session.sent[-1]
    assert prepared.url.endswith("/delivery-sandbox/tariffs/tariff_cdek/areas")
    # tariff_id lives in path, not body
    body = prepared.body if isinstance(prepared.body, dict | type(None)) else json.loads(prepared.body)
    assert body is None or "tariff_id" not in body


async def test_list_tariff_terminals_path_templating(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(ListTariffTerminals, "delivery/tariff_terminals.json")

    terminals = await client(ListTariffTerminals(tariff_id="tariff_post"))

    assert isinstance(terminals, TerminalList)
    prepared = fake_session.sent[-1]
    assert prepared.url.endswith("/delivery-sandbox/tariffs/tariff_post/terminals")


# ---- GET with path templating: delivery task ------------------------------


async def test_get_delivery_task_returns_task(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(GetDeliveryTask, "delivery/delivery_task.json")

    task = await client(GetDeliveryTask(task_id="task_abc123"))

    assert isinstance(task, DeliveryTask)
    assert task.status == "succeeded"
    prepared = fake_session.sent[-1]
    assert prepared.http_method == "GET"
    assert prepared.url.endswith("/delivery-sandbox/tasks/task_abc123")


# ---- generic ack envelope -------------------------------------------------


async def test_set_area_custom_schedule_returns_generic_result(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.register(SetAreaCustomSchedule, body={"ok": True})

    result = await client(
        SetAreaCustomSchedule(area_id="area_msk", schedule={"mon": "09-18"}),
    )

    assert isinstance(result, GenericDeliveryResult)
    assert result.ok is True


# ---- announcement track --------------------------------------------------


async def test_track_announcement_v1_routes_to_v1_endpoint(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.register(
        TrackAnnouncementV1,
        body={"type": "delivered", "occurred_at": "2026-05-17T13:00:00Z", "payload": {}},
    )

    event = await client(TrackAnnouncementV1(announcement_id="ann_xyz"))

    assert event.type == "delivered"
    prepared = fake_session.sent[-1]
    assert prepared.url.endswith("/delivery-sandbox/announcements/track")


# ---- v1 parcel info -------------------------------------------------------


async def test_get_parcel_info_v1_round_trip(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(GetParcelInfoV1, "delivery/parcel_info.json")

    info = await client(GetParcelInfoV1(parcel_id="parcel_001"))

    assert isinstance(info, ParcelInfo)
    assert info.parcel_id == "parcel_001"
    assert info.info["weight_kg"] == 1.2

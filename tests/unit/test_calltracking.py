"""Calltracking — call metadata + binary audio recording streaming."""

from __future__ import annotations

from datetime import UTC, datetime

from avitoapi.client import Client
from avitoapi.methods.calltracking import GetCall, GetCallRecording, ListCalls
from avitoapi.models.calltracking import Call, CallList, CallStatus

from tests._fake_session import FakeSession


async def test_get_call_returns_typed_call(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(GetCall, "calltracking/call.json")

    call = await client(GetCall(call_id="call-abc-1"))

    assert isinstance(call, Call)
    assert call.id == "call-abc-1"
    assert call.status is CallStatus.ANSWERED
    assert call.duration_s == 73


async def test_get_call_uses_path_template(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(GetCall, "calltracking/call.json")

    await client(GetCall(call_id="call-abc-1"))

    prepared = fake_session.sent[-1]
    assert prepared.http_method == "GET"
    assert prepared.url.endswith("/calltracking/v2/calls/call-abc-1")


async def test_list_calls_returns_envelope_with_two_rows(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(ListCalls, "calltracking/calls_list.json")

    calls = await client(
        ListCalls(
            date_from=datetime(2026, 5, 16, tzinfo=UTC),
            date_to=datetime(2026, 5, 17, tzinfo=UTC),
        ),
    )

    assert isinstance(calls, CallList)
    assert len(calls) == 2
    rows = list(calls)
    assert rows[0].status is CallStatus.ANSWERED
    assert rows[1].status is CallStatus.MISSED


async def test_get_call_recording_returns_raw_bytes(
    client: Client,
    fake_session: FakeSession,
) -> None:
    """Validates ``__binary_response__ = True`` short-circuits the JSON decode path."""
    audio = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"\x00" * 100
    fake_session.register(
        GetCallRecording,
        body=audio,
        status=200,
        headers={"content-type": "audio/mpeg"},
    )

    result = await client(GetCallRecording(call_id="call-abc-1"))

    assert isinstance(result, bytes)
    assert result == audio


async def test_get_call_recording_path_includes_call_id(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.register(
        GetCallRecording,
        body=b"raw-audio",
        status=200,
        headers={"content-type": "audio/mpeg"},
    )

    await client(GetCallRecording(call_id="call-xyz"))

    prepared = fake_session.sent[-1]
    assert prepared.url.endswith("/calltracking/v2/calls/call-xyz/recording")

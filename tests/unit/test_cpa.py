"""CPA v3 — balance, calls/chats by time, complaints lifecycle round-trips."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from avitoapi.client import Client
from avitoapi.exceptions import ModelNotBoundError
from avitoapi.methods.cpa import (
    CallsByTime,
    CancelComplaint,
    ChatByActionId,
    ChatsByTime,
    CpaBalance,
    CreateComplaint,
    ListComplaints,
)
from avitoapi.models.cpa import (
    CallList,
    ChatByTime,
    ChatList,
    Complaint,
    ComplaintList,
    ComplaintStatus,
    CpaBalanceInfo,
)

from tests._fake_session import FakeSession


async def test_cpa_balance_round_trip(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(CpaBalance, "cpa/balance.json")

    balance = await client(CpaBalance())

    assert isinstance(balance, CpaBalanceInfo)
    assert str(balance.real.amount) == "12500.50"
    assert str(balance.bonus.amount) == "1000.00"


async def test_calls_by_time_round_trip(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(CallsByTime, "cpa/calls_by_time.json")

    calls = await client(
        CallsByTime(
            date_time_from=datetime(2026, 5, 15, tzinfo=UTC),
            date_time_to=datetime(2026, 5, 16, tzinfo=UTC),
        ),
    )

    assert isinstance(calls, CallList)
    assert len(calls) == 2
    assert calls.root[0].action_id == "act_call_1"
    assert calls.root[0].duration_s == 142


async def test_chats_by_time_round_trip(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(ChatsByTime, "cpa/chats_by_time.json")

    chats = await client(
        ChatsByTime(
            date_time_from=datetime(2026, 5, 15, tzinfo=UTC),
            date_time_to=datetime(2026, 5, 16, tzinfo=UTC),
        ),
    )

    assert isinstance(chats, ChatList)
    assert len(chats) == 1


async def test_chat_by_action_id_round_trip(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(ChatByActionId, "cpa/chat_by_action.json")

    chat = await client(ChatByActionId(action_id="act_chat_1"))

    assert isinstance(chat, ChatByTime)
    assert chat.chat_id == "chat_aaa"


async def test_list_complaints_round_trip(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(ListComplaints, "cpa/complaints.json")

    complaints = await client(ListComplaints())

    assert isinstance(complaints, ComplaintList)
    assert len(complaints) == 1
    assert complaints.root[0].status is ComplaintStatus.PENDING


async def test_create_complaint_idempotent(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.bind_fixture(CreateComplaint, "cpa/complaint.json")

    complaint = await client(
        CreateComplaint(action_id="act_call_2", kind="spam"),
    )

    assert isinstance(complaint, Complaint)
    assert complaint.id == "cpl_2"
    prepared = fake_session.sent[-1]
    assert "Idempotency-Key" in prepared.headers


async def test_cancel_complaint_idempotent(
    client: Client,
    fake_session: FakeSession,
) -> None:
    fake_session.register(CancelComplaint, body=b"", status=204)

    result = await client(CancelComplaint(complaint_id="cpl_2"))

    assert result is None
    prepared = fake_session.sent[-1]
    assert prepared.http_method == "POST"
    assert prepared.url.endswith("/cpa/v3/complaints/cpl_2/cancel")
    assert "Idempotency-Key" in prepared.headers


async def test_complaint_bound_cancel_without_client_raises() -> None:
    complaint = Complaint(
        id="cpl_x",
        action_id="act_x",
        kind="spam",
        status=ComplaintStatus.PENDING,
        created_at=datetime(2026, 5, 16, tzinfo=UTC),
    )

    with pytest.raises(ModelNotBoundError):
        complaint.cancel()

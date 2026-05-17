"""Unit tests for :class:`AvitoWebhookHandler`."""

from __future__ import annotations

import json

from avitoapi.events.messenger import ChatArchived, MessageRead, NewMessage
from avitoapi.routers import Router
from avitoapi.web.avito_webhook_handler import (
    AvitoWebhookHandler,
    AvitoWebhookParseError,
)


def _envelope(kind: str, value: dict) -> dict:
    return {
        "id": "evt-1",
        "version": "v3.0.0",
        "timestamp": 1700000000,
        "payload": {"type": kind, "value": value},
    }


class _DispatcherStub:
    def __init__(self) -> None:
        self.feed_calls: list[object] = []
        self.router = Router()

    async def feed_event(self, event) -> None:
        self.feed_calls.append(event)


async def test_parse_new_message():
    payload = _envelope(
        "message",
        {"user_id": "acc-1", "chat_id": "chat-42", "id": "msg-1", "text": "hi"},
    )
    event = AvitoWebhookHandler.parse_event(payload)
    assert isinstance(event, NewMessage)
    assert event.account_id == "acc-1"
    assert event.chat_id == "chat-42"
    assert event.message["text"] == "hi"


async def test_parse_message_read():
    payload = _envelope(
        "message_read",
        {"user_id": "acc-1", "chat_id": "chat-42", "message_id": "msg-9"},
    )
    event = AvitoWebhookHandler.parse_event(payload)
    assert isinstance(event, MessageRead)
    assert event.message_id == "msg-9"


async def test_parse_chat_archived():
    payload = _envelope("chat_archived", {"user_id": "acc-1", "chat_id": "chat-42"})
    event = AvitoWebhookHandler.parse_event(payload)
    assert isinstance(event, ChatArchived)
    assert event.chat_id == "chat-42"


async def test_parse_missing_ids_raises():
    payload = _envelope("message", {"text": "no ids"})
    try:
        AvitoWebhookHandler.parse_event(payload)
    except AvitoWebhookParseError as exc:
        assert "account_id" in str(exc) or "chat_id" in str(exc)
    else:
        raise AssertionError("expected AvitoWebhookParseError")


async def test_parse_unknown_kind_raises():
    payload = _envelope("alien", {"user_id": "x", "chat_id": "y"})
    try:
        AvitoWebhookHandler.parse_event(payload)
    except AvitoWebhookParseError as exc:
        assert "alien" in str(exc)
    else:
        raise AssertionError("expected AvitoWebhookParseError")


async def test_handle_bad_json_returns_400():
    dispatcher = _DispatcherStub()
    handler = AvitoWebhookHandler(dispatcher)
    status, body = await handler.handle(b"this is not json")
    assert status == 400
    assert body == {"error": "invalid_body"}
    assert not dispatcher.feed_calls


async def test_handle_unknown_kind_returns_200_skipped():
    dispatcher = _DispatcherStub()
    handler = AvitoWebhookHandler(dispatcher)
    payload = _envelope("nope", {"user_id": "a", "chat_id": "c"})
    status, body = await handler.handle(json.dumps(payload).encode())
    assert status == 200
    assert body.get("ok") is True
    assert "skipped" in body
    assert not dispatcher.feed_calls


async def test_handle_dispatches_to_feed_event():
    dispatcher = _DispatcherStub()
    handler = AvitoWebhookHandler(dispatcher)
    payload = _envelope(
        "message",
        {"user_id": "acc-1", "chat_id": "chat-1", "id": "m", "text": "hi"},
    )
    status, body = await handler.handle(json.dumps(payload).encode())
    assert status == 200
    assert body == {"ok": True}
    assert len(dispatcher.feed_calls) == 1
    assert isinstance(dispatcher.feed_calls[0], NewMessage)


async def test_handle_falls_back_to_router_when_no_feed_event():
    class _NoFeedDispatcher:
        def __init__(self):
            self.router = Router()

    dispatcher = _NoFeedDispatcher()
    received: list[NewMessage] = []

    @dispatcher.router.new_message()
    async def handle(event: NewMessage, _ctx: object) -> None:
        received.append(event)

    handler = AvitoWebhookHandler(dispatcher)
    payload = _envelope(
        "message",
        {"user_id": "acc-1", "chat_id": "c-1", "id": "m", "text": "hi"},
    )
    status, _ = await handler.handle(json.dumps(payload).encode())
    assert status == 200
    assert len(received) == 1
    assert received[0].chat_id == "c-1"


async def test_handle_accepts_dict_directly():
    dispatcher = _DispatcherStub()
    handler = AvitoWebhookHandler(dispatcher)
    payload = _envelope(
        "message",
        {"user_id": "acc-1", "chat_id": "c-1", "id": "m", "text": "hi"},
    )
    status, body = await handler.handle(payload)
    assert status == 200
    assert body == {"ok": True}
    assert len(dispatcher.feed_calls) == 1

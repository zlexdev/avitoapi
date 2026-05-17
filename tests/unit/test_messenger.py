"""Unit tests for the messenger method-classes.

Each method-class is exercised through the funnel using :class:`FakeSession`
canned responses. Tests assert:

- the wire URL/path is what RestProtocol renders from ``__endpoint__`` +
  ``__path_fields__``,
- query / body routing matches the verb,
- the decoded response is the right typed DTO with the client pre-bound.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from avitoapi.client import Client
from avitoapi.config import ClientConfig
from avitoapi.methods.messenger import (
    AddBlacklist,
    DeleteMessage,
    GetChat,
    GetVoiceFiles,
    ListBlacklist,
    ListChats,
    ListMessages,
    ListSubscriptions,
    MarkChatRead,
    RemoveBlacklist,
    SendImageMessage,
    SendTextMessage,
    SubscribeWebhook,
    UnsubscribeWebhook,
    UploadImage,
)
from avitoapi.models.messenger import (
    Blacklist,
    Chat,
    ChatList,
    DeleteResult,
    MessageEnvelope,
    MessageList,
    SubscriptionList,
    TextMessage,
    UploadImageResult,
    VoiceFiles,
    WebhookActionResult,
)
from avitoapi.storage.memory import MemoryStorage

from tests._fake_session import FakeSession

FIXTURES = Path(__file__).parent.parent / "fixtures" / "messenger"


def _load(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.fixture
def msgr_config() -> ClientConfig:
    return ClientConfig(
        client_id="cid",
        client_secret="secret",
        user_id=42,
        max_retries=0,
        backoff_initial_s=0.001,
        backoff_max_s=0.01,
    )


@pytest.fixture
async def msgr_client(msgr_config: ClientConfig) -> Any:
    session = FakeSession(config=msgr_config)
    storage = MemoryStorage()
    session.register_route(
        "POST",
        "/token",
        body={"access_token": "tok", "token_type": "Bearer", "expires_in": 3600},
    )
    session.register_route(
        "GET",
        "/token/",
        body={"access_token": "tok", "token_type": "Bearer", "expires_in": 3600},
    )
    client = Client(config=msgr_config, session=session, storage=storage)
    yield client, session
    await client.close()


# ---- ListChats -------------------------------------------------------------


async def test_list_chats_decodes_chat_list_and_renders_path(
    msgr_client: tuple[Client, FakeSession],
) -> None:
    client, session = msgr_client
    session.register(ListChats, body=_load("chats_list.json"))

    result = await client(ListChats(user_id=42, unread_only=True, limit=50))

    assert isinstance(result, ChatList)
    assert len(result.chats) == 2
    assert result.chats[0].id == "u2i-aaa111"
    sent = session.sent[-1]
    assert sent.http_method == "GET"
    assert "/messenger/v2/accounts/42/chats" in sent.url
    assert sent.query.get("unread_only") is True
    assert sent.query.get("limit") == 50


# ---- GetChat ---------------------------------------------------------------


async def test_get_chat_renders_path_and_decodes_chat(
    msgr_client: tuple[Client, FakeSession],
) -> None:
    client, session = msgr_client
    session.register(GetChat, body=_load("chat_detail.json"))

    chat = await client(GetChat(user_id=42, chat_id="u2i-aaa111"))

    assert isinstance(chat, Chat)
    assert chat.id == "u2i-aaa111"
    assert chat.unread_count == 0
    sent = session.sent[-1]
    assert "/messenger/v2/accounts/42/chats/u2i-aaa111" in sent.url
    assert sent.http_method == "GET"


# ---- ListMessages ----------------------------------------------------------


async def test_list_messages_renders_v3_path_and_decodes(
    msgr_client: tuple[Client, FakeSession],
) -> None:
    client, session = msgr_client
    session.register(ListMessages, body=_load("messages_p1.json"))

    result = await client(ListMessages(user_id=42, chat_id="u2i-aaa111", limit=20))

    assert isinstance(result, MessageList)
    assert len(result.messages) == 3
    sent = session.sent[-1]
    assert "/messenger/v3/accounts/42/chats/u2i-aaa111/messages/" in sent.url
    assert sent.query.get("limit") == 20


# ---- SendTextMessage -------------------------------------------------------


async def test_send_text_message_posts_body_and_idempotency_header(
    msgr_client: tuple[Client, FakeSession],
) -> None:
    client, session = msgr_client
    session.register(
        SendTextMessage,
        body={
            "id": "msg-new-001",
            "chat_id": "u2i-aaa111",
            "author_id": 42,
            "created_at": "2026-05-16T12:00:00+00:00",
            "type": "text",
            "content": {"text": "hi"},
        },
    )

    envelope = await client(SendTextMessage(user_id=42, chat_id="u2i-aaa111", text="hi"))

    assert isinstance(envelope, MessageEnvelope)
    assert isinstance(envelope.root, TextMessage)
    assert envelope.root.content.text == "hi"
    sent = session.sent[-1]
    assert sent.http_method == "POST"
    assert "/messenger/v1/accounts/42/chats/u2i-aaa111/messages" in sent.url
    assert sent.body is not None
    assert sent.body.get("text") == "hi"
    assert sent.body.get("type") == "text"
    assert "Idempotency-Key" in sent.headers


# ---- SendImageMessage ------------------------------------------------------


async def test_send_image_posts_image_id_in_body(msgr_client: tuple[Client, FakeSession]) -> None:
    client, session = msgr_client
    session.register(
        SendImageMessage,
        body={
            "id": "msg-img-001",
            "chat_id": "u2i-aaa111",
            "author_id": 42,
            "created_at": "2026-05-16T12:01:00+00:00",
            "type": "image",
            "content": {"image_id": "img-xyz", "sizes": {}},
        },
    )

    envelope = await client(SendImageMessage(user_id=42, chat_id="u2i-aaa111", image_id="img-xyz"))

    assert isinstance(envelope, MessageEnvelope)
    assert envelope.root.type == "image"
    sent = session.sent[-1]
    assert sent.http_method == "POST"
    assert sent.url.endswith("/messages/image")
    assert sent.body.get("image_id") == "img-xyz"


# ---- MarkChatRead ----------------------------------------------------------


async def test_mark_chat_read_posts_to_read_endpoint(
    msgr_client: tuple[Client, FakeSession],
) -> None:
    client, session = msgr_client
    session.register(MarkChatRead, body={"success": True})

    result = await client(MarkChatRead(user_id=42, chat_id="u2i-aaa111"))

    assert isinstance(result, DeleteResult)
    assert result.success is True
    sent = session.sent[-1]
    assert sent.http_method == "POST"
    assert sent.url.endswith("/chats/u2i-aaa111/read")
    assert "Idempotency-Key" in sent.headers


# ---- DeleteMessage ---------------------------------------------------------


async def test_delete_message_renders_three_path_fields(
    msgr_client: tuple[Client, FakeSession],
) -> None:
    client, session = msgr_client
    session.register(DeleteMessage, body={"success": True})

    result = await client(DeleteMessage(user_id=42, chat_id="u2i-aaa111", message_id="msg-1"))

    assert isinstance(result, DeleteResult)
    sent = session.sent[-1]
    assert sent.http_method == "DELETE"
    assert "/messenger/v1/accounts/42/chats/u2i-aaa111/messages/msg-1" in sent.url


# ---- UploadImage -----------------------------------------------------------


async def test_upload_image_collapses_random_key_response(
    msgr_client: tuple[Client, FakeSession],
) -> None:
    client, session = msgr_client
    session.register(UploadImage, body=_load("upload_image_response.json"))

    result = await client(
        UploadImage(user_id=42, filename="pic.jpg", image_bytes=b"fake-image-bytes"),
    )

    assert isinstance(result, UploadImageResult)
    assert result.image_id == "img-uploaded-id-12345"
    sent = session.sent[-1]
    assert sent.http_method == "POST"
    assert sent.url.endswith("/messenger/v1/accounts/42/uploadImages")


# ---- ListBlacklist ---------------------------------------------------------


async def test_list_blacklist_decodes_blacklist_envelope(
    msgr_client: tuple[Client, FakeSession],
) -> None:
    client, session = msgr_client
    session.register(ListBlacklist, body={"users": [{"user_id": 99}, {"user_id": 100}]})

    result = await client(ListBlacklist(user_id=42))

    assert isinstance(result, Blacklist)
    assert {u.user_id for u in result.users} == {99, 100}
    sent = session.sent[-1]
    assert sent.http_method == "GET"
    assert sent.url.endswith("/messenger/v1/accounts/42/blacklist")


# ---- AddBlacklist ----------------------------------------------------------


async def test_add_blacklist_posts_user_ids(msgr_client: tuple[Client, FakeSession]) -> None:
    client, session = msgr_client
    session.register(AddBlacklist, body={"success": True})

    result = await client(AddBlacklist(user_id=42, users=[101, 102]))

    assert isinstance(result, DeleteResult)
    sent = session.sent[-1]
    assert sent.http_method == "POST"
    assert sent.url.endswith("/messenger/v2/accounts/42/blacklist")
    assert sent.body.get("users") == [101, 102]
    assert "Idempotency-Key" in sent.headers


# ---- RemoveBlacklist -------------------------------------------------------


async def test_remove_blacklist_uses_delete_verb_with_target(
    msgr_client: tuple[Client, FakeSession],
) -> None:
    client, session = msgr_client
    session.register(RemoveBlacklist, body={"success": True})

    result = await client(RemoveBlacklist(user_id=42, target_user_id=101))

    assert isinstance(result, DeleteResult)
    sent = session.sent[-1]
    assert sent.http_method == "DELETE"
    assert "/messenger/v2/accounts/42/blacklist/101" in sent.url


# ---- GetVoiceFiles ---------------------------------------------------------


async def test_get_voice_files_renders_query_and_decodes(
    msgr_client: tuple[Client, FakeSession],
) -> None:
    client, session = msgr_client
    session.register(
        GetVoiceFiles,
        body={
            "voices": [
                {"voice_id": "v-1", "url": "https://cdn.avito.ru/voices/v-1.mp3"},
                {"voice_id": "v-2", "url": "https://cdn.avito.ru/voices/v-2.mp3"},
            ],
        },
    )

    result = await client(GetVoiceFiles(user_id=42, voice_ids=["v-1", "v-2"]))

    assert isinstance(result, VoiceFiles)
    assert len(result.voices) == 2
    sent = session.sent[-1]
    assert sent.http_method == "GET"
    assert sent.url.endswith("/messenger/v1/accounts/42/voice/files")
    assert sent.query.get("voice_ids") == ["v-1", "v-2"]


# ---- Bound actions on Chat / Message --------------------------------------


async def test_chat_send_text_builds_bound_send_text_message(
    msgr_client: tuple[Client, FakeSession],
) -> None:
    client, session = msgr_client
    session.register(GetChat, body=_load("chat_detail.json"))

    chat = await client(GetChat(user_id=42, chat_id="u2i-aaa111"))
    method = chat.send_text("hello")

    assert isinstance(method, SendTextMessage)
    assert method.chat_id == "u2i-aaa111"
    assert method.text == "hello"
    assert method._client is client


async def test_message_reply_uses_send_text_regardless_of_source(
    msgr_client: tuple[Client, FakeSession],
) -> None:
    """Reply is always a SendTextMessage even when source variant is image / voice."""

    client, session = msgr_client
    session.register(GetChat, body=_load("chat_detail.json"))

    chat = await client(GetChat(user_id=42, chat_id="u2i-aaa111"))
    assert chat.last_message is not None

    reply = chat.last_message.reply("ok")
    assert isinstance(reply, SendTextMessage)
    assert reply.chat_id == chat.id


# ---- webhook lifecycle (W7-A) ---------------------------------------------


async def test_subscribe_webhook_posts_url_and_secret(
    msgr_client: tuple[Client, FakeSession],
) -> None:
    client, session = msgr_client
    session.register(SubscribeWebhook, body={"success": True, "message": "subscribed"})

    result = await client(
        SubscribeWebhook(url="https://example.com/hook", secret="topsecret"),
    )

    assert isinstance(result, WebhookActionResult)
    assert result.success is True
    sent = session.sent[-1]
    assert sent.http_method == "POST"
    assert sent.url.endswith("/messenger/v3/webhook")
    assert sent.body is not None
    assert sent.body.get("url") == "https://example.com/hook"
    assert sent.body.get("secret") == "topsecret"
    assert "Idempotency-Key" in sent.headers


async def test_unsubscribe_webhook_posts_url(msgr_client: tuple[Client, FakeSession]) -> None:
    client, session = msgr_client
    session.register(UnsubscribeWebhook, body={"success": True})

    result = await client(UnsubscribeWebhook(url="https://example.com/hook"))

    assert isinstance(result, WebhookActionResult)
    sent = session.sent[-1]
    assert sent.http_method == "POST"
    assert sent.url.endswith("/messenger/v1/webhook/unsubscribe")
    assert sent.body is not None
    assert sent.body.get("url") == "https://example.com/hook"
    assert "Idempotency-Key" in sent.headers


async def test_list_subscriptions_decodes_envelope(msgr_client: tuple[Client, FakeSession]) -> None:
    client, session = msgr_client
    session.register(
        ListSubscriptions,
        body=[
            {"url": "https://example.com/hook", "callbackId": "cb-1", "version": "v3"},
            {"url": "https://example.com/legacy", "callbackId": "cb-2", "version": "v1"},
        ],
    )

    subs = await client(ListSubscriptions())

    assert isinstance(subs, SubscriptionList)
    assert len(subs) == 2
    rows = list(subs)
    assert rows[0].callback_id == "cb-1"
    assert rows[1].version == "v1"
    sent = session.sent[-1]
    assert sent.http_method == "POST"
    assert sent.url.endswith("/messenger/v1/subscriptions")

"""Messenger v2/v3 endpoints — chats, messages, blacklist, voice, image upload.

Mutating method-classes declare ``__idempotent_mutation__ = True`` so
:class:`RestProtocol` auto-injects an ``Idempotency-Key`` header dedup'd
across retries.

``UploadImage`` currently rides the bytes inside the JSON body (base64-
encoded). Switching to real ``multipart/form-data`` requires
:class:`RestProtocol` + :class:`CurlSession` to honour ``__multipart__``
via ``PreparedRequest.files``.
"""
from __future__ import annotations

from typing import ClassVar

from pydantic import Field

from ..models.messenger import (
    Blacklist,
    Chat,
    ChatList,
    DeleteResult,
    MessageEnvelope,
    MessageList,
    SubscriptionList,
    UploadImageResult,
    VoiceFiles,
    WebhookActionResult,
)
from ..pagination import OffsetMethod
from ._base import BaseMethod


class ListChats(OffsetMethod[ChatList]):
    """List chats via ``GET /messenger/v2/accounts/{user_id}/chats``.

    Args:
        user_id: Avito account id (own user).
        unread_only: When true, return only chats with unread messages.
        item_ids: Optional filter — chats about specific items.
        limit: Page size (Avito default 100).
        offset: Time-window offset for paging.
    """

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/messenger/v2/accounts/{user_id}/chats"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"user_id"})
    __items_attr__: ClassVar[str | None] = "chats"

    user_id: int = Field(..., ge=1)
    unread_only: bool | None = Field(default=None)
    item_ids: list[int] | None = Field(default=None)
    limit: int = Field(default=100, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class GetChat(BaseMethod[Chat]):
    """Fetch one chat via ``GET /messenger/v2/accounts/{user_id}/chats/{chat_id}``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/messenger/v2/accounts/{user_id}/chats/{chat_id}"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"user_id", "chat_id"})

    user_id: int = Field(..., ge=1)
    chat_id: str = Field(..., min_length=1)


class ListMessages(OffsetMethod[MessageList]):
    """List messages via ``GET /messenger/v3/accounts/{user_id}/chats/{chat_id}/messages/``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = (
        "/messenger/v3/accounts/{user_id}/chats/{chat_id}/messages/"
    )
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"user_id", "chat_id"})
    __items_attr__: ClassVar[str | None] = "messages"

    user_id: int = Field(..., ge=1)
    chat_id: str = Field(..., min_length=1)
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class SendTextMessage(BaseMethod[MessageEnvelope]):
    """Send a text message via ``POST /messenger/v1/.../chats/{chat_id}/messages``.

    Body shape (per Avito wire): ``{"text": ..., "type": "text"}``. We declare
    ``text`` + ``type`` and let :class:`RestProtocol`'s default body routing
    emit them.

    Returns:
        :class:`MessageEnvelope` whose ``.root`` is the typed :class:`Message`
        variant (via discriminated union).
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/messenger/v1/accounts/{user_id}/chats/{chat_id}/messages"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"user_id", "chat_id"})
    __idempotent_mutation__: ClassVar[bool] = True

    user_id: int = Field(..., ge=1)
    chat_id: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1, max_length=4096)
    type: str = Field(default="text")


class SendImageMessage(BaseMethod[MessageEnvelope]):
    """Send an image via ``POST /messenger/v1/.../chats/{chat_id}/messages/image``.

    The ``image_id`` must come from a prior :class:`UploadImage` call.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = (
        "/messenger/v1/accounts/{user_id}/chats/{chat_id}/messages/image"
    )
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"user_id", "chat_id"})
    __idempotent_mutation__: ClassVar[bool] = True

    user_id: int = Field(..., ge=1)
    chat_id: str = Field(..., min_length=1)
    image_id: str = Field(..., min_length=1)


class MarkChatRead(BaseMethod[DeleteResult]):
    """Mark whole chat read via ``POST /messenger/v1/.../chats/{chat_id}/read``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/messenger/v1/accounts/{user_id}/chats/{chat_id}/read"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"user_id", "chat_id"})
    __idempotent_mutation__: ClassVar[bool] = True

    user_id: int = Field(..., ge=1)
    chat_id: str = Field(..., min_length=1)


class DeleteMessage(BaseMethod[DeleteResult]):
    """Delete one message via ``DELETE /messenger/v1/.../chats/{chat_id}/messages/{message_id}``."""

    __http_method__: ClassVar[str] = "DELETE"
    __endpoint__: ClassVar[str] = (
        "/messenger/v1/accounts/{user_id}/chats/{chat_id}/messages/{message_id}"
    )
    __path_fields__: ClassVar[frozenset[str]] = frozenset(
        {"user_id", "chat_id", "message_id"},
    )

    user_id: int = Field(..., ge=1)
    chat_id: str = Field(..., min_length=1)
    message_id: str = Field(..., min_length=1)


class UploadImage(BaseMethod[UploadImageResult]):
    """Upload a chat image via ``POST /messenger/v1/accounts/{user_id}/uploadImages``.

    Bytes currently ride inside the JSON body (base64-encoded by Pydantic's
    JSON dump). ``__multipart__ = True`` is declared for the future
    multipart-aware Protocol/Session pair.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/messenger/v1/accounts/{user_id}/uploadImages"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"user_id"})
    __idempotent_mutation__: ClassVar[bool] = True
    __multipart__: ClassVar[bool] = True

    user_id: int = Field(..., ge=1)
    filename: str = Field(..., min_length=1)
    image_bytes: bytes = Field(
        ...,
        description="Raw image bytes; encoded for the wire by the session layer.",
    )


class ListBlacklist(BaseMethod[Blacklist]):
    """Fetch the blacklist via ``GET /messenger/v1/accounts/{user_id}/blacklist``."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/messenger/v1/accounts/{user_id}/blacklist"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"user_id"})

    user_id: int = Field(..., ge=1)


class AddBlacklist(BaseMethod[DeleteResult]):
    """Block users via ``POST /messenger/v2/accounts/{user_id}/blacklist``."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/messenger/v2/accounts/{user_id}/blacklist"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"user_id"})
    __idempotent_mutation__: ClassVar[bool] = True

    user_id: int = Field(..., ge=1)
    users: list[int] = Field(..., min_length=1, description="User ids to block.")


class RemoveBlacklist(BaseMethod[DeleteResult]):
    """Unblock one user via ``DELETE /messenger/v2/.../blacklist/{target_user_id}``."""

    __http_method__: ClassVar[str] = "DELETE"
    __endpoint__: ClassVar[str] = (
        "/messenger/v2/accounts/{user_id}/blacklist/{target_user_id}"
    )
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"user_id", "target_user_id"})

    user_id: int = Field(..., ge=1)
    target_user_id: int = Field(..., ge=1)


class GetVoiceFiles(BaseMethod[VoiceFiles]):
    """Resolve voice URLs via ``GET /messenger/v1/accounts/{user_id}/voice/files``.

    Args:
        user_id: Auth'd user id.
        voice_ids: ids extracted from :class:`VoiceMessage.content.voice_id`.
    """

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/messenger/v1/accounts/{user_id}/voice/files"
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"user_id"})

    user_id: int = Field(..., ge=1)
    voice_ids: list[str] = Field(..., min_length=1)


class SubscribeWebhook(BaseMethod[WebhookActionResult]):
    """Register a messenger webhook via ``POST /messenger/v3/webhook``.

    Args:
        url: Public callback URL (HTTPS recommended).
        secret: Optional shared secret Avito signs payloads with.

    Idempotent — re-registering the same URL is a no-op.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/messenger/v3/webhook"
    __idempotent_mutation__: ClassVar[bool] = True

    url: str = Field(..., min_length=1, description="Callback URL.")
    secret: str | None = Field(default=None, description="Optional signing secret.")


class UnsubscribeWebhook(BaseMethod[WebhookActionResult]):
    """Unregister a messenger webhook via ``POST /messenger/v1/webhook/unsubscribe``.

    Idempotent — unsubscribing an already-removed URL returns success.
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/messenger/v1/webhook/unsubscribe"
    __idempotent_mutation__: ClassVar[bool] = True

    url: str = Field(..., min_length=1, description="Callback URL to unregister.")


class ListSubscriptions(BaseMethod[SubscriptionList]):
    """Enumerate active subscriptions via ``POST /messenger/v1/subscriptions``.

    POST despite being a read — Avito's wire requires an empty JSON body
    (auth header carries the account scope).
    """

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/messenger/v1/subscriptions"

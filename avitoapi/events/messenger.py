"""Messenger domain events.

Each event carries the originating ``account_id`` so multi-account
dispatchers can route to per-account handlers. ``NewMessage.message`` is
typed as the :data:`avitoapi.models.messenger.Message` discriminated union
so handlers get full IDE completion + type narrowing on ``message.type``.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import Field

from ..models._base import AvitoObject
from ._base import Event as BaseEvent


class MessageType(StrEnum):
    """All ``type`` values Avito has shipped on the messenger surface.

    Minimal local enum: no generated enum matches 1:1 — ``WebhookMessageType``
    lacks ``UNKNOWN`` and spells the app-call variant ``APPCALL``/``VIDEO``
    instead of this SDK's ``APP_CALL`` naming used by :func:`avitoapi.routers.install_observers`.
    """

    TEXT = "text"
    IMAGE = "image"
    LINK = "link"
    ITEM = "item"
    LOCATION = "location"
    VOICE = "voice"
    CALL = "call"
    FILE = "file"
    SYSTEM = "system"
    APP_CALL = "appCall"
    DELETED = "deleted"
    UNKNOWN = "_unknown"


class Message(AvitoObject):
    """Normalized messenger payload for :class:`NewMessage`.

    Minimal local DTO: no generated model matches this shape —
    ``MessagesRoot``/``WebhookMessage`` alias their discriminator field as
    ``type_`` (Pydantic alias ``"type"``), while :func:`avitoapi.routers.install_observers`
    narrows on a plain ``.type`` attribute for both the webhook and REST paths.
    """

    type: MessageType | None = None


class MessengerEvent(BaseEvent, event_name="messenger"):
    """Common ancestor of every messenger-domain event."""

    account_id: str
    chat_id: str


class NewMessage(MessengerEvent, event_name="messenger.new_message"):
    """A new inbound message landed in one of the bot's chats.

    ``message`` is the typed :class:`Message` on the REST path; the webhook
    path delivers a raw ``dict`` (the typed union is only built for REST), so
    the field accepts either. Specialised observers
    (:class:`avitoapi.routers.Router.text_message`, etc.) narrow on
    ``message.type`` when a typed :class:`Message` is present.
    """

    # left_to_right: a webhook raw dict stays a dict (verbatim); a REST-built
    # Message instance stays a Message. Smart-union would coerce some dicts.
    message: dict[str, Any] | Message = Field(union_mode="left_to_right")

    @property
    def dedup_key(self) -> str:
        msg = self.message
        if isinstance(msg, dict):
            mid = str(msg.get("id") or msg.get("message_id") or "")
        else:
            mid = str(getattr(msg, "id", "") or getattr(msg, "message_id", ""))
        return f"messenger.new_message:{self.account_id}:{self.chat_id}:{mid}"


class MessageRead(MessengerEvent, event_name="messenger.message_read"):
    """The counterparty marked a message as read."""

    message_id: str


class ChatArchived(MessengerEvent, event_name="messenger.chat_archived"):
    """A chat was archived (by the user or by the system)."""


class ChatBlacklisted(MessengerEvent, event_name="messenger.chat_blacklisted"):
    """The counterparty was added to the account blacklist."""

    blocked_user_id: int


class VoiceFileResolved(MessengerEvent, event_name="messenger.voice_file_resolved"):
    """The CDN URL for a voice message has been resolved.

    Emitted by the voice-resolver helper after a successful
    ``GET /messenger/v1/.../voice/files``. Lets handlers download or
    transcribe the file without polling for the URL themselves.
    """

    voice_id: str
    url: str


__all__ = [
    "BaseEvent",
    "ChatArchived",
    "ChatBlacklisted",
    "MessageRead",
    "MessengerEvent",
    "NewMessage",
    "VoiceFileResolved",
]

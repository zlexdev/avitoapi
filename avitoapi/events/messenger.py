"""Messenger domain events.

Each event carries the originating ``account_id`` so multi-account
dispatchers can route to per-account handlers. ``NewMessage.message`` is
typed as the :data:`avitoapi.models.messenger.Message` discriminated union
so handlers get full IDE completion + type narrowing on ``message.type``.
"""

from __future__ import annotations

from enum import StrEnum

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

    def __init__(self, *, account_id: str, chat_id: str, **kwargs: object) -> None:
        super().__init__()
        self.account_id = account_id
        self.chat_id = chat_id
        for k, v in kwargs.items():
            setattr(self, k, v)


class NewMessage(MessengerEvent, event_name="messenger.new_message"):
    """A new inbound message landed in one of the bot's chats.

    ``message`` is the typed discriminated union — use
    ``isinstance(event.message, TextMessage)`` or ``event.message.type`` to
    branch on the variant. Specialised observers
    (:class:`avitoapi.routers.MessengerRouter.text_message`, etc.) filter on
    the variant for you, so a handler bound to ``router.text_message``
    receives only ``NewMessage`` events whose payload is a ``TextMessage``.
    """

    message: Message

    def __init__(self, *, account_id: str, chat_id: str, message: Message) -> None:
        super().__init__(account_id=account_id, chat_id=chat_id)
        self.message = message


class MessageRead(MessengerEvent, event_name="messenger.message_read"):
    """The counterparty marked a message as read."""

    message_id: str

    def __init__(self, *, account_id: str, chat_id: str, message_id: str) -> None:
        super().__init__(account_id=account_id, chat_id=chat_id)
        self.message_id = message_id


class ChatArchived(MessengerEvent, event_name="messenger.chat_archived"):
    """A chat was archived (by the user or by the system)."""

    def __init__(self, *, account_id: str, chat_id: str) -> None:
        super().__init__(account_id=account_id, chat_id=chat_id)


class ChatBlacklisted(MessengerEvent, event_name="messenger.chat_blacklisted"):
    """The counterparty was added to the account blacklist."""

    blocked_user_id: int

    def __init__(self, *, account_id: str, chat_id: str, blocked_user_id: int) -> None:
        super().__init__(account_id=account_id, chat_id=chat_id)
        self.blocked_user_id = blocked_user_id


class VoiceFileResolved(MessengerEvent, event_name="messenger.voice_file_resolved"):
    """The CDN URL for a voice message has been resolved.

    Emitted by the voice-resolver helper after a successful
    ``GET /messenger/v1/.../voice/files``. Lets handlers download or
    transcribe the file without polling for the URL themselves.
    """

    voice_id: str
    url: str

    def __init__(self, *, account_id: str, chat_id: str, voice_id: str, url: str) -> None:
        super().__init__(account_id=account_id, chat_id=chat_id)
        self.voice_id = voice_id
        self.url = url


__all__ = [
    "BaseEvent",
    "ChatArchived",
    "ChatBlacklisted",
    "MessageRead",
    "MessengerEvent",
    "NewMessage",
    "VoiceFileResolved",
]

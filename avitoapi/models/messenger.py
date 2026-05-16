"""Messenger domain — chats, message discriminated union, bound actions.

Avito's messenger v2/v3 returns one wire shape for chats and a polymorphic
``Message`` whose payload depends on ``type``. We model the polymorphism as a
Pydantic v2 *discriminated union* on the ``type`` field so each variant has
its own typed ``content`` shape, and an :class:`UnknownMessage` fallback
absorbs forward-compat ``type`` values from future Avito rollouts.
"""
from __future__ import annotations

import logging
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, RootModel, model_validator

from ._base import BoundModel
from .common import Money

if TYPE_CHECKING:
    from ..methods.messenger import (
        DeleteMessage,
        ListMessages,
        MarkChatRead,
        SendImageMessage,
        SendTextMessage,
    )

log = logging.getLogger(__name__)

_WARNED_UNKNOWN_TYPES: set[str] = set()


class ChatState(StrEnum):
    """Server-side chat lifecycle returned by Avito on chat detail."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    BLOCKED = "blocked"


class MessageType(StrEnum):
    """All ``type`` values Avito has shipped on the messenger surface.

    Forward compat: new server-side types decode into :class:`UnknownMessage`
    and emit one WARNING per never-before-seen value (see :func:`_warn_unknown`).
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


class Participant(BaseModel):
    """One side of a chat (peer user id + optional display name)."""

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    user_id: int = Field(..., description="Avito numeric user id.")
    name: str | None = Field(default=None, description="Display name, when surfaced.")


class ItemRef(BaseModel):
    """Item context carried on a chat or an ``ItemMessage``."""

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    id: int = Field(..., description="Avito numeric item id.")
    title: str | None = Field(default=None, description="Listing title at time of chat.")
    price: Money | None = Field(default=None, description="Price snapshot.")
    url: HttpUrl | None = Field(default=None, description="Public listing URL.")


class TextContent(BaseModel):
    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")
    text: str = Field(..., description="UTF-8 message text.")


class ImageContent(BaseModel):
    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")
    image_id: str | None = Field(default=None, description="Avito-side image id.")
    sizes: dict[str, HttpUrl] = Field(
        default_factory=dict,
        description="Rendered URLs keyed by size label (e.g. ``140x105``).",
    )


class LinkContent(BaseModel):
    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")
    text: str | None = Field(default=None)
    url: HttpUrl = Field(..., description="Linked URL.")
    preview: dict[str, Any] = Field(default_factory=dict)


class LocationContent(BaseModel):
    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")
    lat: float = Field(...)
    lng: float = Field(...)
    title: str | None = Field(default=None)
    text: str | None = Field(default=None)


class VoiceContent(BaseModel):
    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")
    voice_id: str = Field(..., description="Identifier passed to ``GetVoiceFiles``.")


class CallContent(BaseModel):
    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")
    status: str | None = Field(default=None, description="Call status (e.g. ``missed``).")
    target_user_id: int | None = Field(default=None)


class FileContent(BaseModel):
    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")
    name: str | None = Field(default=None)
    size: int | None = Field(default=None, ge=0)
    url: HttpUrl | None = Field(default=None)


class SystemContent(BaseModel):
    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")
    text: str | None = Field(default=None)
    kind: str | None = Field(default=None)


class AppCallContent(BaseModel):
    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")
    call_id: str | None = Field(default=None)
    duration_s: int | None = Field(default=None, ge=0)


class _MessageBase(BoundModel):
    """Shared envelope every message variant carries (id, author, timestamps).

    Concrete subclasses pin ``type`` to a single literal so Pydantic's
    discriminated-union picks the right class. Bound actions (:meth:`reply`,
    :meth:`delete`) live here so every variant inherits them.
    """

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    id: str = Field(..., description="Avito message id (string, not int).")
    chat_id: str = Field(..., description="Owning chat id.")
    author_id: int = Field(..., description="Author user id.")
    created_at: datetime = Field(..., description="Server-side creation time (UTC).")

    def reply(self, text: str) -> SendTextMessage:
        """Build an awaitable text-reply method-class bound to this message's chat.

        The reply is always a :class:`SendTextMessage` regardless of the source
        variant (Avito has no protocol-level "reply to message" — it's a
        plain send into the same chat).

        Args:
            text: Reply body (1+ chars, ≤4096 by Avito's hard cap).

        Returns:
            ``SendTextMessage`` with the client pre-attached.

        Raises:
            ModelNotBoundError: when this message has no client (manually constructed).
        """

        from ..methods.messenger import SendTextMessage

        client = self._require_client()
        return SendTextMessage(
            user_id=_resolve_user_id(client),
            chat_id=self.chat_id,
            text=text,
        ).as_(client)

    def delete(self) -> DeleteMessage:
        """Build an awaitable delete method-class for this message.

        Returns:
            ``DeleteMessage`` with the client pre-attached.

        Raises:
            ModelNotBoundError: when this message has no client.
        """

        from ..methods.messenger import DeleteMessage

        client = self._require_client()
        return DeleteMessage(
            user_id=_resolve_user_id(client),
            chat_id=self.chat_id,
            message_id=self.id,
        ).as_(client)


class TextMessage(_MessageBase):
    type: Literal[MessageType.TEXT] = Field(default=MessageType.TEXT)
    content: TextContent


class ImageMessage(_MessageBase):
    type: Literal[MessageType.IMAGE] = Field(default=MessageType.IMAGE)
    content: ImageContent


class LinkMessage(_MessageBase):
    type: Literal[MessageType.LINK] = Field(default=MessageType.LINK)
    content: LinkContent


class ItemMessage(_MessageBase):
    type: Literal[MessageType.ITEM] = Field(default=MessageType.ITEM)
    content: ItemRef


class LocationMessage(_MessageBase):
    type: Literal[MessageType.LOCATION] = Field(default=MessageType.LOCATION)
    content: LocationContent


class VoiceMessage(_MessageBase):
    type: Literal[MessageType.VOICE] = Field(default=MessageType.VOICE)
    content: VoiceContent


class CallMessage(_MessageBase):
    type: Literal[MessageType.CALL] = Field(default=MessageType.CALL)
    content: CallContent


class FileMessage(_MessageBase):
    type: Literal[MessageType.FILE] = Field(default=MessageType.FILE)
    content: FileContent


class SystemMessage(_MessageBase):
    type: Literal[MessageType.SYSTEM] = Field(default=MessageType.SYSTEM)
    content: SystemContent


class AppCallMessage(_MessageBase):
    type: Literal[MessageType.APP_CALL] = Field(default=MessageType.APP_CALL)
    content: AppCallContent


class DeletedMessage(_MessageBase):
    type: Literal[MessageType.DELETED] = Field(default=MessageType.DELETED)
    content: dict[str, Any] = Field(default_factory=dict)


class UnknownMessage(_MessageBase):
    """Fallback variant for ``type`` values Avito ships after our last update.

    Decoding emits exactly one WARNING per unseen type (process-lifetime
    dedup). The raw ``type`` string is preserved under ``raw_type`` so
    callers can branch on it.
    """

    type: Literal[MessageType.UNKNOWN] = Field(default=MessageType.UNKNOWN)
    raw_type: str | None = Field(default=None, description="Original wire ``type`` value.")
    content: dict[str, Any] = Field(default_factory=dict)


Message = Annotated[
    TextMessage | ImageMessage | LinkMessage | ItemMessage | LocationMessage | VoiceMessage | CallMessage | FileMessage | SystemMessage | AppCallMessage | DeletedMessage | UnknownMessage,
    Field(discriminator="type"),
]


def _warn_unknown(raw_type: str) -> None:
    if raw_type in _WARNED_UNKNOWN_TYPES:
        return
    _WARNED_UNKNOWN_TYPES.add(raw_type)
    log.warning("messenger.unknown_message_type", extra={"raw_type": raw_type})


class MessageEnvelope(BoundModel):
    """Container that normalises arbitrary inbound payloads into a typed Message.

    The discriminated union itself cannot absorb unknown discriminator values,
    so this envelope pre-rewrites ``type`` to ``_unknown`` (and preserves the
    original under ``raw_type``) before delegating to the union validator.
    """

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    root: Message

    @model_validator(mode="before")
    @classmethod
    def _coerce(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        inner = value.get("root", value)
        if isinstance(inner, dict):
            inner = _normalise_unknown(inner)
        return {"root": inner}


def decode_message(payload: dict[str, Any]) -> Message:  # type: ignore[valid-type]
    """Validate one wire payload into the right :class:`Message` variant.

    Re-maps unknown ``type`` values to :class:`UnknownMessage` and emits one
    WARNING per first-seen value. The function is the single entry-point used
    by methods returning a single ``Message``.
    """

    normalised = _normalise_unknown(payload)
    return MessageEnvelope.model_validate({"root": normalised}).root


def _normalise_unknown(payload: dict[str, Any]) -> dict[str, Any]:
    raw_type = payload.get("type")
    if raw_type == MessageType.UNKNOWN.value or payload.get("raw_type") is not None:
        return payload
    known = {member.value for member in MessageType} - {MessageType.UNKNOWN.value}
    if isinstance(raw_type, str) and raw_type not in known:
        _warn_unknown(raw_type)
        return {**payload, "type": MessageType.UNKNOWN.value, "raw_type": raw_type}
    return payload


class Chat(BoundModel):
    """One messenger chat.

    Bound actions return awaitable method-class instances; callers ``await``
    them. Manual-constructed chats raise :class:`ModelNotBoundError` on action.
    """

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    id: str = Field(..., description="Avito chat id (string).")
    state: ChatState = Field(default=ChatState.ACTIVE, description="Lifecycle state.")
    participants: list[Participant] = Field(default_factory=list)
    item: ItemRef | None = Field(default=None, description="Item the chat is about.")
    last_message: Message | None = Field(default=None, description="Most recent message.")
    unread_count: int = Field(default=0, ge=0, description="Unread on the auth'd user's side.")

    @model_validator(mode="before")
    @classmethod
    def _normalise_last_message(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        last = value.get("last_message")
        if isinstance(last, dict):
            return {**value, "last_message": _normalise_unknown(last)}
        return value

    def send_text(self, text: str) -> SendTextMessage:
        """Build an awaitable text-send method-class bound to this chat."""

        from ..methods.messenger import SendTextMessage

        client = self._require_client()
        return SendTextMessage(
            user_id=_resolve_user_id(client),
            chat_id=self.id,
            text=text,
        ).as_(client)

    def send_image(self, image_id: str) -> SendImageMessage:
        """Build an awaitable image-send method-class bound to this chat.

        Args:
            image_id: Server-side id returned by :class:`UploadImage`.
        """

        from ..methods.messenger import SendImageMessage

        client = self._require_client()
        return SendImageMessage(
            user_id=_resolve_user_id(client),
            chat_id=self.id,
            image_id=image_id,
        ).as_(client)

    def mark_read(self) -> MarkChatRead:
        """Build an awaitable mark-read method-class for this chat."""

        from ..methods.messenger import MarkChatRead

        client = self._require_client()
        return MarkChatRead(
            user_id=_resolve_user_id(client),
            chat_id=self.id,
        ).as_(client)

    def list_messages(self, limit: int = 50, offset: int = 0) -> ListMessages:
        """Build an awaitable message-history method-class for this chat."""

        from ..methods.messenger import ListMessages

        client = self._require_client()
        return ListMessages(
            user_id=_resolve_user_id(client),
            chat_id=self.id,
            limit=limit,
            offset=offset,
        ).as_(client)


class ChatList(BoundModel):
    """Page of chats returned by ``GET /messenger/v2/.../chats``."""

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    chats: list[Chat] = Field(default_factory=list)


class MessageList(BoundModel):
    """Page of messages returned by ``GET /messenger/v3/.../messages``."""

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    messages: list[Message] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _normalise_messages(cls, value: Any) -> Any:
        if not isinstance(value, dict):
            return value
        raw = value.get("messages")
        if isinstance(raw, list):
            return {**value, "messages": [_normalise_unknown(m) if isinstance(m, dict) else m for m in raw]}
        return value


class BlacklistEntry(BaseModel):
    """One row in the blacklist endpoint response."""

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    user_id: int = Field(...)
    context: dict[str, Any] = Field(default_factory=dict)


class Blacklist(BoundModel):
    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    users: list[BlacklistEntry] = Field(default_factory=list)


class UploadImageResult(BaseModel):
    """Result of ``POST /messenger/v1/.../uploadImages``.

    Avito returns ``{"<random_key>": "<image_id>"}`` — one key, one id. The
    model collapses that to a flat ``image_id`` field via ``model_validator``.
    """

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    image_id: str = Field(..., description="Server-side id usable in send-image.")

    @model_validator(mode="before")
    @classmethod
    def _flatten(cls, value: Any) -> Any:
        if isinstance(value, dict) and "image_id" not in value and value:
            first = next(iter(value.values()))
            if isinstance(first, str):
                return {"image_id": first}
        return value


class VoiceFile(BaseModel):
    """One row in :class:`VoiceFiles` — voice id paired with its CDN URL."""

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    voice_id: str = Field(...)
    url: HttpUrl = Field(...)


class VoiceFiles(BoundModel):
    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    voices: list[VoiceFile] = Field(default_factory=list)


class DeleteResult(BoundModel):
    """Empty envelope returned by mutating endpoints that have no body."""

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    success: bool = Field(default=True)


def _resolve_user_id(client: Any) -> int:
    user_id = getattr(client.config, "user_id", None)
    if user_id is None:
        raise ValueError(
            "Avito messenger endpoints require config.user_id; set it on ClientConfig.",
        )
    return int(user_id)


class WebhookActionResult(BoundModel):
    """Result envelope for ``POST /messenger/v3/webhook`` and unsubscribe.

    Avito returns a thin acknowledgement; ``message`` carries the
    server-side reason on partial-success rollouts.
    """

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    success: bool = Field(default=True, description="True on 2xx.")
    message: str | None = Field(default=None, description="Optional server message.")


class Subscription(BaseModel):
    """One row from ``POST /messenger/v1/subscriptions``."""

    model_config = ConfigDict(populate_by_name=True, strict=False, extra="allow")

    url: HttpUrl = Field(..., description="Registered callback URL.")
    callback_id: str | None = Field(
        default=None,
        alias="callbackId",
        description="Server-side subscription id (forward-compat field).",
    )
    version: str | None = Field(
        default=None,
        description="API surface version this subscription is bound to (``v1`` / ``v3``).",
    )


class SubscriptionList(RootModel[list[Subscription]]):
    """Top-level array envelope for active-subscriptions responses."""

    root: list[Subscription] = Field(default_factory=list)

    def __iter__(self) -> object:  # type: ignore[override]
        return iter(self.root)

    def __len__(self) -> int:
        return len(self.root)

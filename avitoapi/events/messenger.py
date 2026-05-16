"""Messenger domain events.

Each event carries the originating ``account_id`` so multi-account
dispatchers can route to per-account handlers. ``NewMessage.message`` is
typed as the :data:`avitoapi.models.messenger.Message` discriminated union
so handlers get full IDE completion + type narrowing on ``message.type``.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from ..models.messenger import Message

try:
    import evented as _evented

    _BASE: type = _evented.Event
except ImportError:  # pragma: no cover — exercised via the fallback path

    class _BASE:  # type: ignore[no-redef]
        """Fallback Event base when ``evented`` is not installed.

        Minimal: declares the ``event_name`` class kwarg pattern via
        ``__init_subclass__`` so handlers can dispatch by name.
        """

        event_name: ClassVar[str] = ""

        def __init_subclass__(cls, **kwargs: Any) -> None:
            event_name = kwargs.pop("event_name", None)
            super().__init_subclass__(**kwargs)
            if event_name is not None:
                cls.event_name = event_name


if TYPE_CHECKING:
    BaseEvent = _BASE
else:
    BaseEvent = _BASE


class MessengerEvent(BaseEvent, event_name="messenger"):  # type: ignore[call-arg,misc]
    """Common ancestor of every messenger-domain event."""

    account_id: str
    chat_id: str

    def __init__(self, *, account_id: str, chat_id: str, **kwargs: Any) -> None:
        self.account_id = account_id
        self.chat_id = chat_id
        for k, v in kwargs.items():
            setattr(self, k, v)


class NewMessage(MessengerEvent, event_name="messenger.new_message"):  # type: ignore[call-arg,misc]
    """A new inbound message landed in one of the bot's chats."""

    message: Message

    def __init__(self, *, account_id: str, chat_id: str, message: Message) -> None:
        super().__init__(account_id=account_id, chat_id=chat_id)
        self.message = message


class MessageRead(MessengerEvent, event_name="messenger.message_read"):  # type: ignore[call-arg,misc]
    """The counterparty marked a message as read."""

    message_id: str

    def __init__(self, *, account_id: str, chat_id: str, message_id: str) -> None:
        super().__init__(account_id=account_id, chat_id=chat_id)
        self.message_id = message_id


class ChatArchived(MessengerEvent, event_name="messenger.chat_archived"):  # type: ignore[call-arg,misc]
    """A chat was archived (by the user or by the system)."""

    def __init__(self, *, account_id: str, chat_id: str) -> None:
        super().__init__(account_id=account_id, chat_id=chat_id)

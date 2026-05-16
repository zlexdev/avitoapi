"""TTL-bounded dedup on ``(chat_id, message_id)`` for webhook replays."""
from __future__ import annotations

from datetime import timedelta
from typing import Any

from ...storage.base import BaseStorage


class WebhookIdempotencyMiddleware:
    """Mark and check ``(chat_id, message_id)`` pairs as seen.

    Backed by any :class:`BaseStorage`. On replay the consumer should call
    ``await mw.seen(...)`` first and skip the handler if it returns ``True``.
    """

    def __init__(
        self,
        storage: BaseStorage[Any, str],
        *,
        ttl: timedelta = timedelta(hours=1),
    ) -> None:
        self._storage = storage.namespaced("webhook_seen")
        self._ttl = ttl

    @staticmethod
    def _key(chat_id: str, message_id: str) -> str:
        return f"{chat_id}:{message_id}"

    async def seen(self, chat_id: str, message_id: str) -> bool:
        """Probe + record. Returns ``True`` if the pair was already known."""
        key = self._key(chat_id, message_id)
        if await self._storage.exists(key):
            return True
        await self._storage.put(key, 1, ttl=self._ttl)
        return False

    async def forget(self, chat_id: str, message_id: str) -> None:
        """Drop the dedup record. Useful in tests."""
        await self._storage.delete(self._key(chat_id, message_id))

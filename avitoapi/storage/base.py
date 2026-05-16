"""Generic async key/value storage contract used everywhere (tokens, FSM, idempotency)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any, Generic, TypeVar

TDoc = TypeVar("TDoc")
TId = TypeVar("TId")


class BaseStorage(ABC, Generic[TDoc, TId]):
    """Abstract async K/V store. Values must be JSON-serialisable.

    Type parameters describe the *typical* shape of stored documents and keys for a
    given namespace, but the runtime contract is just JSON-friendly. The TTL argument
    is best-effort — backends without native TTL store the expiry inline and prune
    on read.
    """

    namespace: str = ""

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """Return the JSON-decoded value or ``None`` if absent or expired."""

    @abstractmethod
    async def put(
        self,
        key: str,
        value: Any,
        *,
        ttl: timedelta | None = None,
    ) -> None:
        """Store the value, JSON-encoding it. ``ttl=None`` means persist indefinitely."""

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Remove the key. No-op when absent."""

    async def exists(self, key: str) -> bool:
        """Cheap probe — defaults to ``get(...) is not None`` for backends without EXISTS."""

        return await self.get(key) is not None

    async def health(self) -> bool:
        """Round-trip a sentinel key. Override for backends with a cheaper liveness probe."""

        sentinel = f"__health__:{id(self)}"
        try:
            await self.put(sentinel, 1, ttl=timedelta(seconds=5))
            value = await self.get(sentinel)
            await self.delete(sentinel)
        except Exception:
            return False
        return value == 1

    async def close(self) -> None:
        """Release resources. Idempotent."""

    @abstractmethod
    def namespaced(self, namespace: str) -> BaseStorage[TDoc, TId]:
        """Return a view of this storage that transparently prefixes every key.

        ``parent.namespaced("acc:1").get("token")`` ⇔ ``parent.get("acc:1:token")``.
        Implementations must compose: ``ns("a").ns("b")`` keys land as ``a:b:<k>``.
        """

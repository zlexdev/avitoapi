"""``FileStorage`` ABC — binary K/V parallel to :class:`BaseStorage`.

``BaseStorage`` is JSON-serialisable values only; bytes can't pass through
``json.dumps``. ``FileStorage`` is the bytes-shaped sibling: backends differ
in *where* the bytes live (memory dict, sha256-named files on disk, S3,
Redis bytes).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import timedelta


class FileStorage(ABC):
    """Abstract async binary K/V store.

    The TTL argument is best-effort — backends without native TTL store the
    expiry inline and prune on read.
    """

    namespace: str = ""

    @abstractmethod
    async def get(self, key: str) -> bytes | None:
        """Return the cached bytes or ``None`` if absent or expired."""

    @abstractmethod
    async def put(
        self,
        key: str,
        data: bytes,
        *,
        ttl: timedelta | None = None,
    ) -> None:
        """Store ``data``. ``ttl=None`` persists indefinitely (until eviction)."""

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Remove the key. No-op when absent."""

    @abstractmethod
    def namespaced(self, name: str) -> FileStorage:
        """Return a view of this storage that transparently prefixes every key."""

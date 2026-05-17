"""TTL wrapper over :class:`FileStorage`.

The wrapper enforces a single uniform TTL across every ``put``. Useful when
the underlying storage doesn't speak TTLs natively (e.g. naive S3 bucket
without a lifecycle rule) or when callers want a coarser cache horizon than
per-call decisions.
"""

from __future__ import annotations

from datetime import timedelta

from .file_storage.base import FileStorage


class FileCache:
    """Wrap a :class:`FileStorage` and force every ``put`` to carry ``ttl``."""

    def __init__(self, storage: FileStorage, ttl: timedelta) -> None:
        self.storage = storage
        self.ttl = ttl

    async def get(self, key: str) -> bytes | None:
        """Return cached bytes, ``None`` on miss / expiry."""

        return await self.storage.get(key)

    async def put(self, key: str, data: bytes) -> None:
        """Store ``data`` with the configured TTL (overriding caller's choice)."""

        await self.storage.put(key, data, ttl=self.ttl)

    async def delete(self, key: str) -> None:
        await self.storage.delete(key)

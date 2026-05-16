"""In-process :class:`FileStorage` backed by a dict."""
from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from datetime import timedelta

from .base import FileStorage


@dataclass(slots=True)
class _Entry:
    data: bytes
    expires_at: float | None


class MemoryFileStorage(FileStorage):
    """Thread-safe (asyncio.Lock) in-process binary K/V.

    No LRU bound — long-lived processes should wrap with :class:`FileCache`
    and rely on TTL expiry, or run with bounded request volume.
    """

    def __init__(
        self,
        *,
        namespace: str = "",
        _data: dict[str, _Entry] | None = None,
        _lock: asyncio.Lock | None = None,
    ) -> None:
        self.namespace = namespace
        self._data: dict[str, _Entry] = _data if _data is not None else {}
        self._lock: asyncio.Lock = _lock if _lock is not None else asyncio.Lock()

    def _full(self, key: str) -> str:
        return f"{self.namespace}:{key}" if self.namespace else key

    async def get(self, key: str) -> bytes | None:
        full = self._full(key)
        async with self._lock:
            entry = self._data.get(full)
            if entry is None:
                return None
            if entry.expires_at is not None and entry.expires_at < time.monotonic():
                self._data.pop(full, None)
                return None
            return entry.data

    async def put(
        self,
        key: str,
        data: bytes,
        *,
        ttl: timedelta | None = None,
    ) -> None:
        full = self._full(key)
        expires_at = time.monotonic() + ttl.total_seconds() if ttl is not None else None
        async with self._lock:
            self._data[full] = _Entry(data=data, expires_at=expires_at)

    async def delete(self, key: str) -> None:
        full = self._full(key)
        async with self._lock:
            self._data.pop(full, None)

    def namespaced(self, name: str) -> MemoryFileStorage:
        joined = f"{self.namespace}:{name}" if self.namespace else name
        return MemoryFileStorage(namespace=joined, _data=self._data, _lock=self._lock)

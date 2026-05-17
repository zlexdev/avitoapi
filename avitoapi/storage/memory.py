"""In-process :class:`BaseStorage` backed by a dict. Default for tests and single-process apps."""

from __future__ import annotations

import asyncio
import copy
import time
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from .base import BaseStorage


@dataclass(slots=True)
class _Entry:
    value: Any
    expires_at: float | None


class MemoryStorage(BaseStorage[Any, str]):
    """Thread-safe (asyncio.Lock) in-process K/V. Deep-copies on read and write.

    The deep-copy is intentional: it prevents the "caller mutates a dict still
    held in storage" bug class. Slightly slower than naive dict storage; cheap
    relative to anything that crosses a network.
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

    def _full_key(self, key: str) -> str:
        return f"{self.namespace}:{key}" if self.namespace else key

    async def get(self, key: str) -> Any | None:
        full = self._full_key(key)
        async with self._lock:
            entry = self._data.get(full)
            if entry is None:
                return None
            if entry.expires_at is not None and entry.expires_at < time.monotonic():
                self._data.pop(full, None)
                return None
            return copy.deepcopy(entry.value)

    async def put(
        self,
        key: str,
        value: Any,
        *,
        ttl: timedelta | None = None,
    ) -> None:
        full = self._full_key(key)
        expires_at = time.monotonic() + ttl.total_seconds() if ttl is not None else None
        async with self._lock:
            self._data[full] = _Entry(value=copy.deepcopy(value), expires_at=expires_at)

    async def delete(self, key: str) -> None:
        full = self._full_key(key)
        async with self._lock:
            self._data.pop(full, None)

    def namespaced(self, namespace: str) -> MemoryStorage:
        joined = f"{self.namespace}:{namespace}" if self.namespace else namespace
        return MemoryStorage(namespace=joined, _data=self._data, _lock=self._lock)

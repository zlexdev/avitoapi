"""Disk-backed :class:`FileStorage`. Filenames are sha256(key); metadata sidecar."""
from __future__ import annotations

import asyncio
import hashlib
import json
import time
from datetime import timedelta
from pathlib import Path

from .base import FileStorage


class LocalFileStorage(FileStorage):
    """Bytes live in ``root / sha256(key)``; expiry + original key in ``<file>.meta``.

    The sha256 hashing keeps filenames filesystem-safe regardless of what
    callers pass as keys (URLs, opaque ids, paths). The ``.meta`` sidecar is
    JSON so it's grep-able for debugging.
    """

    def __init__(
        self,
        root: Path,
        *,
        namespace: str = "",
    ) -> None:
        self.root = Path(root)
        self.namespace = namespace
        self._lock: asyncio.Lock = asyncio.Lock()
        self.root.mkdir(parents=True, exist_ok=True)

    def _full(self, key: str) -> str:
        return f"{self.namespace}:{key}" if self.namespace else key

    def _path(self, key: str) -> Path:
        digest = hashlib.sha256(self._full(key).encode()).hexdigest()
        return self.root / digest

    def _meta_path(self, key: str) -> Path:
        return self._path(key).with_suffix(".meta")

    async def get(self, key: str) -> bytes | None:
        path = self._path(key)
        meta_path = self._meta_path(key)
        async with self._lock:
            if not path.exists():
                return None
            if meta_path.exists():
                try:
                    meta = json.loads(meta_path.read_text(encoding="utf-8"))
                    expires_at = meta.get("expires_at")
                    if expires_at is not None and expires_at < time.time():
                        path.unlink(missing_ok=True)
                        meta_path.unlink(missing_ok=True)
                        return None
                except (json.JSONDecodeError, OSError):
                    return None
            return path.read_bytes()

    async def put(
        self,
        key: str,
        data: bytes,
        *,
        ttl: timedelta | None = None,
    ) -> None:
        path = self._path(key)
        meta_path = self._meta_path(key)
        expires_at = time.time() + ttl.total_seconds() if ttl is not None else None
        meta = {"key": self._full(key), "expires_at": expires_at}
        async with self._lock:
            path.write_bytes(data)
            meta_path.write_text(json.dumps(meta), encoding="utf-8")

    async def delete(self, key: str) -> None:
        path = self._path(key)
        meta_path = self._meta_path(key)
        async with self._lock:
            path.unlink(missing_ok=True)
            meta_path.unlink(missing_ok=True)

    def namespaced(self, name: str) -> LocalFileStorage:
        joined = f"{self.namespace}:{name}" if self.namespace else name
        return LocalFileStorage(root=self.root, namespace=joined)

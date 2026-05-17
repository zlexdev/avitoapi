"""``AssetDownloader`` — bounded-concurrency CDN fetch with caching."""

from __future__ import annotations

import asyncio
import hashlib
from typing import TYPE_CHECKING, Any

from .file_storage.base import FileStorage

if TYPE_CHECKING:
    pass


class AssetDownloader:
    """Fetch image / voice / file URLs returned by the Avito API.

    Cache key = ``sha256(url)`` so identical URLs short-circuit the network.
    Concurrency is bounded by an :class:`asyncio.Semaphore` (``max_concurrent``)
    so a single ``download_many`` of 500 voice files doesn't open 500 sockets.

    The downloader is HTTP-client-agnostic: an ``httpx.AsyncClient`` ducktype
    (``await http.get(url) -> response with .content``) is enough. Pass any
    object that satisfies that.
    """

    def __init__(
        self,
        *,
        http: Any,
        file_storage: FileStorage,
        max_concurrent: int = 5,
    ) -> None:
        self.http = http
        self.file_storage = file_storage
        self.max_concurrent: int = max(1, max_concurrent)
        self._semaphore: asyncio.Semaphore = asyncio.Semaphore(self.max_concurrent)

    async def download(self, url: str) -> bytes:
        """Fetch one URL; serve from cache when warm.

        Raises:
            RuntimeError: when the HTTP backend returned a non-2xx status.
        """

        key = self._cache_key(url)
        cached = await self.file_storage.get(key)
        if cached is not None:
            return cached

        async with self._semaphore:
            data = await self._fetch(url)
        await self.file_storage.put(key, data)
        return data

    async def download_many(self, urls: list[str]) -> dict[str, bytes]:
        """Fetch many URLs in parallel under the configured concurrency bound.

        Returns a ``{url: bytes}`` dict in the order URLs were passed. Failures
        propagate — wrap individual ``download`` calls if partial success is
        wanted.
        """

        if not urls:
            return {}

        async def _one(url: str) -> tuple[str, bytes]:
            data = await self.download(url)
            return url, data

        pairs = await asyncio.gather(*(_one(u) for u in urls))
        return dict(pairs)

    async def _fetch(self, url: str) -> bytes:
        response = await self.http.get(url)
        status = getattr(response, "status_code", None)
        if status is not None and not (200 <= status < 300):
            raise RuntimeError(f"asset fetch failed: status={status} url={url}")
        content = getattr(response, "content", None)
        if isinstance(content, bytes):
            return content
        if isinstance(content, (bytearray, memoryview)):
            return bytes(content)
        if isinstance(content, str):
            return content.encode()
        raise RuntimeError(
            f"asset fetch returned unrecognised content type: {type(content).__name__}"
        )

    @staticmethod
    def _cache_key(url: str) -> str:
        return hashlib.sha256(url.encode()).hexdigest()

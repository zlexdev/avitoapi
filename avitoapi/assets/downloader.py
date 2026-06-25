"""``AssetDownloader`` — bounded-concurrency CDN fetch with caching and size guard."""

from __future__ import annotations

import asyncio
import hashlib
from typing import TYPE_CHECKING, Any  # typed-Any: http session duck type

from ..exceptions import AssetTooLargeError
from .file_storage.base import FileStorage

if TYPE_CHECKING:
    pass

# 50 MB — large enough for any Avito image/voice, small enough to prevent
# memory bombs from malformed CDN responses.
_DEFAULT_MAX_BYTES: int = 50 * 1024 * 1024


class AssetDownloader:
    """Fetch image / voice / file URLs returned by the Avito API.

    Cache key = ``sha256(url)`` so identical URLs short-circuit the network.
    Concurrency is bounded by an :class:`asyncio.Semaphore` (``max_concurrent``)
    so a single ``download_many`` of 500 voice files doesn't open 500 sockets.

    The downloader is HTTP-client-agnostic: an ``httpx.AsyncClient`` ducktype
    (``await http.get(url) -> response with .content``) is enough. Pass any
    object that satisfies that.

    Args:
        http: HTTP client duck-typed to ``await http.get(url)``.
        file_storage: Backing cache store.
        max_concurrent: Max in-flight requests at once.
        max_bytes: Reject any asset larger than this byte count. Checked from
            ``Content-Length`` before downloading and from the actual payload
            after. Defaults to 50 MB.

    Raises:
        AssetTooLargeError: The remote asset exceeds *max_bytes*.
    """

    def __init__(
        self,
        *,
        http: Any,
        file_storage: FileStorage,
        max_concurrent: int = 5,
        max_bytes: int = _DEFAULT_MAX_BYTES,
    ) -> None:
        self.http = http
        self.file_storage = file_storage
        self.max_concurrent: int = max(1, max_concurrent)
        self.max_bytes: int = max(1, max_bytes)
        self._semaphore: asyncio.Semaphore = asyncio.Semaphore(self.max_concurrent)

    async def download(self, url: str) -> bytes:
        """Fetch one URL; serve from cache when warm.

        Raises:
            AssetTooLargeError: Asset exceeds :attr:`max_bytes`.
            RuntimeError: HTTP backend returned a non-2xx status.
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

        Raises:
            AssetTooLargeError: Any asset exceeds :attr:`max_bytes`.
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

        # Early size guard via Content-Length — abort before reading the body.
        raw_headers: Any = getattr(response, "headers", {})  # typed-Any: duck-typed headers mapping
        cl_raw: str | None = (
            raw_headers.get("content-length") or raw_headers.get("Content-Length")
        )
        if cl_raw is not None:
            try:
                reported = int(cl_raw)
                if reported > self.max_bytes:
                    raise AssetTooLargeError(url=url, limit=self.max_bytes, reported=reported)
            except ValueError:
                pass  # malformed header — fall through to payload check

        status = getattr(response, "status_code", None)
        if status is not None and not (200 <= status < 300):
            raise RuntimeError(f"asset fetch failed: status={status} url={url}")

        content = getattr(response, "content", None)
        if isinstance(content, bytes):
            data = content
        elif isinstance(content, bytearray | memoryview):
            data = bytes(content)
        elif isinstance(content, str):
            data = content.encode()
        else:
            raise RuntimeError(
                f"asset fetch returned unrecognised content type: {type(content).__name__}"
            )

        # Payload size guard — catches chunked/streaming responses not covered by
        # Content-Length, and Content-Length lies.
        if len(data) > self.max_bytes:
            raise AssetTooLargeError(url=url, limit=self.max_bytes, reported=len(data))

        return data

    @staticmethod
    def _cache_key(url: str) -> str:
        return hashlib.sha256(url.encode()).hexdigest()

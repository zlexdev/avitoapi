"""Unit tests for the :mod:`avitoapi.assets` subsystem.

Covers:

- :class:`MemoryFileStorage` and :class:`LocalFileStorage` round-trip
  (put / get / delete / namespaced).
- :class:`FileCache` TTL enforcement.
- :class:`AssetDownloader` cache-hit behaviour (second call → zero new
  fetches) and bounded concurrency via ``download_many``.
"""
from __future__ import annotations

import asyncio
from datetime import timedelta
from pathlib import Path
from typing import Any

import pytest
from avitoapi.assets import (
    AssetDownloader,
    FileCache,
    LocalFileStorage,
    MemoryFileStorage,
)

# ---- MemoryFileStorage -----------------------------------------------------


async def test_memory_file_storage_put_get_round_trip() -> None:
    storage = MemoryFileStorage()
    await storage.put("k1", b"hello")
    assert await storage.get("k1") == b"hello"


async def test_memory_file_storage_get_missing_returns_none() -> None:
    storage = MemoryFileStorage()
    assert await storage.get("missing") is None


async def test_memory_file_storage_delete() -> None:
    storage = MemoryFileStorage()
    await storage.put("k1", b"data")
    await storage.delete("k1")
    assert await storage.get("k1") is None


async def test_memory_file_storage_ttl_expiry() -> None:
    storage = MemoryFileStorage()
    await storage.put("k1", b"data", ttl=timedelta(milliseconds=10))
    await asyncio.sleep(0.05)
    assert await storage.get("k1") is None


async def test_memory_file_storage_namespaced_isolates() -> None:
    storage = MemoryFileStorage()
    ns = storage.namespaced("imgs")
    await ns.put("a", b"x")

    assert await ns.get("a") == b"x"
    assert await storage.get("a") is None
    assert await storage.get("imgs:a") == b"x"


# ---- LocalFileStorage ------------------------------------------------------


async def test_local_file_storage_put_get_round_trip(tmp_path: Path) -> None:
    storage = LocalFileStorage(root=tmp_path)
    await storage.put("k1", b"on-disk-bytes")
    assert await storage.get("k1") == b"on-disk-bytes"


async def test_local_file_storage_delete(tmp_path: Path) -> None:
    storage = LocalFileStorage(root=tmp_path)
    await storage.put("k1", b"data")
    await storage.delete("k1")
    assert await storage.get("k1") is None


async def test_local_file_storage_ttl_expiry(tmp_path: Path) -> None:
    storage = LocalFileStorage(root=tmp_path)
    await storage.put("k1", b"data", ttl=timedelta(milliseconds=10))
    await asyncio.sleep(0.05)
    assert await storage.get("k1") is None


async def test_local_file_storage_filenames_are_sha256_hashed(tmp_path: Path) -> None:
    storage = LocalFileStorage(root=tmp_path)
    await storage.put("some/url?with=special&chars", b"x")
    files = list(tmp_path.iterdir())
    assert files, "expected at least one file written"
    for f in files:
        if f.suffix == ".meta":
            continue
        assert len(f.name) == 64
        int(f.name, 16)


# ---- FileCache -------------------------------------------------------------


async def test_file_cache_enforces_uniform_ttl() -> None:
    storage = MemoryFileStorage()
    cache = FileCache(storage=storage, ttl=timedelta(milliseconds=20))

    await cache.put("k", b"v")
    assert await cache.get("k") == b"v"
    await asyncio.sleep(0.05)
    assert await cache.get("k") is None


async def test_file_cache_delegates_delete_to_storage() -> None:
    storage = MemoryFileStorage()
    cache = FileCache(storage=storage, ttl=timedelta(seconds=60))
    await cache.put("k", b"v")
    await cache.delete("k")
    assert await cache.get("k") is None


# ---- AssetDownloader -------------------------------------------------------


class _FakeHttp:
    """Minimal ducktype: one ``get`` returning an object with ``status_code`` + ``content``."""

    def __init__(self, payloads: dict[str, bytes]) -> None:
        self.payloads = payloads
        self.calls: list[str] = []

    async def get(self, url: str) -> Any:
        self.calls.append(url)

        class _Response:
            def __init__(self, content: bytes) -> None:
                self.status_code = 200
                self.content = content

        return _Response(self.payloads[url])


async def test_asset_downloader_caches_after_first_fetch() -> None:
    storage = MemoryFileStorage()
    http = _FakeHttp({"https://cdn/img.jpg": b"BINARY"})
    downloader = AssetDownloader(http=http, file_storage=storage)

    first = await downloader.download("https://cdn/img.jpg")
    second = await downloader.download("https://cdn/img.jpg")

    assert first == second == b"BINARY"
    assert len(http.calls) == 1


async def test_asset_downloader_download_many_returns_dict() -> None:
    storage = MemoryFileStorage()
    payloads = {f"https://cdn/{i}.bin": f"x{i}".encode() for i in range(5)}
    http = _FakeHttp(payloads)
    downloader = AssetDownloader(http=http, file_storage=storage, max_concurrent=2)

    result = await downloader.download_many(list(payloads.keys()))

    assert set(result.keys()) == set(payloads.keys())
    for url, blob in payloads.items():
        assert result[url] == blob


async def test_asset_downloader_download_many_empty_returns_empty() -> None:
    storage = MemoryFileStorage()
    http = _FakeHttp({})
    downloader = AssetDownloader(http=http, file_storage=storage)

    result = await downloader.download_many([])

    assert result == {}


async def test_asset_downloader_propagates_non_2xx_status() -> None:
    class _BadHttp:
        async def get(self, url: str) -> Any:
            class _Response:
                status_code = 500
                content = b""

            return _Response()

    storage = MemoryFileStorage()
    downloader = AssetDownloader(http=_BadHttp(), file_storage=storage)

    with pytest.raises(RuntimeError, match="status=500"):
        await downloader.download("https://cdn/broken")

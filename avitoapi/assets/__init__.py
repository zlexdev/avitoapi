"""Asset (image / voice) download and caching subsystem.

The package ships an :class:`AssetDownloader` for bounded-concurrency CDN
fetches and a tiny binary K/V abstraction (:class:`FileStorage`) so cached
bytes can live in process memory, on disk, or — later — in S3 / Redis.
"""
from __future__ import annotations

from .downloader import AssetDownloader
from .file_cache import FileCache
from .file_storage.base import FileStorage
from .file_storage.local import LocalFileStorage
from .file_storage.memory import MemoryFileStorage

__all__ = [
    "AssetDownloader",
    "FileCache",
    "FileStorage",
    "LocalFileStorage",
    "MemoryFileStorage",
]

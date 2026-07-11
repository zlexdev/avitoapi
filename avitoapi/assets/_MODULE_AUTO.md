# assets/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

> Asset (image / voice) download and caching subsystem.

## Submodules

- [`file_storage/`](file_storage\_MODULE_AUTO.md) — Binary K/V storage backends for downloaded assets. (3 py, 4 cls)

## __init__.py
```
# Asset (image / voice) download and caching subsystem.


```

## downloader.py
```
# ``AssetDownloader`` — bounded-concurrency CDN fetch with caching and size guard.


cls AssetDownloader
  __init__() -> None
  async download(url: str) -> bytes
  async download_many(urls: list[str) -> dict[str, bytes]

```

## file_cache.py
```
# TTL wrapper over :class:`FileStorage`.


cls FileCache
  # Wrap a :class:`FileStorage` and force every ``put`` to carry ``ttl``.
  __init__(storage: FileStorage, ttl: timedelta) -> None
  async get(key: str) -> bytes | None
    # Return cached bytes, ``None`` on miss / expiry.
  async put(key: str, data: bytes) -> None
    # Store ``data`` with the configured TTL (overriding caller's choice).
  async delete(key: str) -> None

```

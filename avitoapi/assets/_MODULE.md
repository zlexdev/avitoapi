# avitoapi.assets

CDN fetch + caching subsystem for image / voice / file URLs the Avito
messenger surface returns.

## Surface

- `AssetDownloader(http, file_storage, max_concurrent=5)`
  - `await downloader.download(url) -> bytes` — single fetch; cache
    hit short-circuits the network. Cache key = `sha256(url)`.
  - `await downloader.download_many(urls) -> dict[str, bytes]` —
    bounded `asyncio.gather` (semaphore size = `max_concurrent`).
    **Failures propagate**; wrap per-URL for partial success.
- `FileStorage` (ABC) — binary K/V (`get` / `put` / `delete` /
  `namespaced`).
- `MemoryFileStorage` — process-local dict. No LRU bound; combine
  with `FileCache` for TTL eviction in long-lived workers.
- `LocalFileStorage(root)` — filenames are `sha256(key)`; original
  key + expiry in a `.meta` sidecar JSON.
- `FileCache(storage, ttl)` — wrapper that forces a uniform TTL on
  every `put`. Reads delegate (storage decides if entry is fresh).

## Why a separate `FileStorage` (not reusing `BaseStorage`)

`BaseStorage` is JSON-serialisable values only. Bytes can't pass
through `json.dumps`. Two options:

1. Hack `bytes → base64-string` into `BaseStorage` (pollutes the
   abstraction; every key now pays a JSON round-trip even when the
   backend supports raw bytes).
2. Admit that bytes have a different shape and give them their own
   ABC. This package picks the second — `FileStorage` is bytes-only,
   `BaseStorage` is JSON-only, neither pretends to be the other.

## Gotchas

- `LocalFileStorage` keys are sha256-hashed for filenames. The
  original key lives in the `.meta` sidecar — grep there to find
  what a file represents.
- `FileCache.get` returns `None` when the underlying storage's
  metadata is unreadable — treats as cache miss rather than
  fail-loud.
- `MemoryFileStorage` is unbounded. For long-lived workers wrap it in
  a `FileCache` with a short TTL or eyeball memory growth.

## HTTP backend

`AssetDownloader` is HTTP-client-agnostic — it ducktypes the `http`
arg as having `async def get(url) -> response with .content`. Pass
`httpx.AsyncClient`, `curl_cffi.AsyncSession`, or a custom shim. The
fetch raises `RuntimeError` on non-2xx status; callers wrap if they
need exception subclasses.

## Don't

- Don't write text/JSON via `FileStorage`. Use the JSON
  `avitoapi.storage` package for structured values.
- Don't enable `FileCache` over `MemoryFileStorage` without TTL on
  long-running processes — both grow until restart.

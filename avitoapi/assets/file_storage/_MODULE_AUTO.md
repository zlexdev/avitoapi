# file_storage/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

> Binary K/V storage backends for downloaded assets.

## base.py
```
# ``FileStorage`` ABC — binary K/V parallel to :class:`BaseStorage`.


cls FileStorage(ABC)
  async get(key: str) -> bytes | None
    # Return the cached bytes or ``None`` if absent or expired.
  async put(key: str, data: bytes) -> None
    # Store ``data``. ``ttl=None`` persists indefinitely (until eviction).
  async delete(key: str) -> None
    # Remove the key. No-op when absent.
  namespaced(name: str) -> FileStorage
    # Return a view of this storage that transparently prefixes every key.

```

## local.py
```
# Disk-backed :class:`FileStorage`. Filenames are sha256(key); metadata sidecar.


cls LocalFileStorage(FileStorage)
  __init__(root: Path) -> None
  async get(key: str) -> bytes | None
  async put(key: str, data: bytes) -> None
  async delete(key: str) -> None
  namespaced(name: str) -> LocalFileStorage

```

## memory.py
```
# In-process :class:`FileStorage` backed by a dict.


cls _Entry: data: bytes, expires_at: float | None

cls MemoryFileStorage(FileStorage)
  __init__() -> None
  async get(key: str) -> bytes | None
  async put(key: str, data: bytes) -> None
  async delete(key: str) -> None
  namespaced(name: str) -> MemoryFileStorage

```

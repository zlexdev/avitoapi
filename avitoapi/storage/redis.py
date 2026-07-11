"""``RedisStorage`` — :class:`BaseStorage` over ``redis.asyncio`` (lazy import)."""

from __future__ import annotations

import json
from datetime import timedelta
from typing import TYPE_CHECKING

from .base import BaseStorage

if TYPE_CHECKING:
    from redis.asyncio import Redis


class RedisStorage(BaseStorage[object, str]):
    """Async-Redis-backed K/V. Lazy-imports :mod:`redis.asyncio`.

    Install via ``pip install avitoapi[redis]``. JSON-serialises values with
    ``default=str`` so :class:`~decimal.Decimal`, :class:`~datetime.datetime`,
    and :class:`~uuid.UUID` round-trip without explicit converters. TTL maps
    onto Redis ``PEXPIRE``.
    """

    def __init__(
        self,
        client: Redis | None = None,
        *,
        url: str | None = None,
        namespace: str = "",
        owns_client: bool | None = None,
    ) -> None:
        if client is None and url is None:
            raise ValueError("RedisStorage: pass either `client` or `url`")
        self._client_external: Redis | None = client
        self._url = url
        self.namespace = namespace
        self._owns_client = bool(owns_client) if owns_client is not None else client is None
        self._resolved: Redis | None = client

    def _full_key(self, key: str) -> str:
        return f"{self.namespace}:{key}" if self.namespace else key

    def _redis(self) -> Redis:
        if self._resolved is not None:
            return self._resolved
        try:
            from redis.asyncio import Redis as _Redis
        except ImportError as exc:
            raise ImportError(
                "install avitoapi[redis] to use RedisStorage (missing redis.asyncio)",
            ) from exc
        if self._url is None:
            raise RuntimeError("RedisStorage: no URL and no client provided")
        self._resolved = _Redis.from_url(self._url, decode_responses=False)
        return self._resolved

    async def get(self, key: str) -> object | None:
        raw = await self._redis().get(self._full_key(key))
        if raw is None:
            return None
        if isinstance(raw, bytes | bytearray):
            raw = raw.decode("utf-8")
        try:
            return json.loads(raw)  # type: ignore[no-any-return]  # json.loads stubs return Any
        except json.JSONDecodeError:
            return raw  # type: ignore[no-any-return]  # redis stubs type get() as Any

    async def put(
        self,
        key: str,
        value: object,
        *,
        ttl: timedelta | None = None,
    ) -> None:
        payload = json.dumps(value, default=str, ensure_ascii=False)
        full = self._full_key(key)
        if ttl is None:
            await self._redis().set(full, payload)
        else:
            await self._redis().set(full, payload, px=int(ttl.total_seconds() * 1000))

    async def add(self, key: str, value: object, *, ttl: timedelta | None = None) -> bool:
        """Atomic set-if-absent via native ``SET ... NX`` — cross-process safe."""

        payload = json.dumps(value, default=str, ensure_ascii=False)
        full = self._full_key(key)
        if ttl is None:
            result = await self._redis().set(full, payload, nx=True)
        else:
            result = await self._redis().set(
                full,
                payload,
                px=int(ttl.total_seconds() * 1000),
                nx=True,
            )
        return bool(result)

    async def delete(self, key: str) -> None:
        await self._redis().delete(self._full_key(key))

    async def exists(self, key: str) -> bool:
        return bool(await self._redis().exists(self._full_key(key)))

    async def close(self) -> None:
        if self._owns_client and self._resolved is not None:
            client = self._resolved
            self._resolved = None
            try:
                await client.close()
            except Exception:  # noqa: BLE001 — boundary cleanup, best-effort
                return

    def namespaced(self, namespace: str) -> RedisStorage:
        joined = f"{self.namespace}:{namespace}" if self.namespace else namespace
        view = RedisStorage.__new__(RedisStorage)
        view._client_external = self._client_external
        view._url = self._url
        view.namespace = joined
        view._owns_client = False
        view._resolved = self._resolved
        return view

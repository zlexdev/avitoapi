"""``MongoStorage`` — :class:`BaseStorage` over ``motor.motor_asyncio`` (lazy import)."""

from __future__ import annotations

import contextlib
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any  # typed-Any: motor AsyncIOMotorClient type param

from .base import BaseStorage

if TYPE_CHECKING:
    from motor.motor_asyncio import (  # optional dep, only with [mongo] extra
        AsyncIOMotorClient,
        AsyncIOMotorCollection,
    )


class MongoStorage(BaseStorage[object, str]):
    """Async-MongoDB-backed K/V. Lazy-imports :mod:`motor.motor_asyncio`.

    Install via ``pip install avitoapi[mongo]``. Each entry is one document:
    ``{"_id": <full_key>, "value": <jsonable>, "expires_at": <datetime|None>}``.

    TTL is enforced by a Mongo TTL index on ``expires_at`` (``expireAfterSeconds=0``)
    plus a read-side ``expires_at < now`` guard so writes are visibly expired
    even before the background sweeper runs.
    """

    def __init__(
        self,
        client: AsyncIOMotorClient[dict[str, Any]] | None = None,
        *,
        url: str | None = None,
        database: str = "avitoapi",
        collection: str = "kv",
        namespace: str = "",
        owns_client: bool | None = None,
    ) -> None:
        if client is None and url is None:
            raise ValueError("MongoStorage: pass either `client` or `url`")
        self._client_external = client
        self._url = url
        self._db_name = database
        self._coll_name = collection
        self.namespace = namespace
        self._owns_client = bool(owns_client) if owns_client is not None else client is None
        self._resolved: AsyncIOMotorClient[dict[str, Any]] | None = client
        self._index_ready = False

    def _full_key(self, key: str) -> str:
        return f"{self.namespace}:{key}" if self.namespace else key

    def _mongo(self) -> AsyncIOMotorClient[dict[str, Any]]:
        if self._resolved is not None:
            return self._resolved
        try:
            from motor.motor_asyncio import AsyncIOMotorClient as _Mongo
        except ImportError as exc:
            raise ImportError(
                "install avitoapi[mongo] to use MongoStorage (missing motor.motor_asyncio)",
            ) from exc
        if self._url is None:
            raise RuntimeError("MongoStorage: no URL and no client provided")
        self._resolved = _Mongo(self._url)
        return self._resolved

    def _collection(self) -> AsyncIOMotorCollection[dict[str, Any]]:
        return self._mongo()[self._db_name][self._coll_name]

    async def _ensure_index(self) -> None:
        if self._index_ready:
            return
        with contextlib.suppress(Exception):
            await self._collection().create_index("expires_at", expireAfterSeconds=0)
        self._index_ready = True

    async def get(self, key: str) -> object | None:
        await self._ensure_index()
        doc = await self._collection().find_one({"_id": self._full_key(key)})
        if doc is None:
            return None
        expires_at = doc.get("expires_at")
        if expires_at is not None and expires_at < datetime.now(UTC):
            await self._collection().delete_one({"_id": self._full_key(key)})
            return None
        value: object | None = doc.get("value")
        return value

    async def put(
        self,
        key: str,
        value: object,
        *,
        ttl: timedelta | None = None,
    ) -> None:
        await self._ensure_index()
        expires_at = datetime.now(UTC) + ttl if ttl is not None else None
        await self._collection().update_one(
            {"_id": self._full_key(key)},
            {"$set": {"value": value, "expires_at": expires_at}},
            upsert=True,
        )

    async def delete(self, key: str) -> None:
        await self._collection().delete_one({"_id": self._full_key(key)})

    async def close(self) -> None:
        if self._owns_client and self._resolved is not None:
            client = self._resolved
            self._resolved = None
            try:
                client.close()
            except Exception:  # noqa: BLE001 — boundary cleanup, best-effort
                return

    def namespaced(self, namespace: str) -> MongoStorage:
        joined = f"{self.namespace}:{namespace}" if self.namespace else namespace
        view = MongoStorage.__new__(MongoStorage)
        view._client_external = self._client_external
        view._url = self._url
        view._db_name = self._db_name
        view._coll_name = self._coll_name
        view.namespace = joined
        view._owns_client = False
        view._resolved = self._resolved
        view._index_ready = self._index_ready
        return view

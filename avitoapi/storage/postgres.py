"""``PostgresStorage`` — :class:`BaseStorage` over ``asyncpg`` (lazy import).

Layout: one table per :class:`PostgresStorage` instance (default
``avitoapi_storage``) with columns ``key`` (text PK), ``value`` (JSONB),
and ``expires_at`` (timestamptz, nullable). The first :meth:`get` /
:meth:`put` call creates the table on demand.

Namespaces are stored as ``"<namespace>:<key>"`` in the ``key`` column so
sub-storages over the same backing pool stay isolated without needing
extra tables.
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from .base import BaseStorage

if TYPE_CHECKING:
    from asyncpg import Pool


_IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")

_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS {table} (
    key        TEXT PRIMARY KEY,
    value      JSONB NOT NULL,
    expires_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS {table}_expires_at_idx
    ON {table} (expires_at)
    WHERE expires_at IS NOT NULL;
"""


class PostgresStorage(BaseStorage[object, str]):
    """Async-Postgres-backed K/V over :mod:`asyncpg`.

    Install via ``pip install avitoapi[postgres]``. Accepts either an
    existing ``asyncpg.Pool`` (recommended for production — share the
    pool across services) or a DSN to build one. Values are stored as
    JSONB; non-JSON-native types (``Decimal``, ``datetime``, ``UUID``)
    are coerced to strings via ``json.dumps(default=str)``.

    TTL is enforced at read time: expired rows are returned as ``None``
    and lazily deleted on next access. Schedule a periodic
    ``DELETE FROM {table} WHERE expires_at < now()`` job for cleanup at
    scale.
    """

    def __init__(
        self,
        pool: Pool | None = None,
        *,
        dsn: str | None = None,
        namespace: str = "",
        table: str = "avitoapi_storage",
        owns_pool: bool | None = None,
        min_pool_size: int = 1,
        max_pool_size: int = 10,
    ) -> None:
        if pool is None and dsn is None:
            raise ValueError("PostgresStorage: pass either `pool` or `dsn`")
        if not _IDENT_RE.fullmatch(table):
            raise ValueError(
                f"PostgresStorage: table name {table!r} must match [A-Za-z_][A-Za-z0-9_]*",
            )
        self._pool_external: Pool | None = pool
        self._dsn = dsn
        self.namespace = namespace
        self._table = table
        self._owns_pool = bool(owns_pool) if owns_pool is not None else pool is None
        self._resolved: Pool | None = pool
        self._schema_ready = False
        self._min_pool_size = int(min_pool_size)
        self._max_pool_size = int(max_pool_size)

    def _full_key(self, key: str) -> str:
        return f"{self.namespace}:{key}" if self.namespace else key

    async def _pool(self) -> Pool:
        if self._resolved is not None:
            await self._ensure_schema(self._resolved)
            return self._resolved
        try:
            import asyncpg
        except ImportError as exc:
            raise ImportError(
                "install avitoapi[postgres] to use PostgresStorage (missing asyncpg)",
            ) from exc
        if self._dsn is None:
            raise RuntimeError("PostgresStorage: no DSN and no pool provided")
        self._resolved = await asyncpg.create_pool(
            self._dsn,
            min_size=self._min_pool_size,
            max_size=self._max_pool_size,
        )
        await self._ensure_schema(self._resolved)
        return self._resolved

    async def _ensure_schema(self, pool: Pool) -> None:
        if self._schema_ready:
            return
        ddl = _TABLE_DDL.format(table=self._table)
        async with pool.acquire() as conn:
            await conn.execute(ddl)
        self._schema_ready = True

    async def get(self, key: str) -> object | None:
        pool = await self._pool()
        full = self._full_key(key)
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                f"SELECT value, expires_at FROM {self._table} WHERE key = $1",
                full,
            )
        if row is None:
            return None
        expires_at = row["expires_at"]
        if expires_at is not None and expires_at < datetime.now(UTC):
            await self.delete(key)
            return None
        value = row["value"]
        if isinstance(value, str):
            try:
                return json.loads(value)  # type: ignore[no-any-return]  # json.loads stubs return Any
            except json.JSONDecodeError:
                return value
        return value  # type: ignore[no-any-return]  # asyncpg Record value typed Any in stubs

    async def put(
        self,
        key: str,
        value: object,
        *,
        ttl: timedelta | None = None,
    ) -> None:
        pool = await self._pool()
        payload = json.dumps(value, default=str, ensure_ascii=False)
        full = self._full_key(key)
        expires_at = datetime.now(UTC) + ttl if ttl is not None else None
        async with pool.acquire() as conn:
            await conn.execute(
                f"""
                INSERT INTO {self._table} (key, value, expires_at)
                VALUES ($1, $2::jsonb, $3)
                ON CONFLICT (key)
                DO UPDATE SET value = EXCLUDED.value,
                              expires_at = EXCLUDED.expires_at
                """,
                full,
                payload,
                expires_at,
            )

    async def add(self, key: str, value: object, *, ttl: timedelta | None = None) -> bool:
        """Atomic set-if-absent via ``INSERT ... ON CONFLICT`` — cross-process safe.

        A fresh key inserts and returns the row. A key whose row is present but
        expired is taken over by the guarded ``DO UPDATE`` (returns a row). A
        live key matches neither branch, returns no row → ``False``.
        """

        pool = await self._pool()
        payload = json.dumps(value, default=str, ensure_ascii=False)
        full = self._full_key(key)
        expires_at = datetime.now(UTC) + ttl if ttl is not None else None
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                f"""
                INSERT INTO {self._table} (key, value, expires_at)
                VALUES ($1, $2::jsonb, $3)
                ON CONFLICT (key) DO UPDATE
                    SET value = EXCLUDED.value,
                        expires_at = EXCLUDED.expires_at
                    WHERE {self._table}.expires_at IS NOT NULL
                      AND {self._table}.expires_at <= now()
                RETURNING key
                """,
                full,
                payload,
                expires_at,
            )
        return row is not None

    async def delete(self, key: str) -> None:
        pool = await self._pool()
        async with pool.acquire() as conn:
            await conn.execute(
                f"DELETE FROM {self._table} WHERE key = $1",
                self._full_key(key),
            )

    async def exists(self, key: str) -> bool:
        pool = await self._pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                f"""
                SELECT 1 FROM {self._table}
                WHERE key = $1
                  AND (expires_at IS NULL OR expires_at > now())
                """,
                self._full_key(key),
            )
        return row is not None

    async def health(self) -> bool:
        try:
            pool = await self._pool()
            async with pool.acquire() as conn:
                value = await conn.fetchval("SELECT 1")
            return bool(value == 1)
        except Exception:  # noqa: BLE001 — boundary probe, surface every failure
            return False

    async def close(self) -> None:
        if self._owns_pool and self._resolved is not None:
            pool = self._resolved
            self._resolved = None
            try:
                await pool.close()
            except Exception:  # noqa: BLE001 — boundary cleanup, best-effort
                return

    def namespaced(self, namespace: str) -> PostgresStorage:
        joined = f"{self.namespace}:{namespace}" if self.namespace else namespace
        view = PostgresStorage.__new__(PostgresStorage)
        view._pool_external = self._pool_external
        view._dsn = self._dsn
        view.namespace = joined
        view._table = self._table
        view._owns_pool = False
        view._resolved = self._resolved
        view._schema_ready = self._schema_ready
        view._min_pool_size = self._min_pool_size
        view._max_pool_size = self._max_pool_size
        return view

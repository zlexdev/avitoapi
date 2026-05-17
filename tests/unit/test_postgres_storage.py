"""Unit tests for :class:`PostgresStorage`.

We can't hit a real Postgres in CI, so we substitute a stub pool that
records the SQL+args and returns canned rows. Verifies SQL surface,
TTL handling, namespace prefixing, and the lazy schema bootstrap.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from avitoapi.storage.postgres import PostgresStorage


class _StubConn:
    def __init__(self, sink: list[tuple[str, tuple[Any, ...]]], rows: dict[str, Any]) -> None:
        self._sink = sink
        self._rows = rows

    async def execute(self, sql: str, *args: Any) -> None:
        self._sink.append(("execute", (sql, args)))

    async def fetchrow(self, sql: str, *args: Any) -> dict[str, Any] | None:
        self._sink.append(("fetchrow", (sql, args)))
        return self._rows.get(args[0] if args else "_no_key")

    async def fetchval(self, sql: str, *args: Any) -> Any:
        self._sink.append(("fetchval", (sql, args)))
        return 1


class _PoolAcquireCtx:
    def __init__(self, conn: _StubConn) -> None:
        self._conn = conn

    async def __aenter__(self) -> _StubConn:
        return self._conn

    async def __aexit__(self, *exc: Any) -> None:
        return None


class _StubPool:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[Any, ...]]] = []
        self.rows: dict[str, Any] = {}

    def acquire(self) -> _PoolAcquireCtx:
        return _PoolAcquireCtx(_StubConn(self.calls, self.rows))

    async def close(self) -> None:
        return None


@pytest.fixture
def pool() -> _StubPool:
    return _StubPool()


@pytest.fixture
def storage(pool: _StubPool) -> PostgresStorage:
    return PostgresStorage(pool=pool)  # type: ignore[arg-type]


async def test_lazy_schema_bootstrap_runs_create_table_once(storage, pool):
    await storage.put("k", {"hi": 1})
    await storage.put("k2", {"hi": 2})
    create_ddl_calls = [
        call for call in pool.calls if call[0] == "execute" and "CREATE TABLE" in call[1][0]
    ]
    assert len(create_ddl_calls) == 1


async def test_put_writes_upsert(storage, pool):
    await storage.put("greeting", {"hello": "world"})
    inserts = [call for call in pool.calls if call[0] == "execute" and "INSERT INTO" in call[1][0]]
    assert inserts
    sql, args = inserts[0][1]
    assert "avitoapi_storage" in sql
    assert args[0] == "greeting"
    assert "hello" in args[1]
    assert args[2] is None


async def test_put_with_ttl_sets_expires_at(storage, pool):
    await storage.put("k", "v", ttl=timedelta(seconds=60))
    inserts = [c for c in pool.calls if c[0] == "execute" and "INSERT INTO" in c[1][0]]
    args = inserts[0][1][1]
    assert args[2] is not None
    assert args[2] > datetime.now(UTC)


async def test_get_returns_none_for_missing_key(storage):
    assert await storage.get("missing") is None


async def test_get_returns_decoded_value(storage, pool):
    pool.rows["the-key"] = {"value": '{"hello": "world"}', "expires_at": None}
    result = await storage.get("the-key")
    assert result == {"hello": "world"}


async def test_get_drops_expired_row(storage, pool):
    expired = datetime.now(UTC) - timedelta(seconds=10)
    pool.rows["stale"] = {"value": '{"x": 1}', "expires_at": expired}
    assert await storage.get("stale") is None
    deletes = [c for c in pool.calls if c[0] == "execute" and c[1][0].strip().startswith("DELETE")]
    assert deletes


async def test_namespace_prefixes_key(pool):
    storage = PostgresStorage(pool=pool, namespace="acc:1")  # type: ignore[arg-type]
    await storage.put("token", "abc")
    inserts = [c for c in pool.calls if c[0] == "execute" and "INSERT INTO" in c[1][0]]
    assert inserts[0][1][1][0] == "acc:1:token"


async def test_namespaced_returns_compound_namespace(storage):
    view = storage.namespaced("acc:1").namespaced("token")
    assert view.namespace == "acc:1:token"


async def test_health_runs_select_one(storage):
    assert await storage.health() is True


def test_invalid_table_name_rejected(pool):
    with pytest.raises(ValueError):
        PostgresStorage(pool=pool, table="users; DROP TABLE x")  # type: ignore[arg-type]


def test_requires_pool_or_dsn():
    with pytest.raises(ValueError):
        PostgresStorage()

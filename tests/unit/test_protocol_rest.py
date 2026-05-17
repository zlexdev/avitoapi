"""Unit tests for ``avitoapi.protocol.rest.RestProtocol``.

Coverage:
- Verb routing: GET fields land in ``query``, POST/PUT/PATCH fields in ``body``.
- Path-templating: ``__path_fields__`` placeholders resolved in the URL.
- Idempotency-Key header is auto-injected for ``__idempotent_mutation__ = True``.
- Idempotency-Key is deduplicated across retries via storage (same key reused).
- Non-idempotent mutation (``__idempotent_mutation__`` unset) gets no header.
"""

from __future__ import annotations

from typing import Any, ClassVar

from avitoapi.config import ClientConfig
from avitoapi.methods._base import BaseMethod
from avitoapi.methods.accounts import GetSelf
from avitoapi.models.accounts import Account
from avitoapi.protocol.rest import RestProtocol
from avitoapi.sessions._models import RequestContext
from avitoapi.storage.memory import MemoryStorage
from pydantic import BaseModel

# ---- helper method-classes used only for this test module -----------------


class _EchoResponse(BaseModel):
    ok: bool = True


class _PostThing(BaseMethod[_EchoResponse]):
    """POST /core/v1/things — body fields go in JSON body."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/core/v1/things"
    __returning__: ClassVar[type[BaseModel]] = _EchoResponse
    __idempotent_mutation__: ClassVar[bool] = True

    name: str
    value: int


class _GetThing(BaseMethod[_EchoResponse]):
    """GET /core/v1/things/{thing_id} — path field + query field."""

    __http_method__: ClassVar[str] = "GET"
    __endpoint__: ClassVar[str] = "/core/v1/things/{thing_id}"
    __returning__: ClassVar[type[BaseModel]] = _EchoResponse
    __path_fields__: ClassVar[frozenset[str]] = frozenset({"thing_id"})

    thing_id: str
    expand: str | None = None


class _UnsafePost(BaseMethod[_EchoResponse]):
    """POST without idempotent_mutation — should NOT get an Idempotency-Key."""

    __http_method__: ClassVar[str] = "POST"
    __endpoint__: ClassVar[str] = "/core/v1/unsafe"
    __returning__: ClassVar[type[BaseModel]] = _EchoResponse

    payload: str


# ---- shared helpers --------------------------------------------------------


class _StubClient:
    """Tiny stub with the attributes RestProtocol expects on ``ctx.client``."""

    def __init__(self, *, config: ClientConfig, storage: MemoryStorage) -> None:
        self.config = config
        self.storage = storage


def _ctx(
    client_config: ClientConfig, storage: MemoryStorage, method: BaseMethod[Any]
) -> RequestContext:
    return RequestContext(
        client=_StubClient(config=client_config, storage=storage),
        method=method,
    )


# ---- verb routing ----------------------------------------------------------


async def test_build_request_routes_get_fields_into_query(
    client_config: ClientConfig,
    storage: MemoryStorage,
) -> None:
    proto = RestProtocol()
    method = _GetThing(thing_id="abc", expand="details")
    ctx = _ctx(client_config, storage, method)

    prepared = await proto.build_request(method, ctx)

    assert prepared.http_method == "GET"
    assert "abc" in prepared.url
    assert prepared.query.get("expand") == "details"
    assert prepared.body in (None, b"", "", {})


async def test_build_request_routes_post_fields_into_body(
    client_config: ClientConfig,
    storage: MemoryStorage,
) -> None:
    proto = RestProtocol()
    method = _PostThing(name="widget", value=42)
    ctx = _ctx(client_config, storage, method)

    prepared = await proto.build_request(method, ctx)

    assert prepared.http_method == "POST"
    assert prepared.body is not None
    if isinstance(prepared.body, (bytes, str)):
        import json

        decoded = json.loads(
            prepared.body if isinstance(prepared.body, str) else prepared.body.decode()
        )
    else:
        decoded = prepared.body
    assert decoded.get("name") == "widget"
    assert decoded.get("value") == 42


# ---- path templating -------------------------------------------------------


async def test_build_request_substitutes_path_placeholders(
    client_config: ClientConfig,
    storage: MemoryStorage,
) -> None:
    proto = RestProtocol()
    method = _GetThing(thing_id="abc-123")
    ctx = _ctx(client_config, storage, method)

    prepared = await proto.build_request(method, ctx)

    assert "/core/v1/things/abc-123" in prepared.url
    assert "{thing_id}" not in prepared.url


async def test_build_request_leaves_path_field_out_of_query(
    client_config: ClientConfig,
    storage: MemoryStorage,
) -> None:
    proto = RestProtocol()
    method = _GetThing(thing_id="abc-123")
    ctx = _ctx(client_config, storage, method)

    prepared = await proto.build_request(method, ctx)

    assert "thing_id" not in prepared.query


# ---- is_idempotent ---------------------------------------------------------


def test_is_idempotent_true_for_get_methods() -> None:
    assert RestProtocol().is_idempotent(GetSelf()) is True


def test_is_idempotent_false_for_non_retry_safe_post() -> None:
    assert RestProtocol().is_idempotent(_UnsafePost(payload="x")) is False


# ---- Idempotency-Key injection ---------------------------------------------


async def test_build_request_injects_idempotency_key_when_method_opts_in(
    client_config: ClientConfig,
    storage: MemoryStorage,
) -> None:
    proto = RestProtocol()
    method = _PostThing(name="w", value=1)
    ctx = _ctx(client_config, storage, method)

    prepared = await proto.build_request(method, ctx)

    assert "Idempotency-Key" in prepared.headers
    assert len(prepared.headers["Idempotency-Key"]) >= 16


async def test_build_request_omits_idempotency_key_when_not_marked(
    client_config: ClientConfig,
    storage: MemoryStorage,
) -> None:
    proto = RestProtocol()
    method = _UnsafePost(payload="x")
    ctx = _ctx(client_config, storage, method)

    prepared = await proto.build_request(method, ctx)

    assert "Idempotency-Key" not in prepared.headers


async def test_build_request_reuses_idempotency_key_across_calls_with_same_body(
    client_config: ClientConfig,
    storage: MemoryStorage,
) -> None:
    """Same method-class + same body fields → same idempotency key, cached in storage.

    This is the retry-dedup guarantee: a retried POST gets the same key, so the
    server treats it as a re-delivery of the original request.
    """
    proto = RestProtocol()

    method_a = _PostThing(name="w", value=1)
    method_b = _PostThing(name="w", value=1)
    ctx_a = _ctx(client_config, storage, method_a)
    ctx_b = _ctx(client_config, storage, method_b)

    prepared_a = await proto.build_request(method_a, ctx_a)
    prepared_b = await proto.build_request(method_b, ctx_b)

    assert prepared_a.headers["Idempotency-Key"] == prepared_b.headers["Idempotency-Key"]


async def test_build_request_uses_different_idempotency_key_for_different_body(
    client_config: ClientConfig,
    storage: MemoryStorage,
) -> None:
    proto = RestProtocol()

    method_a = _PostThing(name="w", value=1)
    method_b = _PostThing(name="w", value=2)
    ctx_a = _ctx(client_config, storage, method_a)
    ctx_b = _ctx(client_config, storage, method_b)

    prepared_a = await proto.build_request(method_a, ctx_a)
    prepared_b = await proto.build_request(method_b, ctx_b)

    assert prepared_a.headers["Idempotency-Key"] != prepared_b.headers["Idempotency-Key"]


# ---- decode_response -------------------------------------------------------


def test_decode_response_validates_into_returning_model(
    accounts_self_payload: dict[str, Any],
) -> None:
    import json

    from avitoapi.sessions._models import RawResponse

    proto = RestProtocol()
    raw = RawResponse(
        status=200,
        headers={"content-type": "application/json"},
        body=json.dumps(accounts_self_payload).encode(),
    )

    result = proto.decode_response(GetSelf(), raw)

    assert isinstance(result, Account)
    assert result.id == accounts_self_payload["id"]

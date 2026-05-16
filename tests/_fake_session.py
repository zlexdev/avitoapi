"""FakeSession — playback-only stand-in for BaseSession.

Drives the funnel without HTTP. Two lookup strategies:

1. **Explicit registration** — ``fake.register(GetSelf, body=..., status=200)``
   registers a canned response keyed by method-class. Tests that don't care
   about the wire signature use this.

2. **Fixture-file lookup** — ``fake.bind_fixture(GetSelf, "accounts_self.json")``
   loads ``tests/fixtures/accounts_self.json`` and serves it on every matching
   call.

Both modes record the prepared request into ``self.sent`` so tests can assert
what the funnel emitted (URL, headers, body).

Record mode (``AVITOAPI_RECORD=1``) is reserved for later waves — W1 ships
playback only.
"""
from __future__ import annotations

import json
import os
from collections import defaultdict
from collections.abc import Callable
from pathlib import Path
from typing import Any

from avitoapi.config import ClientConfig
from avitoapi.methods._base import BaseMethod
from avitoapi.sessions._models import PreparedRequest, RawResponse
from avitoapi.sessions.base import BaseSession
from avitoapi.utils.proxy._base import NoProxyTransport

FIXTURE_DIR = Path(__file__).parent / "fixtures"


class FakeResponse:
    """Canned response payload + status + headers."""

    __slots__ = ("body", "headers", "status")

    def __init__(
        self,
        body: bytes | str | dict[str, Any] | list[Any],
        status: int = 200,
        headers: dict[str, str] | None = None,
    ) -> None:
        if isinstance(body, (dict, list)):
            self.body: bytes = json.dumps(body).encode()
        elif isinstance(body, str):
            self.body = body.encode()
        else:
            self.body = body
        self.status = status
        self.headers: dict[str, str] = headers or {"content-type": "application/json"}


class FakeSession(BaseSession):
    """Scripted session backend for unit tests.

    Lookup order on each ``_send`` call:

    1. Per-route responders keyed by ``(http_method, url_path)``.
    2. Per-method-class responders keyed by ``type(method).__name__``.
    3. A default fall-through responder, if registered.

    Each lookup returns either a :class:`FakeResponse` or a callable
    ``(PreparedRequest) -> FakeResponse`` so tests can vary the answer by
    request signature (body hash, idempotency-key, attempt number).
    """

    def __init__(
        self,
        *,
        config: ClientConfig,
        record: bool = False,
    ) -> None:
        super().__init__(config=config, proxy_transport=NoProxyTransport())
        self._record = record or os.getenv("AVITOAPI_RECORD") == "1"
        self.sent: list[PreparedRequest] = []
        self._by_route: dict[tuple[str, str], FakeResponse | Callable[[PreparedRequest], FakeResponse]] = {}
        self._by_method_name: dict[str, FakeResponse | Callable[[PreparedRequest], FakeResponse]] = {}
        self._call_counts: dict[str, int] = defaultdict(int)
        self._default: FakeResponse | Callable[[PreparedRequest], FakeResponse] | None = None

    # ---- registration API --------------------------------------------------

    def register(
        self,
        method_cls: type[BaseMethod[Any]],
        body: bytes | str | dict[str, Any] | list[Any],
        status: int = 200,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Register a canned response for one method-class. Latest wins."""
        self._by_method_name[method_cls.__name__] = FakeResponse(body=body, status=status, headers=headers)

    def register_responder(
        self,
        method_cls: type[BaseMethod[Any]],
        responder: Callable[[PreparedRequest], FakeResponse],
    ) -> None:
        """Register a dynamic responder for a method-class."""
        self._by_method_name[method_cls.__name__] = responder

    def register_route(
        self,
        http_method: str,
        url_path: str,
        body: bytes | str | dict[str, Any] | list[Any],
        status: int = 200,
        headers: dict[str, str] | None = None,
    ) -> None:
        """Register a canned response keyed by ``(http_method, url_path)``."""
        self._by_route[(http_method.upper(), url_path)] = FakeResponse(body=body, status=status, headers=headers)

    def register_route_responder(
        self,
        http_method: str,
        url_path: str,
        responder: Callable[[PreparedRequest], FakeResponse],
    ) -> None:
        self._by_route[(http_method.upper(), url_path)] = responder

    def bind_fixture(
        self,
        method_cls: type[BaseMethod[Any]],
        fixture_name: str,
        status: int = 200,
    ) -> None:
        """Bind a fixture file (under ``tests/fixtures/``) to a method-class."""
        path = FIXTURE_DIR / fixture_name
        body = path.read_bytes()
        self._by_method_name[method_cls.__name__] = FakeResponse(body=body, status=status)

    def set_default(self, body: bytes | str | dict[str, Any] | list[Any], status: int = 200) -> None:
        self._default = FakeResponse(body=body, status=status)

    # ---- introspection -----------------------------------------------------

    def call_count(self, method_cls: type[BaseMethod[Any]]) -> int:
        return self._call_counts[method_cls.__name__]

    def reset(self) -> None:
        self.sent.clear()
        self._call_counts.clear()

    # ---- BaseSession contract ---------------------------------------------

    async def _send(self, prepared: PreparedRequest) -> RawResponse:
        self.sent.append(prepared)
        method_name = self._infer_method_name(prepared)
        if method_name is not None:
            self._call_counts[method_name] += 1

        responder = self._lookup(prepared, method_name)
        if responder is None:
            raise LookupError(
                f"FakeSession has no canned response for "
                f"{prepared.http_method} {prepared.url} (method={method_name})"
            )

        resp = responder(prepared) if callable(responder) else responder
        return RawResponse(status=resp.status, headers=resp.headers, body=resp.body)

    # ---- internals ---------------------------------------------------------

    def _lookup(
        self,
        prepared: PreparedRequest,
        method_name: str | None,
    ) -> FakeResponse | Callable[[PreparedRequest], FakeResponse] | None:
        url_path = self._strip_query(prepared.url)
        route_key = (prepared.http_method.upper(), url_path)
        if route_key in self._by_route:
            return self._by_route[route_key]
        if method_name is not None and method_name in self._by_method_name:
            return self._by_method_name[method_name]
        return self._default

    @staticmethod
    def _strip_query(url: str) -> str:
        from urllib.parse import urlsplit
        parts = urlsplit(url)
        return parts.path or url.split("?", 1)[0]

    @staticmethod
    def _infer_method_name(prepared: PreparedRequest) -> str | None:
        return getattr(prepared, "method_name", None)

    async def open(self) -> None:  # pragma: no cover - no real socket
        return None

    async def close(self) -> None:  # pragma: no cover - no real socket
        return None

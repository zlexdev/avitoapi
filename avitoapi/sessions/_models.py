"""Wire-level dataclasses passed through the session funnel."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..utils.proxy._base import Proxy, ProxyAcquireContext


@dataclass(slots=True)
class PreparedRequest:
    """Everything ``BaseSession._send`` needs to perform one HTTP request."""

    host: str
    http_method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    query: dict[str, Any] = field(default_factory=dict)
    body: Any = None
    files: list[tuple[str, bytes, str | None]] | None = None
    proxy: str | None = None
    timeout_s: float = 30.0
    method_name: str | None = None


@dataclass(slots=True)
class RawResponse:
    """Raw HTTP output, pre-decode and pre-status-mapping."""

    status: int
    headers: dict[str, str] = field(default_factory=dict)
    body: bytes = b""
    elapsed_s: float = 0.0


@dataclass(slots=True)
class RequestContext:
    """Per-call mutable bag carried through the middleware chain."""

    client: Any
    method: Any | None = None
    breaker_path: str | None = None
    workflow_data: dict[str, Any] = field(default_factory=dict)
    attempt: int = 0
    elapsed_s: float = 0.0
    request_id: str = ""
    account_id: str | None = None
    proxy: Proxy | None = None
    proxy_acquire: ProxyAcquireContext | None = None

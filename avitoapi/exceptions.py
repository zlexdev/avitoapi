"""SDK exception hierarchy. Everything inherits from :class:`SDKError`."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ErrorContext:
    """Attached to every :class:`SDKError` raised inside the funnel.

    Holds enough for a 3am stacktrace to be self-describing: which method-class fired,
    which host/path, attempt number, request id, account id, breaker scope, start time.
    """

    method: str | None = None
    host: str | None = None
    path: str | None = None
    attempt: int = 0
    request_id: str = ""
    account_id: str | None = None
    breaker_path: str | None = None
    extras: dict[str, Any] = field(default_factory=dict)


class SDKError(Exception):
    """Root of the SDK exception tree. Subclass for specific failure modes."""

    default_message: str = "SDK error"

    def __init__(
        self,
        detail: str | None = None,
        *,
        context: ErrorContext | None = None,
    ) -> None:
        super().__init__(detail or self.default_message)
        self.detail = detail or self.default_message
        self.context = context

    def __str__(self) -> str:
        if self.context is None:
            return self.detail
        ctx = self.context
        parts = [self.detail]
        for label, value in (
            ("method", ctx.method),
            ("host", ctx.host),
            ("path", ctx.path),
            ("attempt", ctx.attempt or None),
            ("request_id", ctx.request_id or None),
            ("account_id", ctx.account_id),
        ):
            if value is not None:
                parts.append(f"{label}={value}")
        return " | ".join(parts)


class ConfigError(SDKError):
    default_message = "Invalid configuration"


class MethodDeclarationError(SDKError, TypeError):
    """Raised at import time when a ``BaseMethod`` subclass is malformed."""

    default_message = "Invalid method declaration"


class MethodNotBoundError(SDKError, RuntimeError):
    """Awaited a method (or called a bound model action) without binding a client."""

    default_message = "Method has no client bound"


class TransportError(SDKError):
    default_message = "Transport-level failure"


class ConnectionError(TransportError):
    default_message = "Connection error"


class TimeoutError(TransportError):
    default_message = "Request timed out"


class TLSError(TransportError):
    default_message = "TLS handshake failure"


class SessionClosed(TransportError, RuntimeError):
    default_message = "Session is closed"


class ProxyError(TransportError):
    """Base for every proxy-attributable failure.

    ``proxy_url`` is the raw proxy endpoint that was in use when the
    failure happened (may be ``None`` when the parser refuses the input
    upfront, before any wire call).
    """

    default_message = "Proxy error"

    def __init__(
        self,
        detail: str | None = None,
        *,
        proxy_url: str | None = None,
        context: ErrorContext | None = None,
    ) -> None:
        super().__init__(detail, context=context)
        self.proxy_url = proxy_url


class ProxyParseError(ProxyError, ValueError):
    """Raised by :func:`parse_proxy` when the input shape is not recognised."""

    default_message = "Could not parse proxy specification"


class ProxyConnectionError(ProxyError):
    """The proxy refused / dropped the connection (TCP-level)."""

    default_message = "Proxy connection error"


class ProxyAuthError(ProxyError):
    """407 from the proxy, or upstream auth challenge the proxy passed through."""

    default_message = "Proxy authentication failed"


class ProxyTimeoutError(ProxyError):
    """The proxy did not respond inside the request timeout."""

    default_message = "Proxy timed out"


class ProxyTLSError(ProxyError):
    """TLS handshake to or through the proxy failed."""

    default_message = "Proxy TLS error"


class ProxyBanned(ProxyError):
    """Accumulated failures crossed the configured threshold; proxy is now banned.

    Carries the failure tally on ``failure_count`` so callers can surface
    the threshold in operator dashboards or alert pipelines.
    """

    default_message = "Proxy banned after accumulated failures"

    def __init__(
        self,
        detail: str | None = None,
        *,
        proxy_url: str | None = None,
        failure_count: int = 0,
        context: ErrorContext | None = None,
    ) -> None:
        super().__init__(detail, proxy_url=proxy_url, context=context)
        self.failure_count = failure_count


class ProxyExhausted(ProxyError):
    """Every proxy in the pool is banned and none are available right now."""

    default_message = "Proxy pool exhausted — all proxies are banned"


class HTTPError(SDKError):
    """Raised when the server returns a non-2xx response."""

    default_message = "HTTP error"
    status: int = 0

    def __init__(
        self,
        detail: str | None = None,
        *,
        status: int | None = None,
        body: bytes | str | None = None,
        context: ErrorContext | None = None,
    ) -> None:
        super().__init__(detail, context=context)
        if status is not None:
            self.status = status
        self.body = body


class ClientError(HTTPError):
    default_message = "4xx client error"


class BadRequest(ClientError):
    default_message = "400 Bad Request"
    status = 400


class UnauthorizedError(ClientError):
    default_message = "401 Unauthorized"
    status = 401


class ForbiddenError(ClientError):
    default_message = "403 Forbidden"
    status = 403


class NotFoundError(ClientError):
    default_message = "404 Not Found"
    status = 404


class ConflictError(ClientError):
    default_message = "409 Conflict"
    status = 409


class ValidationFailed(ClientError):
    default_message = "422 Unprocessable Entity"
    status = 422


class RateLimitedError(ClientError):
    default_message = "429 Too Many Requests"
    status = 429

    def __init__(
        self,
        detail: str | None = None,
        *,
        retry_after_s: float = 0.0,
        body: bytes | str | None = None,
        context: ErrorContext | None = None,
    ) -> None:
        super().__init__(detail, status=429, body=body, context=context)
        self.retry_after_s = retry_after_s


class ServerError(HTTPError):
    default_message = "5xx server error"


class InternalServerError(ServerError):
    default_message = "500 Internal Server Error"
    status = 500


class BadGatewayError(ServerError):
    default_message = "502 Bad Gateway"
    status = 502


class ServiceUnavailableError(ServerError):
    default_message = "503 Service Unavailable"
    status = 503


class GatewayTimeoutError(ServerError):
    default_message = "504 Gateway Timeout"
    status = 504


class AuthError(SDKError):
    default_message = "Authentication failure"


class TokenExpired(AuthError):
    default_message = "OAuth token expired"


class TokenIssuanceFailed(AuthError):
    default_message = "Failed to issue OAuth token"


class ProtocolError(SDKError):
    default_message = "Protocol-level decoding failure"


class ResponseDecodingError(ProtocolError):
    default_message = "Response could not be decoded into the declared returning type"


class PathResolutionError(ProtocolError):
    default_message = "Could not fill a path placeholder from method fields"


class ModelNotBoundError(MethodNotBoundError):
    """Subclass alias so :class:`BoundModel` callers can catch either name."""

    default_message = "Model has no client bound"


class InvalidStateTransition(SDKError):
    """Domain state machine refused a transition from ``current`` to ``target``.

    Raised by ``assert_order_transition`` (and any future state machine guard)
    when the caller asked the model to jump to a state the transition table
    does not allow. Carries the offending pair on ``.current`` / ``.target`` so
    middlewares can map it to a user-facing message.
    """

    default_message = "Invalid state transition"

    def __init__(
        self,
        detail: str | None = None,
        *,
        current: Any = None,
        target: Any = None,
        context: ErrorContext | None = None,
    ) -> None:
        super().__init__(detail, context=context)
        self.current = current
        self.target = target


class StorageError(SDKError):
    default_message = "Storage backend error"


class PaginationError(SDKError):
    default_message = "Pagination error"


class RunawayPagination(PaginationError, RuntimeError):
    """Raised when a paginator exceeds the configured ``max_pages`` guard."""

    default_message = "Paginator exceeded max_pages — runaway loop guard tripped"


_STATUS_MAP: dict[int, type[HTTPError]] = {
    400: BadRequest,
    401: UnauthorizedError,
    403: ForbiddenError,
    404: NotFoundError,
    409: ConflictError,
    422: ValidationFailed,
    429: RateLimitedError,
    500: InternalServerError,
    502: BadGatewayError,
    503: ServiceUnavailableError,
    504: GatewayTimeoutError,
}


def http_error_for_status(status: int) -> type[HTTPError]:
    """Map an HTTP status code to the most-specific exception class.

    Falls back to :class:`ClientError` for unmapped 4xx and :class:`ServerError`
    for unmapped 5xx; everything else gets the generic :class:`HTTPError`.
    """

    if status in _STATUS_MAP:
        return _STATUS_MAP[status]
    if 400 <= status < 500:
        return ClientError
    if 500 <= status < 600:
        return ServerError
    return HTTPError

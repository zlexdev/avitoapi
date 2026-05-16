"""Structlog setup + redaction processor for secrets/tokens."""
from __future__ import annotations

import logging
import sys
from typing import Any

import structlog
from structlog.contextvars import merge_contextvars
from structlog.processors import (
    JSONRenderer,
    TimeStamper,
    add_log_level,
    format_exc_info,
)
from structlog.stdlib import BoundLogger

_REDACT_KEYS = frozenset(
    {
        "access_token",
        "refresh_token",
        "client_secret",
        "authorization",
        "x-api-key",
        "cookie",
        "set-cookie",
        "password",
        "token",
    },
)
_REDACTED = "***"


def _redact_processor(
    _logger: Any,
    _method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    return _walk_redact(event_dict)


def _walk_redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            k: (_REDACTED if k.lower() in _REDACT_KEYS else _walk_redact(v))
            for k, v in value.items()
        }
    if isinstance(value, list):
        return [_walk_redact(item) for item in value]
    return value


_configured = False


def configure(level: int | str = logging.INFO, *, json: bool = False) -> None:
    """Idempotently configure structlog + stdlib logging.

    JSON renderer when ``json=True`` (production); ConsoleRenderer otherwise.
    """

    global _configured  # noqa: PLW0603 — module-level idempotency guard
    if _configured:
        return

    logging.basicConfig(
        format="%(message)s",
        level=level,
        stream=sys.stderr,
    )

    processors: list[Any] = [
        merge_contextvars,
        add_log_level,
        TimeStamper(fmt="iso", utc=True),
        _redact_processor,
        format_exc_info,
    ]
    processors.append(JSONRenderer() if json else structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(level) if isinstance(level, int) else level,
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(sys.stderr),
        cache_logger_on_first_use=True,
    )
    _configured = True


def get_logger(name: str | None = None) -> BoundLogger:
    """Lazily configures structlog on first call; returns a bound logger."""

    if not _configured:
        configure()
    return structlog.get_logger(name)

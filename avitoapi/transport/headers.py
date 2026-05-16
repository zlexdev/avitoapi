"""Default header builder for outbound requests."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..config import ClientConfig


def build_default_headers(config: ClientConfig) -> dict[str, str]:
    """Build the headers every request inherits — User-Agent, Accept, Accept-Language."""

    return {
        "User-Agent": config.user_agent,
        "Accept": "application/json, */*;q=0.5",
        "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.5",
    }

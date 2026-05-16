"""Wire-protocol abstraction. See ``_MODULE.md``."""
from __future__ import annotations

from .base import Protocol
from .rest import RestProtocol

__all__ = ["Protocol", "RestProtocol"]

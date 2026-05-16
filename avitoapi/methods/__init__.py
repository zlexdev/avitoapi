"""Per-domain method-classes. See ``_MODULE.md``."""
from __future__ import annotations

from ._base import BaseMethod
from .accounts import GetSelf

__all__ = ["BaseMethod", "GetSelf"]

"""Stable model helpers shared by generated DTOs — hand-written, never regenerated.

``_resolve_user_id`` pulls the account id from the bound client's config so bound methods
can fill their ``{user_id}`` path segment. A missing/unbound client yields ``0``; the real
"not bound" failure surfaces later at ``await`` time via ``MethodNotBoundError``.
"""

from __future__ import annotations

from typing import Any


def _resolve_user_id(client: Any) -> int:
    """Resolve the account ``user_id`` from the bound client's config (``0`` if unbound)."""

    user_id = getattr(getattr(client, "config", None), "user_id", None)
    return int(user_id) if user_id is not None else 0

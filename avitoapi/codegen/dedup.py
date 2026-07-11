"""Cross-domain model dedup — collapse structurally-identical DTOs into ``models/_shared.py``.

Placeholder implementation (F1 fills it in): the real pass groups models across every domain
by their field signature, keeps one canonical definition, and rewrites every reference. Until
then it is a no-op so the two-phase ``--all`` pipeline runs unchanged.
"""

from __future__ import annotations

from .build import GeneratedDomain


def dedup_shared(domains: list[GeneratedDomain]) -> dict[str, str]:
    """Collapse duplicate models; return extra files to write (e.g. ``models/_shared.py``).

    No-op until F1 lands: returns no extra files and leaves every domain untouched.
    """

    return {}

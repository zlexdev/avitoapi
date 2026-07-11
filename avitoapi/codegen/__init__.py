"""avitoapi codegen — the auto-builder.

Fetches the official Avito OpenAPI specs from ``developers.avito.ru`` and regenerates the
SDK surface (``enums/``, ``models/``, ``methods/``) in the project house style: method-as-class
with wire ClassVars, ``AvitoObject`` DTOs, ``Field(...)`` constraints, ``StrEnum``s, and
auto-generated bound methods. The operational machinery (base classes, protocol, transport,
client, pools, pagination, events) is hand-written and never touched by the generator.

Usage::

    python -m avitoapi.codegen --slug item
    python -m avitoapi.codegen --all
"""

from __future__ import annotations

from .generate import all_slugs, generate, render_domain

__all__ = ["all_slugs", "generate", "render_domain"]

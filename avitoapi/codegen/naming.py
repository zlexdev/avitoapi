"""Name normalisation — camelCase spec identifiers → Python house style.

`operationId` → PascalCase class name, property/param → snake_case field, path
placeholders → snake_case, plus a keyword/collision guard. All pure string functions,
no spec knowledge.
"""

from __future__ import annotations

import keyword
import re

_WORD_BOUNDARY = re.compile(r"[^0-9a-zA-Z]+")
_CAMEL_SPLIT = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
_PLACEHOLDER = re.compile(r"\{(\w+)\}")


def _words(raw: str) -> list[str]:
    """Split ``raw`` into lowercase word tokens across camelCase and separators."""

    parts: list[str] = []
    for chunk in _WORD_BOUNDARY.split(raw):
        if not chunk:
            continue
        parts.extend(p for p in _CAMEL_SPLIT.split(chunk) if p)
    return [p.lower() for p in parts]


#: field names that would shadow an imported type in the class namespace (Pydantic then
#: fails to resolve the annotation once the field's default becomes a class attribute).
_SHADOWS_TYPE = frozenset({"date", "datetime", "any"})


def snake(raw: str) -> str:
    """``userId`` / ``user-id`` / ``UserID`` → ``user_id`` (keyword- and type-shadow-safe)."""

    out = "_".join(_words(raw)) or "field"
    if out[0].isdigit():
        out = f"f_{out}"
    if keyword.iskeyword(out) or keyword.issoftkeyword(out) or out in _SHADOWS_TYPE:
        out = f"{out}_"
    return out


def pascal(raw: str) -> str:
    """``getItemInfo`` → ``GetItemInfo``; safe for a class identifier."""

    out = "".join(w.capitalize() for w in _words(raw)) or "Model"
    if out[0].isdigit():
        out = f"M{out}"
    return out


def class_name_for_operation(operation_id: str) -> str:
    """Method-class name from an ``operationId``."""

    return pascal(operation_id)


def enum_class_name(owner: str, field: str) -> str:
    """StrEnum name for an inline enum on ``owner.field``."""

    return f"{pascal(owner)}{pascal(field)}"


def normalise_endpoint(path: str) -> str:
    """Rewrite ``{userId}``/``{itemId}`` placeholders to their snake_case field names."""

    return _PLACEHOLDER.sub(lambda m: "{" + snake(m.group(1)) + "}", path)


def placeholders(path: str) -> list[str]:
    """Snake-cased placeholder names in ``path`` (post-:func:`normalise_endpoint`)."""

    return [snake(m.group(1)) for m in _PLACEHOLDER.finditer(path)]

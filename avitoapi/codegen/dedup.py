"""Cross-domain model dedup — collapse structurally-identical DTOs.

Each domain builds its models independently from its own spec, so the same shape is
re-emitted many times: 81 ``{code, message}`` error bodies across 50 names, ``NotFoundError``
in 9 domains, and so on. This pass runs once over the whole catalogue (after
:func:`generate.build_all`) and folds those duplicates away in two stages:

* **Pass A — error bodies → :class:`~avitoapi.models.common.AvitoErrorBody`.** Every model
  whose fields are exactly ``{code, message}`` is dropped and every reference rewritten to
  the shared ``AvitoErrorBody`` already in ``models/common.py``.
* **Pass B — identical models → ``models/_shared.py``.** After pass A converges the wrapper
  shapes, any model that appears under the *same name* with an *identical field signature*
  in ≥2 domains is emitted once into ``models/_shared.py`` and imported everywhere.

Reference rewriting mutates every annotation in place (via :func:`dataclasses.replace`, since
``FieldSpec``/``BoundArg`` are frozen) and records, per domain, which names are now imported
from a shared module (:attr:`GeneratedDomain.shared_imports`) so the emitters wire the imports.

Safety rails: entity models (those carrying bound methods) are never shared, and a model is
only moved to ``_shared.py`` when its annotations reference nothing domain-local — only
scalars, datetimes, and ``AvitoErrorBody`` (see :data:`_SAFE_REFS`).
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import replace

from . import render
from .build import GeneratedDomain
from .types import ModelSpec

_ERROR_FIELDS = frozenset({"code", "message"})
_ERROR_BODY = "AvitoErrorBody"

COMMON = "common"  # -> avitoapi/models/common.py
SHARED = "_shared"  # -> avitoapi/models/_shared.py

# PascalCase tokens a shared model may reference without pulling in a domain-local symbol.
_SAFE_REFS = frozenset({_ERROR_BODY, "TZDatetime"})
_PASCAL = re.compile(r"\b[A-Z][A-Za-z0-9]+\b")

Signature = tuple[tuple[str, str, str, str], ...]  # ordered (name, wire, annotation, assignment)


def dedup_shared(domains: list[GeneratedDomain]) -> dict[str, str]:
    """Collapse duplicate models across ``domains``; return extra files to write.

    Mutates ``domains`` in place (drops duplicate model defs, rewrites references, fills
    :attr:`GeneratedDomain.shared_imports`). Returns ``{"models/_shared.py": source}`` when
    pass B kept anything, else ``{}``.
    """

    _collapse_error_bodies(domains)
    shared = _collapse_identical(domains)
    if not shared:
        return {}
    return {"models/_shared.py": _render_shared_module(shared)}


def _signature(model: ModelSpec) -> Signature:
    return tuple((f.name, f.wire_name, f.annotation, f.assignment or "") for f in model.fields)


def _is_error_shaped(model: ModelSpec) -> bool:
    return len(model.fields) == 2 and {f.name for f in model.fields} == _ERROR_FIELDS


def _shareable(model: ModelSpec, refs_ok: bool = True) -> bool:
    """A model with fields whose annotations reference nothing domain-local."""

    if not model.fields:
        return False
    if not refs_ok:
        return True
    tokens = {t for f in model.fields for t in _PASCAL.findall(f.annotation)}
    return tokens <= _SAFE_REFS


def _rewrite(text: str, renames: dict[str, str]) -> str:
    if not text or not renames:
        return text
    pattern = re.compile(r"\b(" + "|".join(re.escape(k) for k in renames) + r")\b")
    return pattern.sub(lambda m: renames[m.group(0)], text)


def _apply_renames(gen: GeneratedDomain, renames: dict[str, str]) -> None:
    """Rewrite every annotation/assignment in ``gen`` that names a renamed model."""

    for name, model in gen.models.items():
        model.fields = [replace(f, annotation=_rewrite(f.annotation, renames), assignment=_rewrite(f.assignment, renames) if f.assignment else f.assignment) for f in model.fields]
        gen.models[name] = model
    gen.root_models = {k: _rewrite(v, renames) for k, v in gen.root_models.items()}
    for m in gen.methods:
        m.generic_arg = _rewrite(m.generic_arg, renames)
        if m.return_symbol:
            m.return_symbol = _rewrite(m.return_symbol, renames)
        m.fields = [replace(f, annotation=_rewrite(f.annotation, renames), assignment=_rewrite(f.assignment, renames) if f.assignment else f.assignment) for f in m.fields]
    for owner, bms in gen.bound.items():
        gen.bound[owner] = [replace(bm, args=tuple(replace(a, annotation=_rewrite(a.annotation, renames)) for a in bm.args)) for bm in bms]


def _collapse_error_bodies(domains: list[GeneratedDomain]) -> None:
    """Pass A — map every ``{code, message}`` model onto ``common.AvitoErrorBody``."""

    for gen in domains:
        renames = {name: _ERROR_BODY for name, model in gen.models.items() if _is_error_shaped(model) and name not in gen.bound}
        if not renames:
            continue
        for name in renames:
            del gen.models[name]
        _apply_renames(gen, renames)
        gen.shared_imports[_ERROR_BODY] = COMMON


def _collapse_identical(domains: list[GeneratedDomain]) -> dict[str, ModelSpec]:
    """Pass B — move same-name, same-signature, cross-domain models to ``models/_shared.py``."""

    by_name: dict[str, list[tuple[GeneratedDomain, ModelSpec]]] = defaultdict(list)
    bound_anywhere: set[str] = set()
    for gen in domains:
        for name, model in gen.models.items():
            if name in gen.bound:
                bound_anywhere.add(name)
                continue
            by_name[name].append((gen, model))

    shared: dict[str, ModelSpec] = {}
    for name in sorted(by_name):
        if name in bound_anywhere:
            continue
        members = by_name[name]
        if len(members) < 2:
            continue
        if len({_signature(model) for _, model in members}) != 1:
            continue  # same name, divergent shape — keep per-domain
        if not _shareable(members[0][1]):
            continue  # references a domain-local symbol — cannot hoist safely
        shared[name] = members[0][1]
        for gen, _ in members:
            del gen.models[name]
            gen.shared_imports[name] = SHARED
    return shared


def _render_shared_module(shared: dict[str, ModelSpec]) -> str:
    text = " ".join(f.annotation + " " + (f.assignment or "") for model in shared.values() for f in model.fields)
    lines: list[str] = []
    lines.extend(render.datetime_imports(_needs(text), in_methods=False))
    lines.append("from pydantic import Field")
    lines.append("from ._base import AvitoObject")
    if re.search(rf"\b{_ERROR_BODY}\b", text):
        lines.append(f"from .common import {_ERROR_BODY}")
    body: list[str] = [
        render.GENERATED_HEADER,
        render.module_doc("Shared models", "cross-domain DTOs collapsed by codegen dedup"),
        "\nfrom __future__ import annotations\n",
        "\n".join(lines) + "\n",
        "\n",
    ]
    for name in sorted(shared):
        body.append(_render_model(shared[name]))
        body.append("\n")
    return "".join(body)


def _render_model(model: ModelSpec) -> str:
    doc = render.class_docstring(
        model.doc or f"{model.name} — shared across domains.",
        "Attributes",
        [(f.name, f.description) for f in model.fields],
    )
    out = [f"class {model.name}(AvitoObject):", doc.rstrip("\n")]
    for f in model.fields:
        out.append(render.field_line(f.name, f.annotation, f.assignment).rstrip("\n"))
    return "\n".join(out) + "\n"


def _needs(text: str) -> set[str]:
    out: set[str] = set()
    if "TZDatetime" in text:
        out.add("TZDatetime")
    if re.search(r"\bdatetime\b", text):
        out.add("datetime")
    if re.search(r"\bdate\b", text):
        out.add("date")
    return out


def shared_import_lines(gen: GeneratedDomain, text: str, *, in_models_pkg: bool) -> list[str]:
    """Import lines for the shared models ``gen`` references — relative to the emitter's package."""

    by_target: dict[str, list[str]] = defaultdict(list)
    for name, target in gen.shared_imports.items():
        if re.search(rf"\b{name}\b", text):
            by_target[target].append(name)
    prefix = "." if in_models_pkg else "..models."
    return [f"from {prefix}{target} import {', '.join(sorted(set(by_target[target])))}" for target in sorted(by_target)]

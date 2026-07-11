"""Render ``facade/<module>.py`` — a mixin class of endpoint methods inherited by ``Client``.

``Client`` subclasses every ``*Facade`` mixin, so ``await client.get_item_info(item_id=…)``
constructs the generated method-class and awaits it through ``Client.__call__`` (``self`` *is*
the client). ``user_id`` path segments default to the client's account. Paginated endpoints
stay sync and return a ``MethodPaginator``.
"""

from __future__ import annotations

import re

from . import naming, render
from .build import GeneratedDomain, MethodSpec


def facade_class(module: str) -> str:
    return f"{naming.pascal(module)}Facade"


def emit(gen: GeneratedDomain) -> str:
    sig_text = _signature_text(gen)
    out = [
        render.GENERATED_HEADER,
        render.module_doc(gen.title, "client facade mixin"),
        "\nfrom __future__ import annotations\n",
        _import_block(gen, sig_text),
        "\n\n",
        f"class {facade_class(gen.module)}(FacadeBase):\n",
        f'    """``Client`` mixin — {gen.title} endpoints."""\n\n',
    ]
    note = f"See: {gen.docs_url}"
    for method in gen.methods:
        out.append(_render_call(method, note))
        out.append("\n\n")
    return "".join(out)


def _signature_text(gen: GeneratedDomain) -> str:
    parts: list[str] = []
    for m in gen.methods:
        parts.append(m.generic_arg)
        parts.append(m.return_symbol or "")
        for f in m.fields:
            parts.append(f.annotation)
    return " ".join(parts)


def _import_block(gen: GeneratedDomain, text: str) -> str:
    lines: list[str] = []
    if re.search(r"\bAny\b", text):
        lines.append("from typing import Any")
    needs: set[str] = set()
    if "TZDatetime" in text:
        needs.add("TZDatetime")
    if re.search(r"\bdatetime\b", text):
        needs.add("datetime")
    if re.search(r"\bdate\b", text):
        needs.add("date")
    lines.extend(render.datetime_imports(needs, in_methods=True))
    method_classes = sorted(m.class_name for m in gen.methods)
    if method_classes:
        lines.append(f"from ..methods.{gen.module} import {', '.join(method_classes)}")

    known_models = set(gen.models) | set(gen.root_models)
    models_used = sorted({m.return_symbol for m in gen.methods if m.return_symbol} | {s for s in known_models if re.search(rf"\b{s}\b", text)})
    if models_used:
        lines.append(f"from ..models.{gen.module} import {', '.join(models_used)}")
    enums_used = sorted(e for e in gen.enums if re.search(rf"\b{e}\b", text))
    if enums_used:
        lines.append(f"from ..enums.{gen.module} import {', '.join(enums_used)}")

    lines.append("from ..models._helpers import _resolve_user_id")
    if any(m.paginated for m in gen.methods):
        lines.append("from ..pagination import MethodPaginator")
    lines.append("from ._base import FacadeBase")
    return "\n".join(lines) + "\n"


def _return_annotation(m: MethodSpec) -> str:
    if m.paginated:
        return f"MethodPaginator[{m.return_symbol or 'None'}]"
    if m.binary:
        return "bytes"
    return m.generic_arg if m.generic_arg != "None" else "None"


def _render_call(m: MethodSpec, note: str) -> str:
    accounts = set(m.account_params)
    required = [f for f in m.fields if f.required and f.name not in accounts]
    optional = [f for f in m.fields if not f.required or f.name in accounts]

    params = [f"{f.name}: {f.annotation}" for f in required]
    for f in optional:
        annot = f.annotation if f.name not in accounts else f"{f.annotation} | None"
        params.append(f"{f.name}: {annot} = {'None' if f.name in accounts else (f.default_expr or 'None')}")
    signature = ", ".join(["self", *params])

    call_args = [
        f"{f.name}=_resolve_user_id(self) if {f.name} is None else {f.name}"
        if f.name in accounts
        else f"{f.name}={f.name}"
        for f in m.fields
    ]
    call = f"{m.class_name}({', '.join(call_args)})"

    method_name = naming.snake(m.class_name)
    doc = render.class_docstring(m.doc, "Args", [(f.name, f.description) for f in m.fields], indent="        ", note=note)
    kw, invoke = ("def", f"self({call})") if m.paginated else ("async def", f"await self({call})")
    return "\n".join(
        [
            f"    {kw} {method_name}({signature}) -> {_return_annotation(m)}:",
            doc.rstrip("\n"),
            f"        return {invoke}",
        ],
    )

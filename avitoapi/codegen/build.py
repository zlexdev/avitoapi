"""Orchestrator — spec IR → models + method specs + bound methods for one domain.

Runs the pipeline in the order that lets nested types register before emission:
build component models → walk every operation's fields (registering inline models/enums
+ collecting method specs) → detect entities → bind methods.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import config, entities, naming
from .entities import BoundMethod
from .spec import Domain
from .types import EnumSpec, FieldSpec, ModelBuilder, ModelSpec


@dataclass(slots=True)
class MethodSpec:
    """A fully-resolved method-class ready to emit."""

    class_name: str
    operation_id: str
    base: str  # "BaseMethod" | "PageMethod"
    generic_arg: str  # e.g. "Item", "bytes", "None"
    http_method: str
    endpoint: str
    fields: list[FieldSpec]
    account_params: tuple[str, ...]  # path params filled from the client (user_id)
    doc: str
    idempotent: bool
    multipart: bool
    binary: bool
    return_symbol: str | None  # model name to import from the models module
    paginated: bool
    method_name: str  # snake(class_name); globally de-duplicated for the facade (see collisions.py)


@dataclass(slots=True)
class GeneratedDomain:
    """Everything needed to render ``methods/<module>.py`` + ``models/<module>.py``."""

    slug: str
    module: str
    title: str
    docs_url: str
    models: dict[str, ModelSpec]
    enums: dict[str, EnumSpec]
    root_models: dict[str, str] = field(default_factory=dict)
    methods: list[MethodSpec] = field(default_factory=list)
    bound: dict[str, list[BoundMethod]] = field(default_factory=dict)
    shared_imports: dict[str, str] = field(default_factory=dict)  # name -> "common" | "_shared" (dedup.py)


def _is_paginated(op_query_names: set[str]) -> bool:
    return {"page", "per_page"} <= op_query_names


def build_domain(domain: Domain) -> GeneratedDomain:
    """Produce a :class:`GeneratedDomain` from a spec :class:`Domain` IR."""

    builder = ModelBuilder(domain)
    builder.build()

    gen = GeneratedDomain(
        slug=domain.slug,
        module=config.module_for_slug(domain.slug),
        title=domain.title,
        docs_url=config.DOCS_URL_TEMPLATE.format(slug=domain.slug),
        models=builder.models,
        enums=builder.enums,
        root_models=builder.root_models,
    )
    field_specs: dict[str, FieldSpec] = {}

    for op in domain.operations:
        query_names = {p.name for p in op.query_params}
        paginated = _is_paginated(query_names) and op.response_ref is not None
        base = "PageMethod" if paginated else "BaseMethod"

        # return type / generic argument
        if op.binary_response:
            generic, return_symbol = "bytes", None
        elif op.response_ref:
            generic = return_symbol = naming.pascal(op.response_ref)
        elif op.response_inline is not None:
            generic = return_symbol = builder.model_from_inline(f"{op.class_name}Response", op.response_inline)
        else:
            generic, return_symbol = "None", None

        fields: list[FieldSpec] = []
        for p in op.path_params:
            fs = builder.field_spec(p.name, p.wire_name, p.schema, p.required, op.class_name, description=p.description)
            fields.append(fs)
            field_specs[f"{op.class_name}.{p.name}"] = fs
        for p in op.query_params:
            if paginated and p.name in ("page", "per_page"):
                continue  # PageMethod supplies these
            fs = builder.field_spec(p.name, p.wire_name, p.schema, p.required, op.class_name, description=p.description)
            fields.append(fs)
            field_specs[f"{op.class_name}.{p.name}"] = fs
        for prop in op.body_props:
            fs = builder.field_spec(prop.name, prop.wire_name, prop.schema, prop.required, op.class_name, description=prop.description)
            fields.append(fs)
            field_specs[f"{op.class_name}.{prop.name}"] = fs

        account_params = tuple(p.name for p in op.path_params if p.name in config.ACCOUNT_CONTEXT_PARAMS)
        gen.methods.append(
            MethodSpec(
                class_name=op.class_name,
                method_name=naming.snake(op.class_name),
                operation_id=op.operation_id,
                base=base,
                generic_arg=generic,
                http_method=op.http_method,
                endpoint=op.endpoint,
                fields=fields,
                account_params=account_params,
                doc=_method_doc(op.summary, op.description, op.http_method, op.endpoint),
                idempotent=op.idempotent,
                multipart=op.multipart,
                binary=op.binary_response,
                return_symbol=return_symbol,
                paginated=paginated,
            ),
        )

    model_fields = {name: frozenset(f.name for f in m.fields) for name, m in builder.models.items()}
    ents = entities.detect_entities(domain, model_fields)
    gen.bound = entities.bound_methods(domain, ents, field_specs)
    return gen


def _method_doc(summary: str | None, description: str | None, verb: str, endpoint: str) -> str:
    head = (summary or description or f"{verb} {endpoint}").replace("\n", " ").strip()
    return f"{head} via ``{verb} {endpoint}``."

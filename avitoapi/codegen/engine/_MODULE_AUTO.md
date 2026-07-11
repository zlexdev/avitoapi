# engine/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

## build.py
```
# Orchestrator — spec IR → models + method specs + bound methods for one domain.


cls MethodSpec: class_name: str, operation_id: str, base: str, generic_arg: str, http_method: str, endpoint: str, fields: list[FieldSpec], account_params: tuple[str, ...], doc: str, idempotent: bool, … (15)
  # A fully-resolved method-class ready to emit.

cls GeneratedDomain: slug: str, module: str, title: str, docs_url: str, models: dict[str, ModelSpec], enums: dict[str, EnumSpec], root_models: dict[str, str], methods: list[MethodSpec], bound: dict[str, list[BoundMethod]], shared_imports: dict[str, str]
  # Everything needed to render ``methods/<module>.py`` + ``models/<module>.py``.

_is_paginated(op_query_names: set[str) -> bool

build_domain(domain: Domain) -> GeneratedDomain
  # Produce a :class:`GeneratedDomain` from a spec :class:`Domain` IR.

_method_doc(summary: str?, description: str?, verb: str, endpoint: str) -> str

```

## collisions.py
```
# Cross-domain facade collision resolution — make every ``Client`` method name unique.


resolve_facade_collisions(domains: list[GeneratedDomain) -> dict[str, str]

```

## dedup.py
```
# Cross-domain model dedup — collapse structurally-identical DTOs.

_ERROR_FIELDS = frozenset({'code', 'message'})
_ERROR_BODY = 'AvitoErrorBody'
COMMON = 'common'
SHARED = '_shared'
_SAFE_REFS = …
_PASCAL = re.compile('\\b[A-Z][A-Za-z0-9]+\\b')

dedup_shared(domains: list[GeneratedDomain) -> dict[str, str]

_signature(model: ModelSpec) -> Signature

_is_error_shaped(model: ModelSpec) -> bool

_shareable(model: ModelSpec, refs_ok: bool = True) -> bool
  # A model with fields whose annotations reference nothing domain-local.

_rewrite(text: str, renames: dict[str, str) -> str

_apply_renames(gen: GeneratedDomain, renames: dict[str, str) -> None
  # Rewrite every annotation/assignment in ``gen`` that names a renamed model.

_collapse_error_bodies(domains: list[GeneratedDomain) -> None
  # Pass A — map every ``{code, message}`` model onto ``common.AvitoErrorBody``.

_collapse_by_shape(domains: list[GeneratedDomain) -> dict[str, ModelSpec]

_collapse_identical(domains: list[GeneratedDomain) -> dict[str, ModelSpec]
  # Pass B — move same-name, same-signature, cross-domain models to ``models/_shared.py``.

_render_shared_module(shared: dict[str, ModelSpec) -> str

_render_model(model: ModelSpec) -> str

_needs(text: str) -> set[str]

shared_import_lines(gen: GeneratedDomain, text: str) -> list[str]
  # Import lines for the shared models ``gen`` references — relative to the emitter's package.

```

## emit_enums.py
```
# Render ``enums/<module>.py`` — one ``StrEnum`` per generated enum for the domain.


emit(gen: GeneratedDomain) -> str

_render_enum(enum: EnumSpec) -> str

```

## emit_facade.py
```
# Render ``facade/<module>.py`` — a mixin class of endpoint methods inherited by ``Client``.


_base_type(annotation: str) -> str
  # Drop ``| None`` unions and whitespace to get the leading type name.

facade_class(module: str) -> str

emit(gen: GeneratedDomain) -> str

_signature_text(gen: GeneratedDomain) -> str

_import_block(gen: GeneratedDomain, text: str) -> str

_return_annotation(m: MethodSpec) -> str

_facade_fields(m: MethodSpec, models: dict[str, ModelSpec) -> tuple[list[FieldSpec], list[str]]

_render_call(m: MethodSpec, models: dict[str, ModelSpec) -> str

```

## emit_methods.py
```
# Render ``methods/<module>.py`` — one ``BaseMethod``/``PageMethod`` subclass per endpoint.


emit(gen: GeneratedDomain) -> str

_scan_text(gen: GeneratedDomain) -> str

_import_block(gen: GeneratedDomain, text: str) -> str

_needs(text: str) -> set[str]

_render_method(m: MethodSpec, note: str) -> str

```

## emit_models.py
```
# Render ``models/<module>.py`` — DTOs (extend ``AvitoObject``) + generated bound methods.


emit(gen: GeneratedDomain) -> str

_scan_text(gen: GeneratedDomain) -> str

_import_block(gen: GeneratedDomain, text: str) -> str

_needs(text: str) -> set[str]

_render_model(gen: GeneratedDomain, model: ModelSpec) -> str

_render_bound(gen: GeneratedDomain, bm: BoundMethod) -> str

```

## entities.py
```
# Bound-method inference — link entity models to the operations that act on them.


cls Entity: token: str, model: str, self_attr: str
  # A model that owns bound methods.

cls BoundArg: name: str, annotation: str, required: bool, default_expr: str | None
  # One argument of a generated bound method.

cls BoundMethod: owner_model: str, method_name: str, method_class: str, args: tuple[BoundArg, ...], fills: tuple[tuple[str, str], ...]
  # A bound method to emit onto an entity model.

_self_attr_for(token: str, model_fields: frozenset[str) -> str | None

detect_entities(domain: Domain, model_fields: dict[str, frozenset[str) -> dict[str, Entity]
  # Map each entity path token in ``domain`` to its :class:`Entity`.

_bind(op: Operation, entities: dict[str, Entity, field_specs: dict[str, FieldSpec) -> BoundMethod | None

bound_methods(domain: Domain, entities: dict[str, Entity, field_specs: dict[str, FieldSpec) -> dict[str, list[BoundMethod]]
  # Group bound methods by owner model class name.

```

## generate.py
```
# Top-level driver — spec → source files per domain, written under ``avitoapi/``.

_PACKAGE_ROOT = Path(__file__).resolve().parent.parent.parent

build_one(slug: str) -> GeneratedDomain
  # Fetch + parse + build one domain into a :class:`GeneratedDomain` (no emit).

emit_one(gen: GeneratedDomain) -> dict[str, str]
  # Render one already-built domain to ``{relative_path: source}``.

render_domain(slug: str) -> dict[str, str]
  # Return ``{relative_path: source}`` for one domain's enums/models/methods/facade.

build_all(slugs: list[str) -> list[GeneratedDomain]
  # Build every domain in ``slugs`` before any emission (phase one of ``--all``).

apply_global_passes(domains: list[GeneratedDomain) -> dict[str, str]

write_files(files: dict[str, str) -> list[Path]
  # Write rendered sources under the package root; return the paths written.

format_files(paths: list[Path) -> None
  # Run ruff format + autofix over the generated files (best-effort).

generate(slug: str) -> dict[str, str]

generate_all() -> dict[str, str]
  # Regenerate every domain two-phase: build all → global passes → emit → write.

all_slugs() -> list[str]

```

## naming.py
```
# Name normalisation — camelCase spec identifiers → Python house style.

_PLACEHOLDER = re.compile('\\{(\\w+)\\}')
_TOKEN = …
_SHADOWS_TYPE = frozenset({'date', 'datetime', 'any'})
_STRIP_VERB_PREFIXES = ('post_',)

_words(raw: str) -> list[str]
  # Split ``raw`` into lowercase word tokens across camelCase, acronyms, and separators.

snake(raw: str) -> str
  # ``userId`` / ``user-id`` / ``UserID`` → ``user_id`` (keyword- and type-shadow-safe).

pascal(raw: str) -> str
  # ``getItemInfo`` → ``GetItemInfo``; safe for a class identifier.

class_name_for_operation(operation_id: str) -> str
  # Method-class name from an ``operationId``.

facade_method_name(class_name: str) -> str

enum_class_name(owner: str, field: str) -> str
  # StrEnum name for an inline enum on ``owner.field``.

normalise_endpoint(path: str) -> str
  # Rewrite ``{userId}``/``{itemId}`` placeholders to their snake_case field names.

placeholders(path: str) -> list[str]
  # Snake-cased placeholder names in ``path`` (post-:func:`normalise_endpoint`).

```

## render.py
```
# Pure text-emit helpers — import blocks, docstrings, field lines.

GENERATED_HEADER = …
_TYPE_IMPORTS = …

module_doc(title: str, kind: str) -> str

docstring(lines: Iterable[str, indent: str = '    ') -> str

class_docstring(summary: str, section: str, items: Iterable[tuple[str, str?, indent: str = '    ', note: str? = None) -> str

datetime_imports(needs: set[str) -> list[str]
  # Return import lines for the datetime/house type tokens actually used.

field_line(name: str, annotation: str, assignment: str?) -> str
  # Render one field line — bare (``name: T``) when ``assignment`` is ``None``.

```

## types.py
```
# Schema → Python type + ``Field(...)`` mapping, with enum / nested-model collection.

_ENUM_INVALID = re.compile('\\W+')
_TRANSLIT = …
_HTML_TAG = re.compile('<[^>]+>')
_WS = re.compile('\\s+')
_BACKTICK = re.compile('`([^`]+)`')
_ENUM_TOKEN = re.compile('^[A-Za-z][A-Za-z0-9_]*$')

cls FieldSpec: name: str, annotation: str, assignment: str | None, wire_name: str, description: str | None, required: bool, default_expr: str | None

cls ModelSpec: name: str, fields: list[FieldSpec], doc: str | None
  # A generated Pydantic model.

cls EnumSpec: name: str, members: list[tuple[str, str]]
  # A generated ``StrEnum``.

cls Resolved: annotation: str, needs: frozenset[str]
  # Result of mapping one schema node.

cls ModelBuilder
  # Builds model/enum specs and maps schema nodes to Python types for one domain.
  __init__(domain: Domain) -> None
  build() -> None
    # Emit a model / enum / root-model for every top-level component schema.
  model_from_inline(name: str, schema: dict[str, Any) -> str
    # Register a model from an inline (non-component) object schema; return its name.
  resolve(schema: dict[str, Any, owner: str, field_name: str) -> Resolved
    # Map a schema node to a Python annotation, registering nested types.
  field_spec(name: str, wire: str, schema: dict[str, Any, required: bool, owner: str, description: str? = None) -> FieldSpec

_translit(text: str) -> str

_enum_member(value: str) -> str

_escape(text: str) -> str

_clean_desc(text: str) -> str
  # Strip HTML tags (``<br/>`` …) and collapse whitespace in a description; keep markdown.

_desc_enum_values(description: str) -> list[str] | None

_dedup_members(members: list[tuple[str, str) -> list[tuple[str, str]]
  # De-dup enum member names (distinct values can sanitise to the same identifier).

_is_object(schema: dict[str, Any) -> bool

_constraint_kwargs(schema: dict[str, Any) -> list[str]

_literal(value: Any) -> str

build_models(domain: Domain) -> ModelBuilder
  # Convenience: construct a :class:`ModelBuilder` and run :meth:`ModelBuilder.build`.

```

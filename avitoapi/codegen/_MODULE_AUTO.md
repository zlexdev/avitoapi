# codegen/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

> avitoapi codegen — the auto-builder.

## Submodules

- [`engine/`](engine\_MODULE_AUTO.md) (12 py, 10 cls, 75 fn)

## __init__.py
```
# avitoapi codegen — the auto-builder.


```

## __main__.py
```
# CLI — ``python -m avitoapi.codegen [--slug item | --all] [--dry-run] [--no-cache]``.


main(argv: list[str]? = None) -> int

```

## config.py
```
# Codegen configuration — the small curated tables the auto-builder needs.


module_for_slug(slug: str) -> str
  # Return the ``methods/<name>.py`` basename for an OpenAPI ``slug``.

```

## fetch.py
```
# Spec fetching — pull the Avito OpenAPI catalogue and per-domain specs.

_CACHE_DIR = Path(__file__).parent / '_spec_cache'
_USER_AGENT = 'avitoapi-codegen/1.0'
_TIMEOUT = 40

cls SpecFetchError(RuntimeError)
  # Raised when a spec cannot be fetched or parsed.

cls DomainInfo: slug: str, title: str, description: str
  # One entry from ``/openapi/list``.

_get(url: str) -> str

list_domains() -> list[DomainInfo]
  # Return every API domain published in the catalogue.

fetch_spec(slug: str) -> dict[str, Any]
  # Return the parsed OpenAPI 3.0 document for ``slug`` (disk-cached).

```

## parser.py
```
# OpenAPI 3.0 → intermediate representation.

_HTTP_VERBS = …

cls SpecError(RuntimeError)
  # Raised on a malformed or unresolvable spec.

cls Param: name: str, wire_name: str, location: str, schema: dict[str, Any], required: bool, description: str | None
  # A path or query parameter of an operation.

cls Prop: name: str, wire_name: str, schema: dict[str, Any], required: bool, description: str | None
  # A property of a schema / flattened request-body field.

cls Operation: class_name: str, operation_id: str, http_method: str, endpoint: str, path_params: tuple[Param, ...], query_params: tuple[Param, ...], body_props: tuple[Prop, ...], body_ref: str | None, body_required: bool, multipart: bool, … (16)
  # One endpoint call — becomes a ``BaseMethod`` subclass.

cls Domain: slug: str, title: str, operations: list[Operation], schemas: dict[str, dict[str, Any]]
  # A whole API domain: its operations plus the raw component schemas they reference.

cls Resolver
  # Resolves ``$ref`` pointers within a single spec document.
  __init__(spec: dict[str, Any) -> None
  ref_name(ref: str) -> str
    # ``#/components/schemas/Item`` → ``Item``.
  resolve(node: dict[str, Any) -> dict[str, Any]
    # Follow a single ``$ref`` (if present); otherwise return ``node`` unchanged.

_norm_param(raw: dict[str, Any, resolver: Resolver) -> Param | None

_flatten_body(op: dict[str, Any, resolver: Resolver) -> tuple[tuple[Prop, ...], str | None, bool, bool]
  # Return (body_props, body_ref, required, multipart) from an operation's requestBody.

_props_of(schema: dict[str, Any) -> tuple[Prop, ...]

_response(op: dict[str, Any, resolver: Resolver) -> tuple[str | None, dict[str, Any] | None, bool]
  # Return (response_ref, inline_object_schema, is_binary) for the success response.

build_domain(slug: str, title: str, spec: dict[str, Any) -> Domain
  # Parse a full spec document into a :class:`Domain` IR.

```

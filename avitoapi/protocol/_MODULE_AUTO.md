# protocol/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

> Wire-protocol abstraction. See ``_MODULE.md``.

## base.py
```
# ``Protocol`` ABC — separates wire-encoding from method-class intent.


cls Protocol(ABC)
  validate_subclass(method_cls: type[BaseMethod[Any) -> None
    # Hook called from ``BaseMethod.__init_subclass__``. Default = no extra checks.
  async build_request(method: BaseMethod[Any, ctx: RequestContext) -> PreparedRequest
  decode_response(method: BaseMethod[Any, raw: RawResponse) -> Any
    # Validate the raw response body into ``method.__returning__`` (or None).
  is_idempotent(method: BaseMethod[Any) -> bool
    # Return ``True`` when the request may be retried without side-effect risk.

```

## rest.py
```
# Default REST protocol — path templating, verb routing, JSON encode/decode.


cls RestProtocol(Protocol)
  validate_subclass(method_cls: type[BaseMethod[Any) -> None
  async build_request(method: BaseMethod[Any, ctx: RequestContext) -> PreparedRequest
  decode_response(method: BaseMethod[Any, raw: RawResponse) -> Any
  is_idempotent(method: BaseMethod[Any) -> bool

```

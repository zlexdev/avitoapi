# tests/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

## Submodules

- [`unit/`](unit\_MODULE_AUTO.md) (48 py, 25 cls, 402 fn)

## _fake_session.py
```
# FakeSession — playback-only stand-in for BaseSession.

FIXTURE_DIR = Path(__file__).parent / 'fixtures'

cls FakeResponse
  # Canned response payload + status + headers.
  __init__(body: bytes | str | dict[str, Any] | list[Any, status: int = 200, headers: dict[str, str]? = None) -> None

cls FakeSession(BaseSession)
  __init__() -> None
  register(method_cls: type[BaseMethod[Any, body: bytes | str | dict[str, Any] | list[Any, status: int = 200, headers: dict[str, str]? = None) -> None
    # Register a canned response for one method-class. Latest wins.
  register_responder(method_cls: type[BaseMethod[Any, responder: Callable[[PreparedRequest], FakeResponse) -> None
    # Register a dynamic responder for a method-class.
  register_route(http_method: str, url_path: str, body: bytes | str | dict[str, Any] | list[Any, status: int = 200, headers: dict[str, str]? = None) -> None
    # Register a canned response keyed by ``(http_method, url_path)``.
  register_route_responder(http_method: str, url_path: str, responder: Callable[[PreparedRequest], FakeResponse) -> None
  bind_fixture(method_cls: type[BaseMethod[Any, fixture_name: str, status: int = 200) -> None
    # Bind a fixture file (under ``tests/fixtures/``) to a method-class.
  set_default(body: bytes | str | dict[str, Any] | list[Any, status: int = 200) -> None
  call_count(method_cls: type[BaseMethod[Any) -> int
  reset() -> None
  async open() -> None
  async close() -> None

```

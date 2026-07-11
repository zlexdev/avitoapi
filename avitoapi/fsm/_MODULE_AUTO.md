# fsm/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

> FSM primitives — in-package implementation, no external dependency.

## __init__.py
```
# FSM primitives — in-package implementation, no external dependency.


```

## _fallback.py
```
# In-tree FSM implementation.


cls FSMStorageProtocol(Protocol)
  async get_state(key: StorageKey) -> str | None
  async set_state(key: StorageKey, state: str?) -> None
  async get_data(key: StorageKey) -> dict[str, Any]
  async set_data(key: StorageKey, data: dict[str, Any) -> None
  async clear(key: StorageKey) -> None

cls State
  __init__(state: str? = None) -> None

cls _StatesGroupMeta(type)

cls StatesGroup
  # Container for related :class:`State` declarations.

cls MemoryFSMStorage
  __init__() -> None
  async get_state(key: StorageKey) -> str | None
  async set_state(key: StorageKey, state: str?) -> None
  async get_data(key: StorageKey) -> dict[str, Any]
  async set_data(key: StorageKey, data: dict[str, Any) -> None
  async clear(key: StorageKey) -> None

cls FSMContext
  # Per-key FSM facade backed by any :class:`FSMStorageProtocol` backend.
  __init__(storage: FSMStorageProtocol, key: StorageKey) -> None
  async get_state() -> str | None
  async set_state(state: State | str?) -> None
  async get_data() -> dict[str, Any]
  async set_data(data: dict[str, Any) -> None
  async update_data(**kwargs: Any) -> dict[str, Any]
  async clear() -> None

cls StateFilter
  __init__(*states: State | str?) -> None

```

## key_builder.py
```
# Avito-specific storage-key builder for FSM contexts.


cls StorageKey: account_id: str, chat_id: str

cls AvitoStorageKeyBuilder
  build(account_id: str | int, chat_id: str | int) -> StorageKey
    # Construct a :class:`StorageKey`. Inputs are stringified for stability.

```

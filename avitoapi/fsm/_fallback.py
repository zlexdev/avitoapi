"""In-tree FSM implementation.

Covers the subset handlers actually call: ``get_state``, ``set_state``,
``get_data``, ``set_data``, ``update_data``, ``clear``, plus a metaclass
that auto-prefixes ``State`` names with their owning group so
``ChatStates.idle.state == "ChatStates:idle"``.
"""

from __future__ import annotations

import asyncio
import copy
from typing import Any

from .key_builder import StorageKey


class State:
    """Single named state inside a :class:`StatesGroup`.

    The actual string identifier is set by :class:`StatesGroup`'s metaclass
    so callers never write ``"ChatStates:idle"`` by hand.
    """

    __slots__ = ("_attr_name", "_group_name", "state")

    def __init__(self, state: str | None = None) -> None:
        self.state: str = state or ""
        self._group_name: str = ""
        self._attr_name: str = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self._attr_name = name

    def __get__(self, instance: object, owner: type | None = None) -> State:
        return self

    def __eq__(self, other: object) -> bool:
        if isinstance(other, State):
            return self.state == other.state
        if isinstance(other, str):
            return self.state == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.state)

    def __repr__(self) -> str:
        return f"State({self.state!r})"


class _StatesGroupMeta(type):
    def __new__(
        mcls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
    ) -> _StatesGroupMeta:
        cls = super().__new__(mcls, name, bases, namespace)
        for attr_name, value in list(namespace.items()):
            if isinstance(value, State):
                value._group_name = name
                value._attr_name = attr_name
                value.state = f"{name}:{attr_name}"
        return cls


class StatesGroup(metaclass=_StatesGroupMeta):
    """Container for related :class:`State` declarations."""


class MemoryFSMStorage:
    """In-process FSM storage backend keyed by :class:`StorageKey`.

    State and data live under separate inner keys so wiping one doesn't
    wipe the other. ``asyncio.Lock`` guards concurrent updates from
    parallel handler runs.
    """

    def __init__(self) -> None:
        self._state: dict[str, str | None] = {}
        self._data: dict[str, dict[str, Any]] = {}
        self._lock: asyncio.Lock = asyncio.Lock()

    async def get_state(self, key: StorageKey) -> str | None:
        rendered = key.render()
        async with self._lock:
            return self._state.get(rendered)

    async def set_state(self, key: StorageKey, state: str | None) -> None:
        rendered = key.render()
        async with self._lock:
            if state is None:
                self._state.pop(rendered, None)
            else:
                self._state[rendered] = state

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        rendered = key.render()
        async with self._lock:
            return copy.deepcopy(self._data.get(rendered, {}))

    async def set_data(self, key: StorageKey, data: dict[str, Any]) -> None:
        rendered = key.render()
        async with self._lock:
            self._data[rendered] = copy.deepcopy(data)

    async def clear(self, key: StorageKey) -> None:
        rendered = key.render()
        async with self._lock:
            self._state.pop(rendered, None)
            self._data.pop(rendered, None)


class FSMContext:
    """Per-key FSM facade backed by a :class:`MemoryFSMStorage` (or compatible)."""

    def __init__(self, storage: MemoryFSMStorage, key: StorageKey) -> None:
        self.storage = storage
        self.key = key

    async def get_state(self) -> str | None:
        return await self.storage.get_state(self.key)

    async def set_state(self, state: State | str | None) -> None:
        if state is None:
            await self.storage.set_state(self.key, None)
            return
        value = state.state if isinstance(state, State) else state
        await self.storage.set_state(self.key, value)

    async def get_data(self) -> dict[str, Any]:
        return await self.storage.get_data(self.key)

    async def set_data(self, data: dict[str, Any]) -> None:
        await self.storage.set_data(self.key, data)

    async def update_data(self, **kwargs: Any) -> dict[str, Any]:
        current = await self.storage.get_data(self.key)
        current.update(kwargs)
        await self.storage.set_data(self.key, current)
        return current

    async def clear(self) -> None:
        await self.storage.clear(self.key)


class StateFilter:
    """Async predicate matching when an :class:`FSMContext`'s state is in ``states``.

    Pass ``None`` to match cleared contexts.
    """

    def __init__(self, *states: State | str | None) -> None:
        self._states: tuple[State | str | None, ...] = states

    async def __call__(self, ctx: FSMContext) -> bool:
        current = await ctx.get_state()
        for state in self._states:
            target = state.state if isinstance(state, State) else state
            if current == target:
                return True
        return False

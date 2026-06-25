"""FSM primitives — in-package implementation, no external dependency.

Covers ``FSMContext`` (``get_state`` / ``set_state`` / ``get_data`` /
``set_data`` / ``update_data`` / ``clear``) and the metaclass-based
``StatesGroup`` shape, keyed by :class:`StorageKey`.
"""

from __future__ import annotations

from ._fallback import (
    FSMContext,
    FSMStorageProtocol,
    MemoryFSMStorage,
    State,
    StateFilter,
    StatesGroup,
)
from .key_builder import AvitoStorageKeyBuilder, StorageKey

__all__ = [
    "AvitoStorageKeyBuilder",
    "FSMContext",
    "FSMStorageProtocol",
    "MemoryFSMStorage",
    "State",
    "StateFilter",
    "StatesGroup",
    "StorageKey",
]

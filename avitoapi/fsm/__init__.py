"""FSM re-export — :mod:`evented` primitives when installed, in-house fallback otherwise.

When :mod:`evented` is importable, its primitives are re-exported verbatim.
Otherwise the local stand-ins cover ``FSMContext.get_state`` /
``set_state`` / ``get_data`` / ``set_data`` / ``update_data`` / ``clear``
and the metaclass-based ``StatesGroup`` shape, keeping handler code
working against either backend.
"""
from __future__ import annotations

from .key_builder import AvitoStorageKeyBuilder, StorageKey

try:
    from evented import (  # type: ignore[import-not-found]
        FSMContext,
        State,
        StateFilter,
        StatesGroup,
    )
    from evented.storage import MemoryFSMStorage  # type: ignore[import-not-found]
    _EVENTED_AVAILABLE = True
except ImportError:
    from ._fallback import (
        FSMContext,
        MemoryFSMStorage,
        State,
        StateFilter,
        StatesGroup,
    )
    _EVENTED_AVAILABLE = False

__all__ = [
    "AvitoStorageKeyBuilder",
    "FSMContext",
    "MemoryFSMStorage",
    "State",
    "StateFilter",
    "StatesGroup",
    "StorageKey",
]

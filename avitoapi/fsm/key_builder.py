"""Avito-specific storage-key builder for FSM contexts.

Avito's per-account chat model maps cleanly onto an ``(account_id, chat_id)``
identity. :class:`AvitoStorageKeyBuilder` wraps that pair into a
:class:`StorageKey` instance and renders the on-disk key so two different
accounts talking about the same ``chat_id`` never collide in storage.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StorageKey:
    """Composite FSM identity. Both fields are required.

    The ``StorageKey`` is the unit of identity passed to :class:`FSMContext`;
    one key = one independent state machine instance.
    """

    account_id: str
    chat_id: str

    def render(self) -> str:
        """Render the stable string used as the underlying storage key."""

        return f"fsm:{self.account_id}:{self.chat_id}"

    def __str__(self) -> str:
        return self.render()


class AvitoStorageKeyBuilder:
    """Build :class:`StorageKey` from raw ``(account_id, chat_id)`` inputs.

    Both arguments are coerced to strings so callers passing ``int``
    ``user_id``s don't trip the equality check that drives FSM lookups.
    """

    def build(self, account_id: str | int, chat_id: str | int) -> StorageKey:
        """Construct a :class:`StorageKey`. Inputs are stringified for stability."""

        return StorageKey(account_id=str(account_id), chat_id=str(chat_id))

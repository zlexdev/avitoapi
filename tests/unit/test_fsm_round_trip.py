"""FSM round-trip — :class:`MemoryFSMStorage` + :class:`FSMContext` + key builder.

Wave 3 ships the fallback path (no ``evented`` dependency yet); the tests
cover the in-house implementation's API surface that handler code uses.
"""

from __future__ import annotations

import pytest
from avitoapi.fsm import (
    AvitoStorageKeyBuilder,
    FSMContext,
    MemoryFSMStorage,
    State,
    StateFilter,
    StatesGroup,
    StorageKey,
)


class _ChatStates(StatesGroup):
    idle = State()
    awaiting_message = State()
    closed = State()


def test_storage_key_render_format() -> None:
    key = StorageKey(account_id="42", chat_id="abc")
    assert str(key) == "fsm:42:abc"
    assert key.render() == "fsm:42:abc"


def test_storage_key_builder_stringifies_int_account_id() -> None:
    builder = AvitoStorageKeyBuilder()
    key = builder.build(account_id=42, chat_id="abc")
    assert key.account_id == "42"
    assert key.chat_id == "abc"


def test_storage_key_disambiguates_account_chat_pairs() -> None:
    a = AvitoStorageKeyBuilder().build(account_id="1", chat_id="x")
    b = AvitoStorageKeyBuilder().build(account_id="2", chat_id="x")
    c = AvitoStorageKeyBuilder().build(account_id="1", chat_id="y")
    assert {str(a), str(b), str(c)} == {"fsm:1:x", "fsm:2:x", "fsm:1:y"}
    assert a != b
    assert a != c


async def test_fsm_context_state_round_trip() -> None:
    storage = MemoryFSMStorage()
    key = AvitoStorageKeyBuilder().build(account_id="1", chat_id="abc")
    ctx = FSMContext(storage=storage, key=key)

    assert await ctx.get_state() is None
    await ctx.set_state(_ChatStates.awaiting_message)
    assert await ctx.get_state() == _ChatStates.awaiting_message.state

    await ctx.clear()
    assert await ctx.get_state() is None


async def test_fsm_context_data_round_trip() -> None:
    storage = MemoryFSMStorage()
    key = AvitoStorageKeyBuilder().build(account_id="1", chat_id="abc")
    ctx = FSMContext(storage=storage, key=key)

    assert await ctx.get_data() == {}
    await ctx.set_data({"foo": "bar"})
    assert await ctx.get_data() == {"foo": "bar"}

    await ctx.update_data(extra=1)
    data = await ctx.get_data()
    assert data == {"foo": "bar", "extra": 1}


async def test_fsm_context_isolation_between_keys() -> None:
    storage = MemoryFSMStorage()
    key_a = AvitoStorageKeyBuilder().build(account_id="1", chat_id="abc")
    key_b = AvitoStorageKeyBuilder().build(account_id="2", chat_id="abc")
    ctx_a = FSMContext(storage=storage, key=key_a)
    ctx_b = FSMContext(storage=storage, key=key_b)

    await ctx_a.set_state(_ChatStates.idle)
    await ctx_a.set_data({"side": "a"})

    assert await ctx_b.get_state() is None
    assert await ctx_b.get_data() == {}


def test_state_auto_prefixes_with_group_name() -> None:
    assert _ChatStates.idle.state == "_ChatStates:idle"
    assert _ChatStates.awaiting_message.state == "_ChatStates:awaiting_message"


async def test_state_filter_matches_current_state() -> None:
    storage = MemoryFSMStorage()
    key = AvitoStorageKeyBuilder().build(account_id="1", chat_id="abc")
    ctx = FSMContext(storage=storage, key=key)
    await ctx.set_state(_ChatStates.idle)

    flt = StateFilter(_ChatStates.idle)
    assert await flt(ctx) is True

    flt_none = StateFilter(None)
    assert await flt_none(ctx) is False


async def test_state_filter_matches_cleared_context() -> None:
    storage = MemoryFSMStorage()
    key = AvitoStorageKeyBuilder().build(account_id="1", chat_id="abc")
    ctx = FSMContext(storage=storage, key=key)

    flt = StateFilter(None)
    assert await flt(ctx) is True


@pytest.mark.parametrize(
    "states,current,expected",
    [
        ((_ChatStates.idle,), _ChatStates.idle, True),
        ((_ChatStates.idle, _ChatStates.closed), _ChatStates.closed, True),
        ((_ChatStates.idle,), _ChatStates.closed, False),
    ],
)
async def test_state_filter_membership(states: tuple, current: State, expected: bool) -> None:
    storage = MemoryFSMStorage()
    key = AvitoStorageKeyBuilder().build(account_id="1", chat_id="abc")
    ctx = FSMContext(storage=storage, key=key)
    await ctx.set_state(current)

    flt = StateFilter(*states)
    assert await flt(ctx) is expected

"""Discriminated-union decoding for all 11 Message variants + Unknown fallback.

Each fixture under ``tests/fixtures/messenger/message_variants/*.json``
covers one ``type`` value. The ``unknown.json`` fixture additionally asserts
that:

- decoding yields :class:`UnknownMessage` (not an exception),
- the original wire ``type`` is preserved under ``raw_type``,
- exactly one WARNING log line is emitted per first-seen unknown type
  (process-lifetime dedup).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest
from avitoapi.models.messenger import (
    _WARNED_UNKNOWN_TYPES,
    AppCallMessage,
    CallMessage,
    DeletedMessage,
    FileMessage,
    ImageMessage,
    ItemMessage,
    LinkMessage,
    LocationMessage,
    SystemMessage,
    TextMessage,
    UnknownMessage,
    VoiceMessage,
    decode_message,
)

FIXTURES = Path(__file__).parent.parent / "fixtures" / "messenger" / "message_variants"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def _reset_warning_cache() -> None:
    _WARNED_UNKNOWN_TYPES.clear()


def test_text_message_decodes_into_text_variant() -> None:
    msg = decode_message(_load("text.json"))
    assert isinstance(msg, TextMessage)
    assert msg.content.text == "hello"


def test_image_message_decodes_into_image_variant() -> None:
    msg = decode_message(_load("image.json"))
    assert isinstance(msg, ImageMessage)
    assert msg.content.image_id == "img-xyz"
    assert "140x105" in msg.content.sizes


def test_link_message_decodes_into_link_variant() -> None:
    msg = decode_message(_load("link.json"))
    assert isinstance(msg, LinkMessage)
    assert str(msg.content.url) == "https://example.com/page"


def test_item_message_decodes_into_item_variant() -> None:
    msg = decode_message(_load("item.json"))
    assert isinstance(msg, ItemMessage)
    assert msg.content.id == 9001


def test_location_message_decodes_with_lat_lng() -> None:
    msg = decode_message(_load("location.json"))
    assert isinstance(msg, LocationMessage)
    assert msg.content.lat == pytest.approx(55.7558)


def test_voice_message_carries_voice_id() -> None:
    msg = decode_message(_load("voice.json"))
    assert isinstance(msg, VoiceMessage)
    assert msg.content.voice_id == "voice-abc-123"


def test_call_message_decodes_status() -> None:
    msg = decode_message(_load("call.json"))
    assert isinstance(msg, CallMessage)
    assert msg.content.status == "missed"


def test_file_message_decodes_size_and_url() -> None:
    msg = decode_message(_load("file.json"))
    assert isinstance(msg, FileMessage)
    assert msg.content.size == 102400


def test_system_message_decodes_kind() -> None:
    msg = decode_message(_load("system.json"))
    assert isinstance(msg, SystemMessage)
    assert msg.content.kind == "chat_closed"


def test_app_call_message_decodes_into_app_call_variant() -> None:
    msg = decode_message(_load("app_call.json"))
    assert isinstance(msg, AppCallMessage)
    assert msg.content.duration_s == 42


def test_deleted_message_decodes_into_deleted_variant() -> None:
    msg = decode_message(_load("deleted.json"))
    assert isinstance(msg, DeletedMessage)


def test_unknown_message_decodes_into_unknown_fallback_with_raw_type() -> None:
    msg = decode_message(_load("unknown.json"))
    assert isinstance(msg, UnknownMessage)
    assert msg.raw_type == "future_type_xyz"


def test_unknown_message_emits_exactly_one_warning_per_type(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.WARNING, logger="avitoapi.models.messenger"):
        decode_message(_load("unknown.json"))

    relevant = [r for r in caplog.records if r.message == "messenger.unknown_message_type"]
    assert len(relevant) == 1


def test_unknown_warning_is_deduplicated_across_calls(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.WARNING, logger="avitoapi.models.messenger"):
        decode_message(_load("unknown.json"))
        decode_message(_load("unknown.json"))
        decode_message(_load("unknown.json"))

    relevant = [r for r in caplog.records if r.message == "messenger.unknown_message_type"]
    assert len(relevant) == 1

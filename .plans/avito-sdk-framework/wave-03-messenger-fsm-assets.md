# Wave 03 — Messenger + FSM + Assets

## Delivers
Full messenger v2/v3 surface, discriminated `Message` model, FSM
re-export, asset downloader for voice / image URLs returned by the API.

## Releasable definition
- [ ] 12 messenger endpoints work end-to-end vs. FakeSession fixtures.
- [ ] `Message` decodes all 11 documented `type` variants into typed subclasses
      via Pydantic discriminated union; unknown types → `UnknownMessage`.
- [ ] `await chat.send_text("hi")`, `await chat.mark_read()`,
      `await message.reply("...")` bound methods work.
- [ ] FSM round-trip with `MemoryStorage` works; `StorageKey(account_id, chat_id)` keying.
- [ ] `await client.upload_image(path)` multipart POST tested.
- [ ] `ruff` + `mypy --strict` clean.

## Logic
- New `methods/messenger.py` with: `ListChats`, `GetChat`, `ListMessages`,
  `SendTextMessage`, `SendImageMessage`, `MarkChatRead`, `DeleteMessage`,
  `UploadImage`, `ListBlacklist`, `AddBlacklist`, `RemoveBlacklist`,
  `GetVoiceFiles`.
- New `models/messenger.py` with `Chat`, `Message` (discriminated union on
  `type`), and 11 message subclasses (`TextMessage`, `ImageMessage`, …).
  `ChatState: StrEnum = active | archived | blocked`.
- New `fsm/` package — thin re-export of `evented.FSMContext`,
  `evented.State`, `evented.StatesGroup`, `evented.StateFilter` +
  Avito-specific `StorageKeyBuilder` that keys on `(account_id, chat_id)`.
- New `assets/` package — `AssetDownloader` (bounded `download_many`),
  `FileStorage` ABC + `LocalFileStorage` + `MemoryFileStorage`,
  `FileCache` (TTL wrapper).
- `UploadImage` method-class is special: `__protocol__` stays `RestProtocol`
  but RestProtocol detects `bytes`/`PathLike` fields and switches body
  encoding to `multipart/form-data`.

## Files (additions)
```
avitoapi/
├── methods/messenger.py
├── models/messenger.py
├── fsm/__init__.py
├── fsm/_MODULE.md
├── fsm/key_builder.py          ← AvitoStorageKeyBuilder
├── assets/__init__.py
├── assets/_MODULE.md
├── assets/downloader.py        ← AssetDownloader (single + bounded download_many)
├── assets/file_cache.py        ← FileCache (TTL wrapper)
└── assets/file_storage/
    ├── __init__.py
    ├── base.py                 ← FileStorage ABC (binary K/V)
    ├── memory.py               ← MemoryFileStorage
    └── local.py                ← LocalFileStorage (sha256 filenames)
tests/
├── unit/test_messenger.py
├── unit/test_message_discriminated_union.py
├── unit/test_fsm_round_trip.py
├── unit/test_upload_multipart.py
└── fixtures/messenger/
    ├── chats_list.json
    ├── chat_detail.json
    ├── messages_p1.json
    ├── messages_p2.json
    ├── upload_image_response.json
    ├── message_variants/*.json (11 files, one per type)
    └── message_variants/unknown.json  ← (G5 from review) regression: future_type_xyz → UnknownMessage + WARN log
```

## Types
- `Chat(BoundModel)` — `id`, `state: ChatState`, `participants: list[Participant]`,
  `item: ItemRef | None`, `last_message: Message | None`,
  `unread_count: int`. Bound: `send_text(text)`, `send_image(path)`,
  `mark_read()`, `archive()`, `list_messages()` → paginator.
- `Message(BoundModel)` — discriminator on `type`. Subclasses:
  `TextMessage`, `ImageMessage`, `LinkMessage`, `ItemMessage`,
  `LocationMessage`, `VoiceMessage`, `CallMessage`, `FileMessage`,
  `SystemMessage`, `AppCallMessage`, `DeletedMessage`. Each subclass owns
  its `content`-shape fields. Bound: `reply(text)`, `delete()`.

## Tasks
```yaml
- id: W3-T1
  title: "models/messenger.py — Chat + Message discriminated union"
  files: [avitoapi/models/messenger.py]
  depends_on: []
  parallelizable: true

- id: W3-T2
  title: "methods/messenger.py — 12 methods incl. multipart upload"
  files: [avitoapi/methods/messenger.py]
  depends_on: [W3-T1]
  parallelizable: false

- id: W3-T3
  title: "RestProtocol multipart support"
  files: [avitoapi/protocol/rest.py]
  depends_on: []
  parallelizable: true

- id: W3-T4
  title: "fsm/ package (re-exports + key builder)"
  files: [avitoapi/fsm/*]
  depends_on: []
  parallelizable: true

- id: W3-T5
  title: "assets/ package"
  files: [avitoapi/assets/**]
  depends_on: []
  parallelizable: true

- id: W3-T6
  title: "Client public methods + bound methods on Chat/Message"
  files: [avitoapi/client.py]
  depends_on: [W3-T2, W3-T3]
  parallelizable: false

- id: W3-T7
  title: "Tests: messenger fixtures + variant decoding + FSM + multipart"
  files: [tests/unit/test_messenger.py, tests/unit/test_message_*.py,
          tests/unit/test_fsm_*.py, tests/unit/test_upload_*.py,
          tests/fixtures/messenger/**]
  depends_on: [W3-T6]
  parallelizable: false
```

## Risks
- Discriminated union with 11 variants is fragile if Avito adds new types.
  Mitigation: `UnknownMessage` fallback subclass; logged at WARNING level
  once per new type.
- `evented` private dep: not installable without `GH_TOKEN`. CI needs the
  secret. Local dev with `GH_TOKEN` in env. Documented in `.env.example`
  and `README.md` setup section.

## Hardcodes introduced
| What | Where | Replaced in wave |
|---|---|---|
| 11 message-type variants enumerated explicitly | `models/messenger.py` | none (forward-compat via UnknownMessage; new types added as Avito ships them) |

## Hardcodes replaced
None.

## Acceptance checklist
- [ ] All 7 tasks land
- [ ] All 11 message variants decode + round-trip
- [ ] `unknown.json` decodes into `UnknownMessage` + emits exactly one WARNING (caplog)
- [ ] `mypy --strict avitoapi/models/messenger.py` passes (discriminated union sanity)
- [ ] Multipart upload test green
- [ ] FSM round-trip test green
- [ ] `evented` pinned in `pyproject.toml` (loose `@master` from W1 → tag pin happens in W4)

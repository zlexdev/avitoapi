# Wave 06 — Autoload + Calltracking + Job + Realty + Autoteka (post-release)

## Delivers
Closes the documented Avito Partner API surface. Pure breadth — no new
architecture, no new subsystem. Every method-class follows the same
pattern established in W1–W5.

## Releasable definition
- [ ] Every endpoint listed in `_research/raw/avito-api-surface.md §1.4`
      that is not already shipped has a `BaseMethod[T]` subclass, a
      `Client` flat method, and a Pydantic model in `models/`.
- [ ] Each new domain has at least one FakeSession fixture per method.
- [ ] `ruff` + `mypy --strict` clean. Minor bump to `v0.3.0`.

## Files (additions)
```
avitoapi/
├── methods/autoload.py         ← ItemStatus, ListReports, GetLastReport,
│                                  GetReport, GetCategoryFields, GetProfile,
│                                  UpdateProfile, UploadFile, ConvertId
├── methods/calltracking.py     ← GetCall, ListCalls, GetCallRecording (audio/mpeg)
├── methods/job.py              ← SearchResumes, GetResume, GetResumeContacts
├── methods/realty.py           ← ListBookings, GetCalendar, GetPeriodPrices,
│                                  UpdatePeriodPrices, ItemBookings
├── methods/autoteka.py         ← PreviewByVin, PreviewByRegnum, FullReport
├── models/autoload.py          ← AutoloadReport, AutoloadItemStatus(StrEnum), …
├── models/calltracking.py      ← Call, CallRecording, CallStatus(StrEnum)
├── models/job.py               ← Resume, ResumeContact, ResumeSearchQuery
├── models/realty.py            ← Booking, Calendar, PeriodPrice
└── models/autoteka.py          ← AutotekaPreview, AutotekaFullReport
tests/
├── unit/test_autoload.py
├── unit/test_calltracking.py
├── unit/test_job.py
├── unit/test_realty.py
├── unit/test_autoteka.py
└── fixtures/
    ├── autoload/*.json
    ├── calltracking/*.json
    ├── job/*.json
    ├── realty/*.json
    └── autoteka/*.json
```

## Tasks
```yaml
- id: W6-T1
  title: "Autoload domain (models + methods + Client + tests)"
  files: [avitoapi/models/autoload.py, avitoapi/methods/autoload.py,
          avitoapi/client.py, tests/unit/test_autoload.py,
          tests/fixtures/autoload/**]
  depends_on: []
  parallelizable: true

- id: W6-T2
  title: "Calltracking domain (incl. audio/mpeg streaming response)"
  files: [avitoapi/models/calltracking.py, avitoapi/methods/calltracking.py,
          avitoapi/client.py, tests/unit/test_calltracking.py,
          tests/fixtures/calltracking/**]
  depends_on: []
  parallelizable: true

- id: W6-T3
  title: "Job domain"
  files: [avitoapi/models/job.py, avitoapi/methods/job.py,
          avitoapi/client.py, tests/unit/test_job.py,
          tests/fixtures/job/**]
  depends_on: []
  parallelizable: true

- id: W6-T4
  title: "Realty / short-term-rent domain"
  files: [avitoapi/models/realty.py, avitoapi/methods/realty.py,
          avitoapi/client.py, tests/unit/test_realty.py,
          tests/fixtures/realty/**]
  depends_on: []
  parallelizable: true

- id: W6-T5
  title: "Autoteka domain"
  files: [avitoapi/models/autoteka.py, avitoapi/methods/autoteka.py,
          avitoapi/client.py, tests/unit/test_autoteka.py,
          tests/fixtures/autoteka/**]
  depends_on: []
  parallelizable: true

- id: W6-T6
  title: "Bump v0.3.0; update CHANGELOG; full surface audit"
  files: [pyproject.toml, CHANGELOG.md, docs/api-surface.md]
  depends_on: [W6-T1, W6-T2, W6-T3, W6-T4, W6-T5]
  parallelizable: false
```

## Risks
- `calltracking` returns `audio/mpeg` binary on the recording endpoint —
  `RestProtocol` needs a `__returning__ = bytes` path that bypasses JSON
  decoding. Handled via `BaseMethod.__binary_response__ = True` ClassVar
  + `RestProtocol.decode_response` early-return on raw bytes.
- `autoteka` full report is a paid endpoint — tests use a fixture only;
  live test is gated separately.
- `job` surface includes PII (resume contacts) — `logging.py` redaction
  must mask `email`/`phone` fields on `models.job.ResumeContact` in any
  structlog binding.

## Hardcodes introduced
None new.

## Hardcodes replaced
None.

## Acceptance checklist
- [ ] All 6 tasks land
- [ ] Full coverage of documented surface; cross-checked against
      `_research/raw/avito-api-surface.md`
- [ ] `docs/api-surface.md` lists every method-class + endpoint
- [ ] CHANGELOG `v0.3.0`

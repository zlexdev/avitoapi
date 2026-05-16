# Changelog

## v0.3.0 — Wave 6

- closed documented Avito Partner API surface (autoload, calltracking, job,
  realty, autoteka).
- added `AutoloadItemStatus`, `ListAutoloadReports`, `GetLastAutoloadReport`,
  `GetAutoloadReport`, `GetAutoloadCategoryFields`, `GetAutoloadProfile`,
  `UpdateAutoloadProfile`, `UploadAutoloadFile`, `ConvertAutoloadId`.
- added `GetCall`, `ListCalls`, `GetCallRecording` (binary `audio/mpeg`
  response via `__binary_response__ = True`).
- added `SearchResumes`, `GetResume`, `GetResumeContacts` (PII surface; flagged
  for logging redaction).
- added `ListBookings`, `GetCalendar`, `GetPeriodPrices`,
  `UpdatePeriodPrices`, `ItemBookings`.
- added `AutotekaPreviewByVin`, `AutotekaPreviewByRegnum`,
  `AutotekaFullReport` with client-side XOR-validator on identifiers.
- shipped `_Wave6Mixin` in `avitoapi/_client_mixins/wave6.py` for orchestrator
  composition into `Client`.
- `docs/api-surface.md` now lists every method-class across Waves 1–6.

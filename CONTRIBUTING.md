# Contributing

## Local setup

```bash
uv pip install -e ".[dev]"
cp .env.example .env   # fill AVITO_CLIENT_ID / AVITO_CLIENT_SECRET for live calls
```

## Checks (run before every PR)

```bash
ruff check avitoapi tests      # lint
ruff format avitoapi tests     # format
mypy avitoapi                  # types (strict)
pytest -q                      # tests
```

## Regenerating the SDK surface

`methods/`, `models/`, `enums/` and `facade/` are generated — never hand-edit a file carrying the
`AUTO-GENERATED` header. Change the generator under `avitoapi/codegen/` instead, then:

```bash
python -m avitoapi.codegen --all
```

Hand-written machinery (dispatcher, routers, events, transport, storage, `client.py`,
`polling.py`, base classes) is edited directly and never touched by codegen.

## Pull requests

- One logical change per PR; keep the diff focused.
- Add or update tests for behaviour changes; keep `pytest` green.
- Sync the relevant `_MODULE.md` / `_MODULE_AUTO.md` when you change a package's surface.
- Open [issues](../../issues/new/choose) for bugs and feature requests before large changes.

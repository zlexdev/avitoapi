# avitoapi

Aiogram-style async Python SDK over the Avito Partner API.

Wave 1 — skeleton + OAuth + first endpoint (`client.get_self()`).

Specs and design decisions live in `.plans/avito-sdk-framework/`:

- `00-overview.md` — scope, success criteria, mode + tier.
- `00-decisions.md` — every answered design question.
- `wave-01-skeleton.md` — current wave spec.
- `wave-02-…` through `wave-06-…` — subsequent waves.

## Quickstart (work-in-progress)

```bash
uv pip install -e .[dev]
cp .env.example .env
# fill in AVITO_CLIENT_ID, AVITO_CLIENT_SECRET, GH_TOKEN
```

```python
import asyncio
from avitoapi import Client, ClientConfig

async def main() -> None:
    async with Client(config=ClientConfig.from_env()) as client:
        me = await client.get_self()
        print(me.id, me.name)

asyncio.run(main())
```

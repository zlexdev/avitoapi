# Echo Bot — reference multi-account Avito bot

A minimal-but-production-shaped bot built on top of the `avitoapi` SDK.
Demonstrates:

- Multi-account dispatch (N `Client` instances → one `Dispatcher` → one
  webhook server).
- HMAC-SHA256 webhook signature verification.
- Idempotent webhook handling (replays are skipped).
- Fast-return: the HTTP reply lands inside Avito's 2s SLA and the actual
  handler runs in the background.
- `/healthz` endpoint for orchestrators (k8s, systemd, Uptime Kuma).

## Layout

```
echo_bot/
  main.py              entrypoint + multi-account wiring + --register CLI
  dispatcher_factory.py  composes HMAC + idempotency + fast-return middlewares
  healthz.py           aiohttp /healthz handler
scripts/
  run.sh               start the bot
  healthcheck.sh       curl /healthz, exit non-zero on failure
.env.example           every env var the bot reads
```

## Install

The example depends on the parent `avitoapi` package (editable) and on
`evented` (private dep). With `uv`:

```bash
cd examples/echo_bot
uv venv
uv pip install -e ../..          # editable avitoapi
GH_TOKEN=ghp_... uv pip install 'git+https://${GH_TOKEN}@github.com/zlexdev/evented.git@master'
uv pip install -e .
```

Plain `pip`:

```bash
pip install -e ../..
GH_TOKEN=ghp_... pip install 'git+https://${GH_TOKEN}@github.com/zlexdev/evented.git@master'
pip install -e .
```

## Configure

Copy `.env.example` to `.env` and fill in your Avito client credentials:

```bash
cp .env.example .env
# edit .env
```

You can declare multiple accounts by listing IDs in `AVITO_ACCOUNT_IDS`
and supplying `AVITO_CLIENT_ID_<id>`, `AVITO_CLIENT_SECRET_<id>`,
`AVITO_USER_ID_<id>` per account.

## Run

```bash
./scripts/run.sh
# or directly:
python -m echo_bot
```

The bot listens on `0.0.0.0:$PORT` (default `8080`) for webhook deliveries
on `$WEBHOOK_PATH` (default `/messenger`). A `GET /healthz` endpoint is
always available.

## Register webhook URL with Avito (one-shot)

After deploying to a public HTTPS URL, register it once:

```bash
python -m echo_bot --register https://bot.example.com/messenger
```

> Avito requires HTTPS for webhook URLs. Use nginx + certbot, Caddy, or a
> tunnel like Cloudflare Tunnel for local development.

## Notes

- Heavy work inside the handler is fine — the fast-return middleware
  spawns the handler as a background task so the HTTP reply ships
  immediately. Do **not** `await` long operations before returning from
  the webhook handler in your own code.
- Webhook secret is read from `AVITO_WEBHOOK_SECRET` and rotated by
  calling `--register` again.

"""``GET /healthz`` aiohttp handler."""
from __future__ import annotations

from aiohttp import web


async def healthz(_request: web.Request) -> web.Response:
    """Return ``{"status": "ok"}`` with HTTP 200."""
    return web.json_response({"status": "ok"})


def attach(app: web.Application, path: str = "/healthz") -> None:
    """Mount the healthcheck on the given aiohttp app."""
    app.router.add_get(path, healthz)

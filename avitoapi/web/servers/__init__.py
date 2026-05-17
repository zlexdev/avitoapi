"""Per-framework webhook server backends.

Each backend is lazy-loaded so the HTTP framework is only imported when
its class is touched. Pick one explicitly:

* ``AiohttpWebApp`` / ``AiohttpWebhookRunner`` — default, no extra dep.
* ``FastAPIWebApp`` / ``FastAPIWebhookRunner`` — ``pip install
  avitoapi[fastapi]`` (plus ``uvicorn``).
* ``LitestarWebApp`` / ``LitestarWebhookRunner`` — ``pip install
  avitoapi[litestar]`` (plus ``uvicorn``).
* ``SanicWebApp`` / ``SanicWebhookRunner`` — ``pip install
  avitoapi[sanic]``.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ._base import BaseWebApp, BaseWebhookRunner

if TYPE_CHECKING:
    from .aiohttp_server import AiohttpWebApp as AiohttpWebApp
    from .aiohttp_server import AiohttpWebhookRunner as AiohttpWebhookRunner
    from .fastapi_server import FastAPIWebApp as FastAPIWebApp
    from .fastapi_server import FastAPIWebhookRunner as FastAPIWebhookRunner
    from .litestar_server import LitestarWebApp as LitestarWebApp
    from .litestar_server import LitestarWebhookRunner as LitestarWebhookRunner
    from .sanic_server import SanicWebApp as SanicWebApp
    from .sanic_server import SanicWebhookRunner as SanicWebhookRunner

_LAZY: dict[str, tuple[str, str]] = {
    "AiohttpWebApp": (".aiohttp_server", "AiohttpWebApp"),
    "AiohttpWebhookRunner": (".aiohttp_server", "AiohttpWebhookRunner"),
    "FastAPIWebApp": (".fastapi_server", "FastAPIWebApp"),
    "FastAPIWebhookRunner": (".fastapi_server", "FastAPIWebhookRunner"),
    "LitestarWebApp": (".litestar_server", "LitestarWebApp"),
    "LitestarWebhookRunner": (".litestar_server", "LitestarWebhookRunner"),
    "SanicWebApp": (".sanic_server", "SanicWebApp"),
    "SanicWebhookRunner": (".sanic_server", "SanicWebhookRunner"),
}


def __getattr__(name: str) -> Any:
    if name in _LAZY:
        module_name, attr = _LAZY[name]
        from importlib import import_module  # noqa: PLC0415 — lazy by design

        module = import_module(module_name, __name__)
        return getattr(module, attr)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "AiohttpWebApp",
    "AiohttpWebhookRunner",
    "BaseWebApp",
    "BaseWebhookRunner",
    "FastAPIWebApp",
    "FastAPIWebhookRunner",
    "LitestarWebApp",
    "LitestarWebhookRunner",
    "SanicWebApp",
    "SanicWebhookRunner",
]

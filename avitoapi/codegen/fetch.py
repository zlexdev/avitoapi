"""Spec fetching — pull the Avito OpenAPI catalogue and per-domain specs.

The portal serves a stringified OpenAPI 3.0 document per slug under
``/web/1/openapi/info/{slug}``. Responses are cached on disk so a full regen doesn't
re-hit the network for every domain.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import INFO_ENDPOINT, LIST_ENDPOINT

_CACHE_DIR = Path(__file__).parent / "_spec_cache"
_USER_AGENT = "avitoapi-codegen/1.0"
_TIMEOUT = 40


class SpecFetchError(RuntimeError):
    """Raised when a spec cannot be fetched or parsed."""


@dataclass(frozen=True, slots=True)
class DomainInfo:
    """One entry from ``/openapi/list``."""

    slug: str
    title: str
    description: str


def _get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})  # noqa: S310 — fixed https host
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:  # noqa: S310
            return resp.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError) as exc:
        raise SpecFetchError(f"failed to fetch {url}: {exc}") from exc


def list_domains() -> list[DomainInfo]:
    """Return every API domain published in the catalogue."""

    raw = json.loads(_get(LIST_ENDPOINT))
    return [DomainInfo(slug=e["slug"], title=e["title"], description=e.get("description", "")) for e in raw]


def fetch_spec(slug: str, *, use_cache: bool = True) -> dict[str, Any]:
    """Return the parsed OpenAPI 3.0 document for ``slug`` (disk-cached)."""

    cache = _CACHE_DIR / f"{slug}.json"
    if use_cache and cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))

    envelope = json.loads(_get(INFO_ENDPOINT.format(slug=slug)))
    swagger = envelope.get("swagger")
    if not isinstance(swagger, str):
        raise SpecFetchError(f"{slug}: response has no stringified 'swagger' spec")
    spec: dict[str, Any] = json.loads(swagger)

    _CACHE_DIR.mkdir(exist_ok=True)
    cache.write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
    return spec

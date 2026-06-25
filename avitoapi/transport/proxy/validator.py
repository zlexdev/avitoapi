"""Proxy checker — runs a tiny live request through each proxy and reports the outcome."""

from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass, field
from typing import Any

from ...logging import get_logger
from ._base import Proxy
from .parser import ProxyLike, parse_proxy

RequestFn = Callable[[Proxy, str, str, float], Awaitable[tuple[int, float]]]

log = get_logger(__name__)

_DEFAULT_CHECK_URL = "https://api.avito.ru/"


@dataclass(slots=True, frozen=True)
class ProxyCheckResult:
    """Outcome of one proxy probe."""

    proxy: Proxy
    ok: bool
    status_code: int | None = None
    elapsed_s: float = 0.0
    error: str | None = None


@dataclass(slots=True)
class ProxyValidator:
    """Run a small probe request through each proxy in parallel.

    The default probe is a ``GET`` against ``api.avito.ru`` — any 2xx/3xx
    response counts as healthy (the proxy doesn't need to be authenticated
    against Avito to forward the request). Override ``check_url`` /
    ``http_method`` / ``accept_statuses`` for custom protocols.

    Customise the wire backend by supplying ``request_fn`` — it receives
    ``(proxy: Proxy, url: str, method: str, timeout_s: float)`` and returns
    ``(status_code, elapsed_s)``. Default tries ``curl_cffi`` and falls
    back to ``httpx``.
    """

    check_url: str = _DEFAULT_CHECK_URL
    http_method: str = "GET"
    timeout_s: float = 10.0
    accept_statuses: frozenset[int] = field(
        default_factory=lambda: frozenset(range(200, 400)),
    )
    concurrency: int = 16
    request_fn: RequestFn | None = None

    async def validate(self, proxy: ProxyLike) -> ProxyCheckResult:
        """Probe a single proxy. Never raises — wraps every failure into a result."""

        parsed = parse_proxy(proxy)
        fn = self.request_fn or _default_request_fn()
        start = time.monotonic()
        try:
            status, elapsed = await fn(parsed, self.check_url, self.http_method, self.timeout_s)
        except TimeoutError as exc:
            return ProxyCheckResult(
                proxy=parsed,
                ok=False,
                elapsed_s=time.monotonic() - start,
                error=f"timeout: {exc}",
            )
        except Exception as exc:  # noqa: BLE001 — external probe, surface every failure mode
            return ProxyCheckResult(
                proxy=parsed,
                ok=False,
                elapsed_s=time.monotonic() - start,
                error=f"{type(exc).__name__}: {exc}",
            )
        return ProxyCheckResult(
            proxy=parsed,
            ok=status in self.accept_statuses,
            status_code=status,
            elapsed_s=elapsed,
        )

    async def validate_many(self, proxies: Iterable[ProxyLike]) -> list[ProxyCheckResult]:
        """Probe many proxies in parallel under :attr:`concurrency` limit."""

        sem = asyncio.Semaphore(max(1, self.concurrency))

        async def _run(p: ProxyLike) -> ProxyCheckResult:
            async with sem:
                return await self.validate(p)

        return await asyncio.gather(*[_run(p) for p in proxies])


def _default_request_fn() -> RequestFn:
    try:
        import curl_cffi  # noqa: F401 — capability probe
    except ImportError:
        return _httpx_request
    return _curl_request


async def _curl_request(
    proxy: Proxy,
    url: str,
    method: str,
    timeout_s: float,
) -> tuple[int, float]:
    from curl_cffi.requests import AsyncSession

    proxy_url = str(proxy.url)
    start = time.monotonic()
    async with AsyncSession(impersonate="chrome120") as session:
        response: Any = await session.request(
            method,
            url,
            proxies={"http": proxy_url, "https": proxy_url},
            timeout=timeout_s,
        )
    elapsed = time.monotonic() - start
    return int(response.status_code), elapsed


async def _httpx_request(
    proxy: Proxy,
    url: str,
    method: str,
    timeout_s: float,
) -> tuple[int, float]:
    import httpx

    proxy_url = str(proxy.url)
    start = time.monotonic()
    async with httpx.AsyncClient(proxy=proxy_url, timeout=timeout_s) as client:
        response = await client.request(method, url)
    elapsed = time.monotonic() - start
    return int(response.status_code), elapsed


__all__ = ["ProxyCheckResult", "ProxyValidator"]

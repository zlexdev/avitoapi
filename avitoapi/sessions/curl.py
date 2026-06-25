"""``CurlSession`` — default backend using ``curl_cffi`` for browser-grade TLS fingerprinting."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from ..exceptions import AvitoConnectionError, AvitoTimeoutError, TLSError, TransportError
from ._models import PreparedRequest, RawResponse
from .base import BaseSession

if TYPE_CHECKING:
    from ..config import ClientConfig
    from ..transport.proxy._base import BaseProxyTransport


class CurlSession(BaseSession):
    """Async HTTP backend backed by ``curl_cffi.requests.AsyncSession``.

    Lazy-imports ``curl_cffi`` on first use so callers can pip-install
    ``avitoapi[httpx]`` without dragging libcurl-impersonate onto unsupported
    platforms. Default impersonation profile = ``chrome120``.
    """

    def __init__(
        self,
        *,
        config: ClientConfig,
        proxy_transport: BaseProxyTransport | None = None,
        impersonate: str = "chrome120",
    ) -> None:
        super().__init__(config=config, proxy_transport=proxy_transport)
        self.impersonate = impersonate
        self._inner: object = None

    async def open(self) -> None:
        if self._inner is not None:
            return
        from curl_cffi.requests import AsyncSession  # lazy-import

        self._inner = AsyncSession(impersonate=self.impersonate)  # type: ignore[arg-type]  # curl_cffi expects Literal; str is fine at runtime
        await super().open()

    async def close(self) -> None:
        if self._inner is not None:
            import contextlib

            with contextlib.suppress(Exception):
                await self._inner.close()  # type: ignore[attr-defined]
            self._inner = None
        await super().close()

    async def _send(self, prepared: PreparedRequest) -> RawResponse:
        if self._inner is None:
            await self.open()
        assert self._inner is not None

        kwargs: dict[str, object] = {
            "headers": prepared.headers,
            "params": prepared.query or None,
            "timeout": prepared.timeout_s,
        }
        if prepared.body is not None:
            if isinstance(prepared.body, dict | list):
                kwargs["data"] = json.dumps(prepared.body)
                prepared.headers.setdefault("Content-Type", "application/json")
            elif isinstance(prepared.body, str):
                kwargs["data"] = prepared.body
            elif isinstance(prepared.body, bytes | bytearray):
                kwargs["data"] = bytes(prepared.body)
            else:
                kwargs["data"] = json.dumps(prepared.body)
                prepared.headers.setdefault("Content-Type", "application/json")

        if prepared.proxy:
            kwargs["proxies"] = {"http": prepared.proxy, "https": prepared.proxy}

        try:
            response = await self._inner.request(  # type: ignore[attr-defined]
                prepared.http_method,
                prepared.url,
                **kwargs,
            )
        except TimeoutError as exc:
            raise AvitoTimeoutError(str(exc)) from exc
        except Exception as exc:  # noqa: BLE001 — transport boundary: normalise backend error, re-raised
            name = type(exc).__name__.lower()
            if "timeout" in name:
                raise AvitoTimeoutError(str(exc)) from exc
            if "ssl" in name or "tls" in name or "certificate" in name:
                raise TLSError(str(exc)) from exc
            if "connect" in name or "resolve" in name:
                raise AvitoConnectionError(str(exc)) from exc
            raise TransportError(f"{type(exc).__name__}: {exc}") from exc

        body: bytes = (
            response.content
            if isinstance(response.content, bytes)
            else bytes(
                response.content or b"",
            )
        )
        headers = {k.lower(): v for k, v in (response.headers or {}).items()}
        return RawResponse(status=response.status_code, headers=headers, body=body)

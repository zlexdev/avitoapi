"""``HttpxSession`` — fallback backend when ``curl_cffi`` is not installable."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from ..exceptions import ConnectionError as SDKConnectionError
from ..exceptions import TimeoutError as SDKTimeoutError
from ..exceptions import TransportError
from ._models import PreparedRequest, RawResponse
from .base import BaseSession

if TYPE_CHECKING:
    from ..config import ClientConfig
    from ..utils.proxy._base import BaseProxyTransport


class HttpxSession(BaseSession):
    """Pure-Python fallback. No TLS impersonation — Cloudflare-protected hosts may challenge."""

    def __init__(
        self,
        *,
        config: ClientConfig,
        proxy_transport: BaseProxyTransport | None = None,
    ) -> None:
        super().__init__(config=config, proxy_transport=proxy_transport)
        self._inner: Any = None

    async def open(self) -> None:
        if self._inner is not None:
            return
        import httpx  # lazy-import

        # No fixed proxy at construction — per-request proxies require a fresh
        # AsyncClient (httpx binds proxy at client level). We build one on demand.
        self._inner = httpx.AsyncClient(timeout=self.config.request_timeout_s)
        await super().open()

    async def close(self) -> None:
        if self._inner is not None:
            await self._inner.aclose()
            self._inner = None
        await super().close()

    async def _send(self, prepared: PreparedRequest) -> RawResponse:
        if self._inner is None:
            await self.open()
        assert self._inner is not None
        import httpx  # lazy-import for exception classes

        kwargs: dict[str, Any] = {
            "headers": prepared.headers,
            "params": prepared.query or None,
            "timeout": prepared.timeout_s,
        }
        if prepared.body is not None:
            if isinstance(prepared.body, (dict, list)):
                kwargs["content"] = json.dumps(prepared.body)
                prepared.headers.setdefault("Content-Type", "application/json")
            elif isinstance(prepared.body, (bytes, bytearray)):
                kwargs["content"] = bytes(prepared.body)
            else:
                kwargs["content"] = str(prepared.body)

        try:
            response = await self._inner.request(
                prepared.http_method,
                prepared.url,
                **kwargs,
            )
        except httpx.TimeoutException as exc:
            raise SDKTimeoutError(str(exc)) from exc
        except httpx.ConnectError as exc:
            raise SDKConnectionError(str(exc)) from exc
        except httpx.HTTPError as exc:
            raise TransportError(f"{type(exc).__name__}: {exc}") from exc

        headers = {k.lower(): v for k, v in response.headers.items()}
        return RawResponse(status=response.status_code, headers=headers, body=response.content)

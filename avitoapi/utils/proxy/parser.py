"""Flexible proxy parser. Accepts URL strings, ``host:port[:user:pass]`` shorthand, dicts."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any
from urllib.parse import quote, urlsplit

from pydantic import AnyUrl, ValidationError

from ...exceptions import ProxyParseError
from ._base import Proxy

_DEFAULT_SCHEME = "http"
_KNOWN_SCHEMES: frozenset[str] = frozenset({"http", "https", "socks4", "socks5", "socks5h"})

ProxyLike = str | Proxy | dict[str, Any]


def parse_proxy(value: ProxyLike, *, label: str | None = None) -> Proxy:
    """Coerce ``value`` into a :class:`Proxy`.

    Accepted shapes::

        Proxy(...)                                      # returned as-is (label override only)
        "http://user:pass@host:port"                    # full URL
        "socks5://host:port"                            # full URL no auth
        "host:port"                                     # scheme defaults to http
        "host:port:user:pass"                           # legacy 4-tuple format
        "user:pass@host:port"                           # scheme defaults to http
        {"host": ..., "port": ..., "user": ..., "password": ..., "scheme": ...}

    Raises :class:`ProxyParseError` on any input the parser cannot interpret.
    """

    raw: Any = value
    if isinstance(raw, Proxy):
        return raw if label is None else raw.model_copy(update={"label": label})
    if isinstance(raw, dict):
        return _from_dict(raw, label_override=label)
    if isinstance(raw, str):
        return _from_string(raw, label_override=label)
    raise ProxyParseError(f"Unsupported proxy type: {type(raw).__name__}")


def parse_proxy_list(
    values: Iterable[ProxyLike] | str,
    *,
    skip_invalid: bool = False,
) -> list[Proxy]:
    """Parse many proxies.

    ``values`` can be an iterable, or a single multi-line string (one proxy per
    line; blank lines and ``#``-comments skipped). When ``skip_invalid`` is
    ``True``, malformed entries are silently dropped — otherwise the first
    :class:`ProxyParseError` propagates.
    """

    items: Iterable[ProxyLike]
    items = _split_lines(values) if isinstance(values, str) else values

    parsed: list[Proxy] = []
    for raw in items:
        try:
            parsed.append(parse_proxy(raw))
        except ProxyParseError:
            if not skip_invalid:
                raise
    return parsed


def _split_lines(text: str) -> list[str]:
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def _from_dict(data: dict[str, Any], *, label_override: str | None) -> Proxy:
    host = data.get("host") or data.get("hostname")
    port = data.get("port")
    if not host or port is None:
        raise ProxyParseError(f"dict proxy missing host/port: {data!r}")

    scheme = str(data.get("scheme") or _DEFAULT_SCHEME).lower()
    user = data.get("user") or data.get("username")
    password = data.get("password") or data.get("pass")
    label = label_override if label_override is not None else data.get("label")

    return _build(
        scheme=scheme,
        host=str(host),
        port=_coerce_port(port),
        user=user,
        password=password,
        label=label,
    )


def _from_string(value: str, *, label_override: str | None) -> Proxy:
    text = value.strip()
    if not text:
        raise ProxyParseError("Empty proxy string")

    if "://" in text:
        return _from_url(text, label_override=label_override)

    if "@" in text:
        creds, hostport = text.rsplit("@", 1)
        user, password = _split_creds(creds)
        host, port = _split_host_port(hostport)
        return _build(
            scheme=_DEFAULT_SCHEME,
            host=host,
            port=port,
            user=user,
            password=password,
            label=label_override,
        )

    parts = text.split(":")
    if len(parts) == 2:
        host, port_s = parts
        return _build(
            scheme=_DEFAULT_SCHEME,
            host=host,
            port=_coerce_port(port_s),
            user=None,
            password=None,
            label=label_override,
        )
    if len(parts) == 4:
        host, port_s, user, password = parts
        return _build(
            scheme=_DEFAULT_SCHEME,
            host=host,
            port=_coerce_port(port_s),
            user=user,
            password=password,
            label=label_override,
        )
    raise ProxyParseError(f"Unrecognised proxy string: {value!r}")


def _from_url(text: str, *, label_override: str | None) -> Proxy:
    parts = urlsplit(text)
    if parts.scheme.lower() not in _KNOWN_SCHEMES:
        raise ProxyParseError(f"Unknown proxy scheme {parts.scheme!r} in {text!r}")
    if not parts.hostname or parts.port is None:
        raise ProxyParseError(f"Proxy URL missing host/port: {text!r}")
    return _build(
        scheme=parts.scheme.lower(),
        host=parts.hostname,
        port=int(parts.port),
        user=parts.username,
        password=parts.password,
        label=label_override,
    )


def _build(
    *,
    scheme: str,
    host: str,
    port: int,
    user: str | None,
    password: str | None,
    label: str | None,
) -> Proxy:
    if scheme not in _KNOWN_SCHEMES:
        raise ProxyParseError(f"Unknown proxy scheme {scheme!r}")
    if not (0 < port < 65536):
        raise ProxyParseError(f"Proxy port out of range: {port}")

    auth = ""
    if user is not None:
        auth = quote(user, safe="")
        if password is not None:
            auth = f"{auth}:{quote(password, safe='')}"
        auth = f"{auth}@"

    url_text = f"{scheme}://{auth}{host}:{port}"
    try:
        url = AnyUrl(url_text)
    except ValidationError as exc:
        raise ProxyParseError(f"Built invalid proxy URL {url_text!r}: {exc}") from exc
    return Proxy(url=url, label=label)


def _split_creds(creds: str) -> tuple[str, str | None]:
    if ":" not in creds:
        return creds, None
    user, password = creds.split(":", 1)
    return user, password


def _split_host_port(hostport: str) -> tuple[str, int]:
    if ":" not in hostport:
        raise ProxyParseError(f"Missing port in {hostport!r}")
    host, port_s = hostport.rsplit(":", 1)
    return host, _coerce_port(port_s)


def _coerce_port(value: Any) -> int:
    try:
        port = int(value)
    except (TypeError, ValueError) as exc:
        raise ProxyParseError(f"Proxy port must be int, got {value!r}") from exc
    if not (0 < port < 65536):
        raise ProxyParseError(f"Proxy port out of range: {port}")
    return port


__all__ = ["ProxyLike", "parse_proxy", "parse_proxy_list"]

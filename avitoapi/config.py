"""Per-client configuration. Strict Pydantic model with ``.from_env()`` loader."""
from __future__ import annotations

import os
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, SecretStr

from .types import HostKey

__version__ = "0.1.0"

DEFAULT_USER_AGENT = (
    f"avitoapi/{__version__} (+https://github.com/zlexdev/avitoapi)"
)


def _default_hosts() -> dict[HostKey, HttpUrl]:
    return {HostKey("www"): HttpUrl("https://api.avito.ru")}


class ClientConfig(BaseModel):
    """Settings for one :class:`avitoapi.Client` instance.

    Constructed directly or via :meth:`ClientConfig.from_env` which reads
    ``AVITO_*`` env vars. See ``.env.example`` for the canonical key list.
    """

    model_config = ConfigDict(strict=True, frozen=False, extra="forbid")

    client_id: str = Field(..., description="OAuth2 client_id.")
    client_secret: SecretStr = Field(..., description="OAuth2 client_secret.")
    user_id: int | None = Field(
        default=None,
        description="Required for the authorization_code grant.",
    )
    redirect_uri: HttpUrl | None = Field(
        default=None,
        description="Redirect URI registered with Avito (authorization_code grant only).",
    )
    oauth_grant_endpoint: Literal["post_form", "get_query"] = Field(
        default="post_form",
        description="OAuth token endpoint flavor. Avito ships two; default matches recent clients.",
    )

    hosts: dict[HostKey, HttpUrl] = Field(default_factory=_default_hosts)

    user_agent: str = Field(default=DEFAULT_USER_AGENT)
    request_timeout_s: float = Field(default=30.0, gt=0)
    max_retries: int = Field(default=5, ge=0)
    backoff_initial_s: float = Field(default=0.5, gt=0)
    backoff_max_s: float = Field(default=30.0, gt=0)

    rate_limit_global_rps: float = Field(default=5.0, gt=0)
    rate_limit_per_chat_rps: float = Field(default=1.0, gt=0)

    breaker_fail_threshold: int = Field(default=5, ge=1)
    breaker_open_seconds: float = Field(default=30.0, gt=0)
    breaker_per_account: bool = Field(default=False)

    pagination_max_pages: int = Field(
        default=1000,
        ge=1,
        description="Runaway guard for paginators; raises after N pages fetched.",
    )

    webhook_signature_header: str = Field(default="x-avito-messenger-signature")

    category_overrides: dict[str, int] = Field(default_factory=dict)

    cookie_persistence: Literal["manual", "on_close", "after_each"] = Field(default="on_close")

    strict_state_machine: bool = Field(default=True)

    @classmethod
    def from_env(cls, prefix: str = "AVITO_") -> Self:
        """Build a config from ``{prefix}*`` env vars (default prefix ``AVITO_``)."""

        client_id = os.environ.get(f"{prefix}CLIENT_ID")
        client_secret = os.environ.get(f"{prefix}CLIENT_SECRET")
        if not client_id or not client_secret:
            raise ValueError(
                f"Missing required env vars: {prefix}CLIENT_ID and {prefix}CLIENT_SECRET",
            )

        kwargs: dict[str, object] = {
            "client_id": client_id,
            "client_secret": SecretStr(client_secret),
        }
        if uid := os.environ.get(f"{prefix}USER_ID"):
            kwargs["user_id"] = int(uid)
        if redirect := os.environ.get(f"{prefix}REDIRECT_URI"):
            kwargs["redirect_uri"] = HttpUrl(redirect)
        if grant := os.environ.get(f"{prefix}OAUTH_GRANT_ENDPOINT"):
            kwargs["oauth_grant_endpoint"] = grant
        if timeout := os.environ.get(f"{prefix}REQUEST_TIMEOUT_S"):
            kwargs["request_timeout_s"] = float(timeout)
        if retries := os.environ.get(f"{prefix}MAX_RETRIES"):
            kwargs["max_retries"] = int(retries)
        if ua := os.environ.get(f"{prefix}USER_AGENT"):
            kwargs["user_agent"] = ua
        return cls(**kwargs)  # type: ignore[arg-type]

    def base_url(self, host: HostKey) -> str:
        """Resolve a logical host key to its base URL string (no trailing slash)."""

        if host not in self.hosts:
            raise KeyError(f"Unknown host key: {host!r}. Registered: {sorted(self.hosts)}")
        return str(self.hosts[host]).rstrip("/")

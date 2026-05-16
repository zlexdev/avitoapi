"""HMAC-SHA256 signature verification for inbound Avito webhooks.

Avito signs each delivery with the per-webhook secret stored under
``webhook:{webhook_id}:secret``. The middleware looks the secret up via a
caller-supplied async `SecretProvider` and uses :func:`hmac.compare_digest`
for constant-time comparison.
"""
from __future__ import annotations

import hashlib
import hmac
from collections.abc import Awaitable, Callable

SecretProvider = Callable[[str], Awaitable["str | None"]]


class HMACSignatureMissingError(ValueError):
    """Raised when ``require_signature=True`` and no header was supplied."""


class HMACSignatureMiddleware:
    """Verify ``x-avito-messenger-signature`` against the per-webhook secret.

    ``secret_provider(webhook_id)`` returns the secret (or ``None`` if the
    webhook id is unknown — treated as a verification failure).
    """

    def __init__(
        self,
        secret_provider: SecretProvider,
        *,
        header_name: str = "x-avito-messenger-signature",
        require_signature: bool = True,
    ) -> None:
        self._secret_provider = secret_provider
        self.header_name = header_name
        self.require_signature = require_signature

    async def verify(
        self,
        raw_body: bytes,
        signature: str | None,
        webhook_id: str,
    ) -> bool:
        """Return ``True`` iff the body's HMAC matches the given signature.

        * ``signature`` missing + ``require_signature=True`` → raises
          :class:`HMACSignatureMissingError`.
        * ``signature`` missing + ``require_signature=False`` → returns ``False``
          (silent reject, caller decides what to do).
        * Unknown ``webhook_id`` → returns ``False``.
        """
        if signature is None or signature == "":
            if self.require_signature:
                raise HMACSignatureMissingError(
                    f"missing required header: {self.header_name}",
                )
            return False
        secret = await self._secret_provider(webhook_id)
        if secret is None:
            return False
        expected = hmac.new(
            secret.encode("utf-8"),
            raw_body,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

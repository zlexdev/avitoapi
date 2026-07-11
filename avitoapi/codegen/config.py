"""Codegen configuration — the small curated tables the auto-builder needs.

Everything here is the *reliability net* over Avito's inconsistent OpenAPI: slug→module
aliases (the hand-tuned tree renamed a few domains), entity-binding overrides for
bound-method generation, and the header params the transport owns (never emitted as
method fields).
"""

from __future__ import annotations

from typing import Final

BASE_URL: Final = "https://developers.avito.ru"
LIST_ENDPOINT: Final = f"{BASE_URL}/web/1/openapi/list"
INFO_ENDPOINT: Final = f"{BASE_URL}/web/1/openapi/info/{{slug}}"
DOCS_URL_TEMPLATE: Final = f"{BASE_URL}/api-catalog/{{slug}}/documentation"

#: Logical host key every generated method targets (matches ``BaseMethod.__host__`` default).
DEFAULT_HOST: Final = "www"

#: Header params handled by the transport/auth layer — dropped from generated method fields.
SKIP_HEADER_PARAMS: Final[frozenset[str]] = frozenset(
    {"authorization", "content-type", "x-ratelimit-limit", "x-ratelimit-remaining"},
)

#: slug (from ``/openapi/list``) → target module basename under ``methods/`` and ``models/``.
#: Slugs absent here map to ``slug.replace("-", "_")``.
SLUG_TO_MODULE: Final[dict[str, str]] = {
    "item": "items",
    "delivery-sandbox": "delivery",
    "ratings": "reviews",
    "sbc-gateway": "special_offers",
    "user": "user",
    "str": "short_term_rental",
    "avito-promo": "avito_promo",
}

#: Write verbs whose retries must carry an ``Idempotency-Key``.
IDEMPOTENT_VERBS: Final[frozenset[str]] = frozenset({"PUT", "PATCH", "DELETE"})

#: Path-parameter token (``{<token>}`` → snake_cased) → (entity model class, self attr).
#: Drives bound-method generation. ``user_id`` is the account context (resolved from the
#: client), never a model field, so it is deliberately absent.
ENTITY_BINDINGS: Final[dict[str, tuple[str, str]]] = {
    "item_id": ("Item", "id"),
    "chat_id": ("Chat", "id"),
    "order_id": ("Order", "id"),
    "review_id": ("Review", "id"),
    "message_id": ("Message", "id"),
    "vacancy_id": ("Vacancy", "id"),
}

#: Path tokens that are account-context, filled from the client, not from a model field.
ACCOUNT_CONTEXT_PARAMS: Final[frozenset[str]] = frozenset({"user_id"})


def module_for_slug(slug: str) -> str:
    """Return the ``methods/<name>.py`` basename for an OpenAPI ``slug``."""

    return SLUG_TO_MODULE.get(slug, slug.replace("-", "_"))

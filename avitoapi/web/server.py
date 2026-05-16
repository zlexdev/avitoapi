"""Re-exports of ``evented`` web primitives.

Requires ``evented`` (private dep at ``github.com/zlexdev/evented``); install
via ``pip install 'git+https://${GH_TOKEN}@github.com/zlexdev/evented.git'``.
"""
from __future__ import annotations

import evented

WebApp = evented.web.WebApp
WebhookRunner = evented.WebhookRunner
WebhookConfig = evented.WebhookConfig
Webhook = evented.Webhook

__all__ = ["WebApp", "Webhook", "WebhookConfig", "WebhookRunner"]

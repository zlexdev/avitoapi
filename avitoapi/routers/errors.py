"""Typed control-flow signals for event propagation.

These are *control* exceptions, not errors: handlers raise them to steer the
router, and :class:`~avitoapi.routers.Router.propagate` treats them as clean
outcomes rather than failures. Broadcast (every matching handler fires) stays
the default; stopping is opt-in via these signals or
:meth:`~avitoapi.routers.EventContext.stop_propagation`.
"""

from __future__ import annotations


class RoutingError(Exception):
    """Base for router control-flow signals."""


class SkipHandler(RoutingError):
    """Skip the current handler and continue with the remaining ones."""


class CancelPropagation(RoutingError):
    """Stop all further handlers and sub-routers for this event.

    Handlers already run before the raise keep their effects; only
    subsequent handlers and child routers are skipped.
    """


__all__ = ["CancelPropagation", "RoutingError", "SkipHandler"]

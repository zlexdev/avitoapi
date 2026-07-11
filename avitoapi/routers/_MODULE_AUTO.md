# routers/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

> Aiogram-style single ``Router`` — every event as a named observer attribute.

## __init__.py
```
# Aiogram-style single ``Router`` — every event as a named observer attribute.


```

## _routers.py
```
# Single aiogram-style ``Router`` — every domain's observers as attributes.


cls Router
  __init__(name: str = 'avito') -> None
  include_router(router: Router) -> Router
    # Attach a sub-router; events propagate to children after the parent's own handlers.
  include_routers(*routers: Router) -> None
  iter_routers() -> Iterable[Router]
    # Depth-first walk: self → every descendant.
  iter_handlers() -> Iterable[tuple[str, HandlerSpec]]
  manager(name: str) -> HandlerManager[Event]
    # Public alias — create / fetch a manager by route name.
  on(name: str, *filters: Filter) -> Callable[[Handler], Handler]
    # Imperative shortcut: ``@router.on("orders.created")``.
  async propagate(event: Event, ctx: EventContext) -> bool
    # Walk every manager (self → children); return ``True`` if any handler fired.

_isinst() -> Filter
  # Build an ``event_filter`` callable that matches ``isinstance(event, cls)``.

_msg_of(kind: object) -> Filter
  # ``NewMessage`` filter narrowing to one :class:`MessageType` variant.

install_observers(router_like: Router) -> None

```

## context.py
```
# ``EventContext`` — per-event mutable bag passed to every handler.


cls CtxQueue: message_id: str, attempts: int, queued_at: float, metadata: dict[str, Any], _ack: Callable[[str], Awaitable[bool]] | None, _update_metadata: Callable[[str, dict[str, Any]], Awaitable[bool]] | None, _acked: bool

cls EventContext: event: Event, dispatcher: Any, workflow_data: dict[str, Any], handled: bool, queue: CtxQueue, _stopped: bool

```

## errors.py
```
# Typed control-flow signals for event propagation.


cls RoutingError(Exception)
  # Base for router control-flow signals.

cls SkipHandler(RoutingError)
  # Skip the current handler and continue with the remaining ones.

cls CancelPropagation(RoutingError)

```

## middleware.py
```
# ``BaseMiddleware`` — outer/inner middleware ABC for event propagation.


cls BaseMiddleware(ABC, Generic[CtxT, ResultT])

cls MiddlewareChain(Generic[CtxT, ResultT])
  # Ordered list of :class:`BaseMiddleware`. Earlier registrations wrap later ones.
  __init__() -> None
  register(middleware: BaseMiddleware[CtxT, ResultT) -> BaseMiddleware[CtxT, ResultT]
    # Append a middleware. Returns it for fluent chaining.
  wrap(terminal: Callable[[Event, CtxT], Awaitable[ResultT) -> Callable[[Event, CtxT], Awaitable[ResultT]]
    # Fold the chain over ``terminal`` and return the composed handler.

_bind(mw: BaseMiddleware[CtxT, ResultT, nxt: Callable[[Event, CtxT], Awaitable[ResultT) -> Callable[[Event, CtxT], Awaitable[ResultT]]

```

## observer.py
```
# ``EventObserver`` / ``HandlerManager`` — the decorator surface routers expose.


cls HandlerSpec: handler: Handler, filters: tuple[Filter, ...]
  # One registered handler with its activation predicates.

cls HandlerManager(Generic[EventT_contra]): name: str, event_filter: Filter | None, handlers: list[HandlerSpec]

```

# fanout/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

> Fanout — merge many supervised event sources into one dispatcher.

## __init__.py
```
# Fanout — merge many supervised event sources into one dispatcher.


```

## hub.py
```
# ``SourceHub`` — merge N supervised event sources into one dispatcher.


cls _SourceState: alive: bool, restarts: int, last_error: str | None

cls SourceHealth: name: str, alive: bool, restarts: int, last_error: str | None
  # Point-in-time health of one supervised source.

cls HubHealth: sources: list[SourceHealth]
  # Aggregated health across every source in the hub.

cls SourceHub
  # Supervise many :class:`BaseEventSource` into one :class:`Dispatcher`.
  __init__() -> None
  add_source(source: BaseEventSource) -> None
  async start() -> None
    # Start the channel drain and one supervised pump per source. Idempotent.
  async stop() -> None
    # Stop the pumps, then the drain. ``drain=True`` flushes queued events first.
  health() -> HubHealth

```

## source.py
```
# ``BaseEventSource`` — a long-lived stream of events the hub supervises.


cls BaseEventSource(ABC)
  stream() -> AsyncIterator[Event]
    # Yield events until exhausted or raising (→ supervised restart).

```

## supervision.py
```
# ``SupervisionPolicy`` — exponential backoff for restarting a failed source.


cls SupervisionPolicy: base_delay: float, max_delay: float, factor: float, jitter: bool, max_restarts: int | None

```

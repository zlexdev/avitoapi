# channels/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

> Push channels — bounded producer→dispatcher pipes with an overflow policy.

## __init__.py
```
# Push channels — bounded producer→dispatcher pipes with an overflow policy.


```

## _base.py
```
# Push-channel contract — a bounded producer→dispatcher pipe with an overflow policy.


cls ChannelOverflow(StrEnum): BLOCK, DROP_OLDEST, DROP_NEW, RAISE
  # What a full channel does with a new event.

cls ChannelFull(RuntimeError)
  # Raised by :meth:`BaseEventChannel.publish` when overflow is ``RAISE`` and the queue is full.
  __init__(name: str, maxsize: int) -> None

cls ChannelClosed(RuntimeError)
  # Raised when publishing to a closed channel.
  __init__(name: str) -> None

cls BaseEventChannel(ABC)
  # A named, bounded event pipe. One producer side, one drain (consumer) side.
  async publish(event: Event) -> bool
    # Enqueue ``event``. Return ``True`` if accepted, ``False`` if dropped by policy.
  stream() -> AsyncIterator[Event]
    # Async-iterate delivered events until the channel is closed.
  async close() -> None
    # Stop the channel and unblock the drain. Idempotent.

```

## memory.py
```
# ``MemoryEventChannel`` — in-process bounded channel over :class:`asyncio.Queue`.

_CLOSE = object()

cls MemoryEventChannel(BaseEventChannel)
  # Bounded in-process channel. Single drain consumer (the dispatcher's worker).
  __init__(name: str) -> None
  async publish(event: Event) -> bool
  async stream() -> AsyncIterator[Event]
  async close() -> None
  qsize() -> int

```

## registry.py
```
# ``ChannelRegistry`` — owns push channels and drains each into a sink coroutine.


cls ChannelRegistry
  __init__(sink: EventSink) -> None
  register(channel: BaseEventChannel) -> BaseEventChannel
  get(name: str) -> BaseEventChannel | None
  async publish(name: str, event: Event) -> bool
  start() -> None
    # Spawn a drain task per channel that isn't already draining. Idempotent.
  async close() -> None
    # Close every channel and await its drain. Idempotent.

```

# pagination/

Async paginators for the two shapes Avito surfaces (no opaque cursors).

## Contract

- `BasePaginator[T]` — abstract async-iterable. Subclasses implement
  `_advance() -> (items, has_next)`. The base owns:
  * the `async for` loop and per-item yield;
  * a page counter (`pages_fetched`);
  * the runaway guard — raises `RunawayPagination` when `pages_fetched >=
    max_pages`. Default `max_pages` comes from
    `ClientConfig.pagination_max_pages` (1000).
- `IndexPaginator[T]` — `page` + `per_page` shape. Constructor takes a
  `method_factory(page, per_page) -> BaseMethod[Page[T]]`. Stops on a
  short page OR when `len(yielded) >= total`. `start_page` defaults to 1
  (Avito convention).
- `TimeWindowPaginator[T]` — `date_from`/`date_to` + offset shape.
  Constructor takes `method_factory(date_from, date_to, limit, offset)`.
  Stops on a short page OR when `offset > max_offset` (default 10_000).

Both paginators are **async iterators**, not awaitables. Use them with
`async for x in client.iter_X(...)` — `await client.iter_X(...)` is a
bug.

## Why two paginators

Avito has no opaque cursors. The `page`/`per_page` shape is used for
items, reviews, operations history; the time-window shape is used for
messenger chats, calls, CPA stats. The Client exposes one `iter_*` per
endpoint; the paginators are the shared engines.

## Don'ts

- Don't `await` a paginator. They are async iterators.
- Don't reuse one instance across two `async for` loops. State (page
  index / offset) is not reset.
- Don't compute a `max_pages` bound to limit expensive runs — use a
  per-call `max_pages` constructor argument; the guard exists exactly
  for that.
- Don't pass a `start_page=0`. Avito pages start at 1.

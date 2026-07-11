# pagination/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

> Declarative pagination — methods carry pagination fields, ``Client`` auto-dispatches.

## __init__.py
```
# Declarative pagination — methods carry pagination fields, ``Client`` auto-dispatches.


```

## method.py
```
# Paginated method base classes — declarative ``offset/limit`` and ``page/per_page``.

T = TypeVar('T')
_DEFAULT_PAGE_SIZE_OFFSET = 50
_DEFAULT_PAGE_SIZE_NUMBERED = 25
_DEFAULT_MAX_OFFSET = 10000

cls PaginatedMethod(BaseMethod[T], Generic[T])

cls OffsetMethod(PaginatedMethod[T], Generic[T])

cls PageMethod(PaginatedMethod[T], Generic[T])

```

## paginator.py
```
# ``MethodPaginator`` / ``CursorPaginator`` — drive paginated methods to exhaustion.

T = TypeVar('T')
_DEFAULT_MAX_PAGES = 1000

cls CursorPage(Generic[T]): items: list[T], next_cursor: str | None

cls MethodPaginator(Generic[T])
  __init__(client: Client, method: PaginatedMethod[Any) -> None
  pages_fetched() -> int
  max_pages() -> int
  with_max_pages(max_pages: int) -> Self
    # Return a fresh paginator with an adjusted runaway cap.
  async fetch_page() -> object
  async all() -> list[T]
    # Collect every page into one list. ``RunawayPagination`` if uncapped.
  async first() -> T | None
    # Return the first item across pages, or ``None`` if empty.

cls CursorPaginator(Generic[T])
  __init__(fetch_fn: Callable[[str?], Awaitable[CursorPage[T) -> None
  pages_fetched() -> int
  async fetch_page() -> CursorPage[T]
  async all() -> list[T]
    # Collect every page into one list.
  async first() -> T | None
    # Return the first item, or ``None`` if empty.

_page_storage_key(paginator_id: str, caller_id: str) -> str

```

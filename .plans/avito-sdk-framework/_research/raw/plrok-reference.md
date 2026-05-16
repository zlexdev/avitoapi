# PlayerokAPI SDK Structure Reference

**Date:** May 2026
**Analyzed:** plrk2/PlayerokAPI (primary) vs chak-chak/playerokapi (comparison)
**Purpose:** Template for Avito SDK framework

## File Tree

PlayerokAPI/
├── account.py (1459 lines - main facade)
├── apihelper.py (1318 lines - HTTP/GraphQL transport)
├── exceptions.py (570 lines - error hierarchy)
├── states.py (FSM context)
├── const.py (MESSAGE_LENGHT_LIMIT, BOT_CHAR)
├── methods/ (auth.py, properties.py mixins)
├── types/ (~90 Pydantic models with binding)
├── categories/ (Steam, Telegram, etc - static const classes)
├── common/ (enums, queries, urls, api_utils)
├── _graphql/ (methods.py - GraphQL operation classes)
└── updater/ (processor, router, events, background threads)

## 2. Key Architecture Patterns

### Account Class (account.py)
- Central facade for all API operations
- Extends Properties mixin (for organization)
- Holds: token, api (API_helper), runner (Processor), states (FSMContext), me (User cache)
- ~50 public methods: get_me, create_lot, update_deal, send_message, etc.
- Rate limiting: _delays dict + _handle_delay(method) before execution
- Serialization: to_dict() / from_dict() for persistence

### API Helper (apihelper.py)
- GraphQL HTTP transport for https://playerok.com/graphql
- curl_cffi (TLS client) + proxy rotation
- Task queue for async concurrency
- ETag caching + retry logic (5 attempts)
- Error handling: CloudFlare detection, domain-specific exceptions
- Headers: Bearer auth + HTTP/2 pseudo-headers + Sentry trace context

### Types/Models (types/)
- Base: Model(Pydantic BaseModel + AccountContext)
- as_(account) binding → models carry parent reference
- from_dict() deserialization → each type validates GraphQL response
- ~90 files: User, Chat, Deal, MyItem, Game*, Transaction*, etc.
- Binding pattern: user = User.de_json(resp).as_(self) → access account methods

### Methods (methods/)
- Mixin classes with @classmethod validators
- Example: AuthMethods.is_error(), is_valid_code()
- Account inherits from these for organization while maintaining flat API

### GraphQL Operations (_graphql/methods.py)
- Simple classes store query + operationName
- class CreateBanner: query = "...", operationName = "createBanner"
- Used by apihelper for mutation/query dispatch

### Categories (categories/)
- Static classes: Steam, Telegram, etc.
- ID, Slug, Tags, sub-category UUIDs
- Used in item filtering, UI, category lookups

### Exceptions (exceptions.py)
- Hierarchy: RequestFailedError → CloudflareError, InternalServerError
- 15+ custom errors with pattern matching on GraphQL response
- Factory: _InternalError() creates errors dynamically
- Examples: ItemMustNotUpdateError, NotEnoughFundsError, Unauthorized

### States (states.py)
- FSMContext: per-user dialogue state tracking
- set_state(), get_state_user(), clear_state()
- Used in Account.states for chat-based FSM

### Updater/Events (updater/)
- Processor: main event loop (polls chats, routes handlers)
- Router: register handlers for event types
- BaseEvent: filter + kwargs for matching
- Events: NewMessage, NewOrder, SystemMessage, OrderConfirmed, etc.
- Handler binding: @account.on(NewMessage(...))

## 3. Comparison: chak-chak/playerokapi (Older)

| Aspect | plrk2 | chak-chak |
|--------|-------|-----------|
| Client | Monolithic Account | Singleton via __new__ |
| Types | ~90 separate Pydantic files | Single types.py |
| Transport | curl_cffi + ETag cache | tls_requests, basic |
| Events | Full updater/processor system | Simple listener |
| GraphQL | _graphql/ folder with classes | misc.py PERSISTED_QUERIES dict |
| Exceptions | 15+ custom w/ factory | Simple flat |
| Architecture | Modular (categories/, methods/, common/) | Monolithic (parser.py) |

Verdict: plrk2 is production, modular. chak-chak is POC.

## 4. Patterns to Replicate in Avito SDK

1. **Flat Client Interface** - Single Account/Client class, all methods directly exposed
   - `client.create_item()` NOT `client.items.create()`

2. **Mixin-Based Composition** - Account inherits from method classes for organization

3. **GraphQL-First HTTP Layer** - Abstract transport with retry, CF detection, proxy rotation

4. **Pydantic Models with Binding** - Models carry parent Account reference via as_()
   - from_dict() deserialization
   - Enables bound methods

5. **GraphQL Queries as Classes** - Simple dataclass-like objects with query + operationName

6. **Rate Limiting per Method** - _delays dict + _handle_delay() blocking sleep

7. **Event-Driven Polling** (Optional) - Separate updater/processor/router modules
   - Event filtering (BaseEvent + kwargs)
   - Handler routing, background threads
   - Account.runner integration

8. **Type-Safe Enums & Constants** - common/enums.py + categories/ static classes

9. **Layered Exception Hierarchy** - Factory pattern for pattern-matched GraphQL errors
   - Base → domain → API-specific
   - _InternalError() factory

10. **Serialization First** - to_dict() / from_dict() / de_json() for persistence

11. **Pagination Abstraction** - EdgesKw TypedDict + paginate_results() utility
    - Account methods accept **kwargs: Unpack[EdgesKw]

12. **State Machine for Chats** (Optional) - FSMContext for per-user dialogue state

## 5. Implementation Checklist

- [ ] Single flat Client class with all methods
- [ ] Mixin-based internal organization
- [ ] GraphQL HTTP transport layer
- [ ] ~50 Pydantic type models with binding
- [ ] GraphQL queries in simple operation classes
- [ ] Rate limiting per method
- [ ] Exception hierarchy with pattern matching
- [ ] Serialization (to_dict/from_dict)
- [ ] Pagination wrapper utility
- [ ] Optional: Event polling + updater
- [ ] Optional: FSM context

---

**Document Created:** May 16, 2026
**Status:** Reference design for Avito SDK
**Word Count:** ~1100

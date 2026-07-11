"""Flat ``Client`` facade — every Avito Partner API method bound directly here."""

from __future__ import annotations

import contextlib
from collections.abc import Coroutine
from types import TracebackType
from typing import (  # typed-Any: MethodPaginator[Any]/Coroutine[Any,...] = erased-T holders
    TYPE_CHECKING,
    Any,
    Self,
    TypeVar,
    overload,
)

from .auth.oauth import OAuthClient, OAuthInjectorMiddleware, TokenCache
from .config import ClientConfig
from .facade.accounts_hierarchy import AccountsHierarchyFacade
from .facade.ads import AdsFacade
from .facade.auction import AuctionFacade
from .facade.auth import AuthFacade
from .facade.autoload import AutoloadFacade
from .facade.autostrategy import AutostrategyFacade
from .facade.autoteka import AutotekaFacade
from .facade.avito_promo import AvitoPromoFacade
from .facade.calltracking import CalltrackingFacade
from .facade.cpa import CpaFacade
from .facade.cpxpromo import CpxpromoFacade
from .facade.delivery import DeliveryFacade
from .facade.items import ItemsFacade
from .facade.job import JobFacade
from .facade.messenger import MessengerFacade
from .facade.order_management import OrderManagementFacade
from .facade.promotion import PromotionFacade
from .facade.realty_reports import RealtyReportsFacade
from .facade.reviews import ReviewsFacade
from .facade.short_term_rental import ShortTermRentalFacade
from .facade.special_offers import SpecialOffersFacade
from .facade.stock_management import StockManagementFacade
from .facade.tariff import TariffFacade
from .facade.trxpromo import TrxpromoFacade
from .facade.user import UserFacade
from .logging import get_logger
from .methods._base import BaseMethod
from .pagination import MethodPaginator, PaginatedMethod
from .sessions import create_default_session
from .sessions.base import BaseSession
from .storage.base import BaseStorage
from .storage.memory import MemoryStorage
from .transport.proxy._base import BaseProxyTransport, NoProxyTransport
from .types import HealthState, HealthStatus

if TYPE_CHECKING:
    from .sessions.middleware import RequestMiddlewareManager

log = get_logger(__name__)

TR = TypeVar("TR")


class Client(
    AccountsHierarchyFacade,
    AdsFacade,
    AuctionFacade,
    AuthFacade,
    AutoloadFacade,
    AutostrategyFacade,
    AutotekaFacade,
    AvitoPromoFacade,
    CalltrackingFacade,
    CpaFacade,
    CpxpromoFacade,
    DeliveryFacade,
    ItemsFacade,
    JobFacade,
    MessengerFacade,
    OrderManagementFacade,
    PromotionFacade,
    RealtyReportsFacade,
    ReviewsFacade,
    ShortTermRentalFacade,
    SpecialOffersFacade,
    StockManagementFacade,
    TariffFacade,
    TrxpromoFacade,
    UserFacade,
):
    """Async SDK facade for the Avito Partner API.

    Two execution surfaces, both routed through ``session.make_request(client, method)``:

    * ``await client.get_user_info_self()`` — flat method (the common path), bound via the
      generated ``*Facade`` mixins listed as bases.
    * ``await client(SomeMethod())`` — universal, accepts any :class:`BaseMethod`.

    Construct inside an async context::

        async with Client(config=ClientConfig.from_env()) as client:
            me = await client.get_user_info_self()

    Shared infra (session pool, storage, proxy transport) can be injected so
    multi-account dashboards share one HTTP client and one storage backend
    while each ``Client`` keeps its own per-account namespace and account_id.
    """

    def __init__(
        self,
        *,
        config: ClientConfig,
        session: BaseSession | None = None,
        storage: BaseStorage[object, str] | None = None,
        transport: BaseProxyTransport | None = None,
        account_id: str | None = None,
    ) -> None:
        self.config = config
        self.account_id = account_id
        self.storage: BaseStorage[object, str] = storage or MemoryStorage()
        proxy_transport = transport or NoProxyTransport()
        self.session: BaseSession = session or create_default_session(
            config,
            proxy_transport=proxy_transport,
        )

        self._oauth = OAuthClient(
            config=config,
            http=self.session,
            cache=TokenCache(self.storage),
        )
        self._auth_middleware = OAuthInjectorMiddleware(
            self._oauth,
            cache_key_builder=self._build_oauth_cache_key,
        )
        self.session.request_middlewares.register(self._auth_middleware)

    async def __aenter__(self) -> Self:
        await self.open()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.close()

    async def open(self) -> None:
        """Initialise pooled resources. Idempotent."""

        await self.session.open()

    async def close(self) -> None:
        """Tear down session + storage. Idempotent."""

        with contextlib.suppress(Exception):
            await self.session.close()
        with contextlib.suppress(Exception):
            await self.storage.close()

    @overload
    def __call__(self, method: PaginatedMethod[TR]) -> MethodPaginator[Any]: ...  # type: ignore[overload-overlap]
    @overload
    def __call__(self, method: BaseMethod[TR]) -> Coroutine[Any, Any, TR]: ...
    def __call__(
        self,
        method: BaseMethod[TR],
    ) -> MethodPaginator[Any] | Coroutine[Any, Any, TR]:
        """Universal executor with auto-pagination dispatch.

        * :class:`PaginatedMethod` subclass → returns a :class:`MethodPaginator`
          (both ``await``-able for the first page and ``async for``-iterable
          across every page).
        * Anything else → returns the awaitable coroutine.

        Examples::

            me = await client(GetUserInfoSelf())        # one wire call
            async for chat in client(ListChats(user_id=42)):
                ...
            first_page = await client(ListChats(user_id=42))  # first-page envelope
        """

        if isinstance(method, PaginatedMethod):
            return self.paginate(method)
        return self.execute(method)

    async def execute(self, method: BaseMethod[TR]) -> TR:
        """Run one non-paginated method and return its decoded result.

        The generated facade methods call this (``await self.execute(...)``) — an explicit
        coroutine return type, unlike the overloaded :meth:`__call__`, so IDE async
        inspections don't flag the ``await`` at every call site.
        """

        return await method.as_(self).emit(self)

    def paginate(self, method: PaginatedMethod[TR]) -> MethodPaginator[Any]:
        """Wrap a paginated method in a :class:`MethodPaginator` (await first page / async-for all)."""

        return MethodPaginator(self, method)

    @property
    def request_middlewares(self) -> RequestMiddlewareManager:
        """Manager for request-side middlewares (auth, tracing, custom logging)."""
        return self.session.request_middlewares

    @property
    def oauth(self) -> OAuthClient:
        """Direct access to the OAuth client (for one-off ``authorization_code`` flows)."""
        return self._oauth

    async def healthcheck(self) -> HealthStatus:
        """Aggregate health: storage round-trip + session liveness."""

        storage_ok = await self.storage.health()
        sessions = {"www": not getattr(self.session, "_closed", False)}
        all_ok = storage_ok and all(sessions.values())
        return HealthStatus(
            state=HealthState.OK if all_ok else HealthState.DEGRADED,
            storage=storage_ok,
            sessions=sessions,
        )

    def _user_id(self, override: int | None) -> int:
        if override is not None:
            return override
        if self.config.user_id is None:
            raise ValueError(
                "user_id not set: pass `user_id=...` or configure "
                "`ClientConfig.user_id` for the authorization_code grant",
            )
        return self.config.user_id

    def _build_oauth_cache_key(self, client: Self) -> str:
        return self._oauth.cache_key_for(user_id=client.config.user_id)

"""Flat ``Client`` facade — every Avito Partner API method bound directly here."""

from __future__ import annotations

import contextlib
from collections.abc import Coroutine
from datetime import date, datetime
from decimal import Decimal
from types import TracebackType
from typing import TYPE_CHECKING, Any, Self, TypeVar, overload

from .auth.oauth import OAuthClient, OAuthInjectorMiddleware, TokenCache
from .auth.solvers.base import ChallengeSolver, NullSolver
from .config import ClientConfig
from .logging import get_logger
from .methods._base import BaseMethod
from .methods.accounts import GetSelf
from .methods.accounts_hierarchy import (
    CheckAhUser,
    GetEmployees,
    LinkItems,
    ListCompanyPhones,
    ListItemsByEmployee,
)
from .methods.auction import GetAuctionBids, SetAuctionBids
from .methods.autoload import (
    AutoloadItemStatus,
    ConvertAutoloadId,
    GetAutoloadCategoryFields,
    GetAutoloadProfile,
    GetAutoloadReport,
    GetLastAutoloadReport,
    ListAutoloadReports,
    UpdateAutoloadProfile,
    UploadAutoloadFile,
)
from .methods.autostrategy import (
    CreateAutostrategyCampaign,
    EditAutostrategyCampaign,
    GetAutostrategyCampaignInfo,
    GetAutostrategyStats,
    ListAutostrategyCampaigns,
    SetAutostrategyBudget,
    StopAutostrategyCampaign,
)
from .methods.autoteka import (
    AutotekaFullReport,
    AutotekaPreviewByRegnum,
    AutotekaPreviewByVin,
)
from .methods.balance import GetBalance, GetBalanceBonus, OperationsHistory
from .methods.calltracking import GetCall, GetCallRecording, ListCalls
from .methods.cpa import (
    CallsByTime,
    CancelComplaint,
    ChatByActionId,
    ChatsByTime,
    CpaBalance,
    CreateComplaint,
    ListComplaints,
)
from .methods.cpxpromo import (
    GetCpxBids,
    GetCpxPromotionsByItems,
    RemoveCpxPromotion,
    SetCpxAutoPromotion,
    SetCpxManualPromotion,
)
from .methods.delivery import (
    BatchChangeParcels,
    CancelAnnouncement,
    CancelAnnouncementV1,
    CancelParcel,
    CancelParcelV1,
    ChangeParcelResult,
    ChangeParcelV1,
    CheckConfirmationCode,
    CreateAnnouncement,
    CreateAnnouncementV1,
    CreateAnnouncementV1Alt,
    CreateParcel,
    CreateParcelV2,
    GetAnnouncementEventV1,
    GetChangeParcelInfoV1,
    GetDeliveryTask,
    GetOrderRealAddress,
    GetOrderTracking,
    GetParcelInfoV1,
    GetRegisteredParcelIdV1,
    GetSortingCenter,
    ListTariffAreas,
    ListTariffSortingCenters,
    ListTariffsV2,
    ListTariffTerminals,
    ListTariffTerms,
    ProhibitOrderAcceptance,
    SetAreaCustomSchedule,
    SetOrderProperties,
    SetSortingCenterTariff,
    TrackAnnouncementV1,
)
from .methods.items import (
    ApplyVas,
    ApplyVasPackage,
    ApplyVasV2,
    ArchiveItem,
    GetItem,
    ListItems,
    UpdateItemPrice,
)
from .methods.job import GetResume, GetResumeContacts, SearchResumes
from .methods.messenger import (
    AddBlacklist,
    DeleteMessage,
    GetChat,
    GetVoiceFiles,
    ListBlacklist,
    ListChats,
    ListMessages,
    ListSubscriptions,
    MarkChatRead,
    RemoveBlacklist,
    SendImageMessage,
    SendTextMessage,
    SubscribeWebhook,
    UnsubscribeWebhook,
    UploadImage,
)
from .methods.order_management import (
    AcceptReturnOrder,
    ApplyOrderTransition,
    CheckOrderConfirmationCode,
    CncSetOrderDetails,
    CreateOrderLabels,
    CreateOrderLabelsExtended,
    DownloadOrderLabels,
    GetCourierDeliveryRange,
    ListManagedOrders,
    SetCourierDeliveryRange,
    SetOrderMarkings,
    SetOrderTrackingNumber,
)
from .methods.orders import (
    ChangeOrderStatus,
    GetOrder,
    ListOrders,
    RefundOrder,
    TransferDeliveryTerms,
    TransferTrackNumber,
)
from .methods.promotion import (
    BbipForecast,
    CreateBbipOrder,
    DropPromotion,
    ListActivePromotions,
    ListBids,
)
from .methods.realty import (
    GetCalendar,
    GetPeriodPrices,
    ItemBookings,
    ListBookings,
    UpdatePeriodPrices,
)
from .methods.realty_reports import CreateRealtyReport, GetMarketPriceCorrespondence
from .methods.reviews import (
    DeleteReviewReply,
    GetReviewInfo,
    ListReviews,
    ReplyToReview,
)
from .methods.special_offers import (
    GetAvailableOffers,
    GetOffersStats,
    GetOfferTariffInfo,
    MultiConfirmOffers,
    MultiCreateOffers,
    OfferDraft,
)
from .methods.stats import CallStats, ItemStatsDeep, ItemStatsShallow, Spendings
from .methods.stock_management import GetStockInfo, UpdateStocks
from .methods.tariff import GetTariffInfo
from .methods.trxpromo import ApplyTrxPromo, CancelTrxPromo, GetTrxCommissions
from .models.accounts import Account
from .models.accounts_hierarchy import (
    AhUserStatus,
    EmployeeList,
    ItemList,
    LinkItemsResult,
    PhoneList,
)
from .models.auction import AuctionBid, AuctionBidList, SetAuctionBidsResult
from .models.autostrategy import (
    AutostrategyStatList,
    BudgetUpdateResult,
    CampaignActionResult,
    CampaignInfo,
    CampaignList,
)
from .models.balance import Balance, BalanceBonus, Operation, OperationList
from .models.common import Money
from .models.cpxpromo import CpxActionResult, CpxBidList, CpxPromotionList
from .models.delivery import (
    Announcement,
    AnnouncementEvent,
    AnnouncementId,
    ChangeParcelInfo,
    ConfirmationCheck,
    DeliveryTask,
    GenericDeliveryResult,
    OrderProperties,
    Parcel,
    ParcelChangeResult,
    ParcelInfo,
    ParcelTracking,
    RealAddress,
    RegisteredParcelId,
    SortingCenter,
    SortingCenterList,
    Tariff,
    TariffAreaList,
    TariffList,
    TariffTermList,
    TerminalList,
)
from .models.items import Item, ItemStatus, VasOrderResult
from .models.order_management import (
    CncDetailsResult,
    CourierDeliveryRange,
    LabelTaskResult,
    ManagedOrderList,
    MarkingResult,
    OrderConfirmationCheck,
    OrderMarking,
    OrderTransition,
)
from .models.orders import OrderStatus, assert_order_transition
from .models.promotion import BbipForecast as BbipForecastModel
from .models.realty_reports import MarketPriceCorrespondence, RealtyReportTask
from .models.special_offers import (
    AvailableOfferList,
    OfferConfirmationList,
    OfferCreateResultList,
    OfferStatList,
    OfferTariffInfo,
)
from .models.stats import CallStatList, ItemViewStatsList
from .models.stock_management import StockInfo, StockInfoList, StockUpdateResult
from .models.tariff import TariffInfo
from .models.trxpromo import TrxApplyResult, TrxCancelResult, TrxCommissionList
from .pagination import MethodPaginator, PaginatedMethod
from .sessions import create_default_session
from .sessions.base import BaseSession
from .storage.base import BaseStorage
from .storage.memory import MemoryStorage
from .types import HealthState, HealthStatus
from .utils.proxy._base import BaseProxyTransport, NoProxyTransport

if TYPE_CHECKING:
    from datetime import date

    from .models.autoload import (
        AutoloadCategoryFields,
        AutoloadIdConversion,
        AutoloadItemReport,
        AutoloadProfile,
        AutoloadReport,
        AutoloadUploadResult,
    )
    from .models.autoteka import AutotekaFullReport as AutotekaFullReportDoc
    from .models.autoteka import AutotekaPreview
    from .models.calltracking import Call, CallList
    from .models.cpa import (
        CallList as CpaCallList,
    )
    from .models.cpa import (
        ChatByTime,
        ChatList,
        Complaint,
        CpaBalanceInfo,
    )
    from .models.job import Resume, ResumeContact
    from .models.messenger import (
        Blacklist,
        Chat,
        DeleteResult,
        MessageEnvelope,
        SubscriptionList,
        UploadImageResult,
        VoiceFiles,
        WebhookActionResult,
    )
    from .models.orders import Order
    from .models.promotion import BbipOrder, BidList, PromotionList
    from .models.realty import BookingList, Calendar, PeriodPriceList
    from .models.reviews import RatingInfo, ReviewReply
    from .sessions.middleware import RequestMiddlewareManager

log = get_logger(__name__)

TR = TypeVar("TR")


class Client:
    """Async SDK facade for the Avito Partner API.

    Two execution surfaces, both routed through ``session.make_request(client, method)``:

    * ``await client.get_self()`` — flat method (the common path).
    * ``await client(GetSelf())`` — universal, accepts any :class:`BaseMethod`.

    Construct inside an async context::

        async with Client(config=ClientConfig.from_env()) as client:
            me = await client.get_self()

    Shared infra (session pool, storage, proxy transport) can be injected so
    multi-account dashboards share one HTTP client and one storage backend
    while each ``Client`` keeps its own per-account namespace and account_id.
    """

    def __init__(
        self,
        *,
        config: ClientConfig,
        session: BaseSession | None = None,
        storage: BaseStorage[Any, str] | None = None,
        solver: ChallengeSolver | None = None,
        transport: BaseProxyTransport | None = None,
        account_id: str | None = None,
    ) -> None:
        self.config = config
        self.account_id = account_id
        self.storage: BaseStorage[Any, str] = storage or MemoryStorage()
        self.solver: ChallengeSolver = solver or NullSolver()
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
    def __call__(self, method: PaginatedMethod[TR]) -> MethodPaginator[Any]: ...
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

            me = await client(GetSelf())                # one wire call
            async for chat in client(ListChats(user_id=42)):
                ...
            first_page = await client(ListChats(user_id=42))  # first-page envelope
        """

        if isinstance(method, PaginatedMethod):
            return MethodPaginator(self, method)
        return method.as_(self).emit(self)

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

    async def get_self(self) -> Account:
        return await self(GetSelf())

    def list_items(
        self,
        *,
        status: ItemStatus | None = None,
        per_page: int = 25,
        start_page: int = 1,
        max_pages: int | None = None,
    ) -> MethodPaginator[Item]:
        """Async-iterate every page of own items via ``GET /core/v1/items``.

        Returns a :class:`MethodPaginator` ready to ``async for``::

            async for item in client.list_items():
                ...
        """

        method = ListItems(page=start_page, per_page=per_page, status=status)
        paginator: MethodPaginator[Item] = self(method)
        return paginator if max_pages is None else paginator.with_max_pages(max_pages)

    async def get_item(self, item_id: int, *, user_id: int | None = None) -> Item:
        return await self(
            GetItem(user_id=self._user_id(user_id), item_id=item_id),
        )

    async def update_item_price(
        self,
        item_id: int,
        price: Decimal | int,
        *,
        user_id: int | None = None,
    ) -> Item:
        """Update the price of a single item. Auto-injects ``Idempotency-Key``."""
        return await self(
            UpdateItemPrice(
                user_id=self._user_id(user_id),
                item_id=item_id,
                price=int(price),
            ),
        )

    async def apply_vas(
        self,
        item_ids: list[int],
        slug: str,
        *,
        user_id: int | None = None,
    ) -> VasOrderResult:
        return await self(
            ApplyVas(user_id=self._user_id(user_id), item_ids=item_ids, slug=slug),
        )

    async def apply_vas_package(
        self,
        item_ids: list[int],
        package_id: int,
        *,
        user_id: int | None = None,
    ) -> VasOrderResult:
        return await self(
            ApplyVasPackage(
                user_id=self._user_id(user_id),
                item_ids=item_ids,
                package_id=package_id,
            ),
        )

    async def apply_vas_v2(
        self,
        item_id: int,
        package_id: int,
        *,
        user_id: int | None = None,
    ) -> VasOrderResult:
        return await self(
            ApplyVasV2(
                user_id=self._user_id(user_id),
                item_id=item_id,
                package_id=package_id,
            ),
        )

    async def archive_item(self, item_id: int, *, user_id: int | None = None) -> None:
        """Archive (delete) an item. Avito returns 2xx with no body."""
        return await self(
            ArchiveItem(user_id=self._user_id(user_id), item_id=item_id),
        )

    async def item_stats_shallow(
        self,
        item_ids: list[int],
        date_from: date,
        date_to: date,
        *,
        user_id: int | None = None,
    ) -> ItemViewStatsList:
        """Bulk shallow stats — caps at 200 ids and 270 days, both checked client-side."""
        return await self(
            ItemStatsShallow(
                user_id=self._user_id(user_id),
                item_ids=item_ids,
                date_from=date_from,
                date_to=date_to,
            ),
        )

    async def item_stats_deep(
        self,
        item_ids: list[int],
        date_from: date,
        date_to: date,
        *,
        user_id: int | None = None,
        fields: list[str] | None = None,
    ) -> ItemViewStatsList:
        """Deep stats — per-item, per-day rows for the requested fields."""
        return await self(
            ItemStatsDeep(
                user_id=self._user_id(user_id),
                item_ids=item_ids,
                date_from=date_from,
                date_to=date_to,
                fields=fields if fields is not None else ["views", "contacts", "favorites"],
            ),
        )

    async def call_stats(
        self,
        item_id: int,
        *,
        user_id: int | None = None,
    ) -> CallStatList:
        return await self(
            CallStats(user_id=self._user_id(user_id), item_id=item_id),
        )

    async def spendings(
        self,
        date_from: datetime,
        date_to: datetime,
        *,
        user_id: int | None = None,
    ) -> OperationList:
        """Profile spendings in a time window — returns a bare list of operations."""
        return await self(
            Spendings(
                user_id=self._user_id(user_id),
                date_from=date_from,
                date_to=date_to,
            ),
        )

    async def get_balance(self, *, user_id: int | None = None) -> Balance:
        return await self(GetBalance(user_id=self._user_id(user_id)))

    async def get_balance_bonus(self, *, user_id: int | None = None) -> BalanceBonus:
        return await self(GetBalanceBonus(user_id=self._user_id(user_id)))

    def operations_history(
        self,
        date_from: datetime,
        date_to: datetime,
        *,
        per_page: int = 25,
        max_pages: int | None = None,
    ) -> MethodPaginator[Operation]:
        """Async-iterate every page of wallet operations in a date range."""

        method = OperationsHistory(
            date_from=date_from,
            date_to=date_to,
            per_page=per_page,
        )
        paginator: MethodPaginator[Operation] = self(method)
        return paginator if max_pages is None else paginator.with_max_pages(max_pages)

    def list_chats(
        self,
        *,
        unread_only: bool | None = None,
        item_ids: list[int] | None = None,
        limit: int = 100,
        max_pages: int | None = None,
    ) -> MethodPaginator[Any]:
        """Async-iterate messenger chats. Walks ``limit`` + ``offset`` shape."""

        method = ListChats(
            user_id=self._user_id(None),
            unread_only=unread_only,
            item_ids=item_ids,
            limit=limit,
        )
        paginator: MethodPaginator[Any] = self(method)
        return paginator if max_pages is None else paginator.with_max_pages(max_pages)

    async def get_chat(self, chat_id: str) -> Chat:
        return await self(GetChat(user_id=self._user_id(None), chat_id=chat_id))

    def list_messages(
        self,
        chat_id: str,
        *,
        limit: int = 50,
        max_pages: int | None = None,
    ) -> MethodPaginator[Any]:
        """Async-iterate message history for one chat."""

        method = ListMessages(
            user_id=self._user_id(None),
            chat_id=chat_id,
            limit=limit,
        )
        paginator: MethodPaginator[Any] = self(method)
        return paginator if max_pages is None else paginator.with_max_pages(max_pages)

    async def send_text_message(self, chat_id: str, text: str) -> MessageEnvelope:
        return await self(
            SendTextMessage(user_id=self._user_id(None), chat_id=chat_id, text=text),
        )

    async def send_image_message(self, chat_id: str, image_id: str) -> MessageEnvelope:
        """Send a previously-uploaded image (by :class:`UploadImage` id)."""
        return await self(
            SendImageMessage(
                user_id=self._user_id(None),
                chat_id=chat_id,
                image_id=image_id,
            ),
        )

    async def mark_chat_read(self, chat_id: str) -> DeleteResult:
        return await self(MarkChatRead(user_id=self._user_id(None), chat_id=chat_id))

    async def delete_message(self, chat_id: str, message_id: str) -> DeleteResult:
        return await self(
            DeleteMessage(
                user_id=self._user_id(None),
                chat_id=chat_id,
                message_id=message_id,
            ),
        )

    async def upload_image(self, filename: str, image_bytes: bytes) -> UploadImageResult:
        """Upload a chat image. The returned id feeds :meth:`send_image_message`."""
        return await self(
            UploadImage(
                user_id=self._user_id(None),
                filename=filename,
                image_bytes=image_bytes,
            ),
        )

    async def list_blacklist(self) -> Blacklist:
        return await self(ListBlacklist(user_id=self._user_id(None)))

    async def add_blacklist(self, users: list[int]) -> DeleteResult:
        return await self(AddBlacklist(user_id=self._user_id(None), users=users))

    async def remove_blacklist(self, target_user_id: int) -> DeleteResult:
        return await self(
            RemoveBlacklist(
                user_id=self._user_id(None),
                target_user_id=target_user_id,
            ),
        )

    async def get_voice_files(self, voice_ids: list[str]) -> VoiceFiles:
        """Resolve voice ids (from :class:`VoiceMessage`) to playback URLs."""
        return await self(
            GetVoiceFiles(user_id=self._user_id(None), voice_ids=voice_ids),
        )

    def list_orders(
        self,
        *,
        per_page: int = 25,
        max_pages: int | None = None,
    ) -> MethodPaginator[Order]:
        """Async-iterate DBS orders. Use ``async for order in ...``."""

        paginator: MethodPaginator[Order] = self(ListOrders(per_page=per_page))
        return paginator if max_pages is None else paginator.with_max_pages(max_pages)

    async def get_order(self, order_id: str) -> Order:
        return await self(GetOrder(order_id=order_id))

    async def change_order_status(
        self,
        order_id: str,
        status: OrderStatus,
        *,
        current: OrderStatus | None = None,
        strict: bool = True,
    ) -> Order:
        """Move an order to a new status, guarded by the transition table.

        When ``current`` is provided, an illegal transition raises
        :class:`InvalidStateTransition` (or warns when ``strict=False``).
        """

        if current is not None:
            assert_order_transition(current, status, strict=strict)
        return await self(ChangeOrderStatus(order_id=order_id, status=status))

    async def transfer_delivery_terms(
        self,
        order_id: str,
        term_days: int,
        note: str | None = None,
    ) -> Order:
        return await self(
            TransferDeliveryTerms(order_id=order_id, term_days=term_days, note=note),
        )

    async def transfer_track_number(
        self,
        order_id: str,
        carrier: str,
        code: str,
    ) -> Order:
        return await self(
            TransferTrackNumber(order_id=order_id, carrier=carrier, code=code),
        )

    async def refund_order(self, order_id: str, reason: str | None = None) -> Order:
        return await self(RefundOrder(order_id=order_id, reason=reason))

    def list_reviews(
        self,
        *,
        per_page: int = 25,
        max_pages: int | None = None,
    ) -> MethodPaginator[Any]:
        """Async-iterate reviews."""

        paginator: MethodPaginator[Any] = self(ListReviews(per_page=per_page))
        return paginator if max_pages is None else paginator.with_max_pages(max_pages)

    async def get_review_info(self) -> RatingInfo:
        return await self(GetReviewInfo())

    async def reply_to_review(self, review_id: int, message: str) -> ReviewReply:
        return await self(ReplyToReview(review_id=review_id, message=message))

    async def delete_review_reply(self, answer_id: int) -> None:
        return await self(DeleteReviewReply(answer_id=answer_id))

    async def list_active_promotions(
        self,
        item_ids: list[int] | None = None,
    ) -> PromotionList:
        return await self(ListActivePromotions(item_ids=item_ids))

    async def drop_promotion(self, item_ids: list[int]) -> None:
        return await self(DropPromotion(item_ids=item_ids))

    async def list_bids(self, item_ids: list[int] | None = None) -> BidList:
        return await self(ListBids(item_ids=item_ids))

    async def create_bbip_order(self, item_ids: list[int], budget: int) -> BbipOrder:
        """Create a BBIP (budget-bound item promotion) order."""
        return await self(CreateBbipOrder(item_ids=item_ids, budget=budget))

    async def bbip_forecast(self, item_id: int) -> BbipForecastModel:
        return await self(BbipForecast(item_id=item_id))

    async def cpa_balance(self) -> CpaBalanceInfo:
        return await self(CpaBalance())

    async def calls_by_time(
        self,
        date_time_from: datetime,
        date_time_to: datetime,
    ) -> CpaCallList:
        return await self(
            CallsByTime(date_time_from=date_time_from, date_time_to=date_time_to),
        )

    async def chats_by_time(
        self,
        date_time_from: datetime,
        date_time_to: datetime,
    ) -> ChatList:
        return await self(
            ChatsByTime(date_time_from=date_time_from, date_time_to=date_time_to),
        )

    async def chat_by_action_id(self, action_id: str) -> ChatByTime:
        return await self(ChatByActionId(action_id=action_id))

    def list_complaints(
        self,
        *,
        per_page: int = 25,
        max_pages: int | None = None,
    ) -> MethodPaginator[Complaint]:
        """Async-iterate CPA complaints."""

        paginator: MethodPaginator[Complaint] = self(ListComplaints(per_page=per_page))
        return paginator if max_pages is None else paginator.with_max_pages(max_pages)

    async def create_complaint(
        self,
        action_id: str,
        kind: str,
        reason: str | None = None,
    ) -> Complaint:
        return await self(
            CreateComplaint(action_id=action_id, kind=kind, reason=reason),
        )

    async def cancel_complaint(self, complaint_id: str) -> None:
        return await self(CancelComplaint(complaint_id=complaint_id))

    async def autoload_item_status(self, ad_id: int) -> AutoloadItemReport:
        return await self(
            AutoloadItemStatus(user_id=self._user_id(None), ad_id=ad_id),
        )

    def list_autoload_reports(
        self,
        *,
        per_page: int = 25,
        max_pages: int | None = None,
    ) -> MethodPaginator[AutoloadReport]:
        """Async-iterate autoload-run reports."""

        method = ListAutoloadReports(user_id=self._user_id(None), per_page=per_page)
        paginator: MethodPaginator[AutoloadReport] = self(method)
        return paginator if max_pages is None else paginator.with_max_pages(max_pages)

    async def get_last_autoload_report(self) -> AutoloadReport:
        return await self(GetLastAutoloadReport(user_id=self._user_id(None)))

    async def get_autoload_report(self, report_id: str) -> AutoloadReport:
        return await self(
            GetAutoloadReport(user_id=self._user_id(None), report_id=report_id),
        )

    async def get_autoload_category_fields(
        self,
        category_id: int,
    ) -> AutoloadCategoryFields:
        return await self(GetAutoloadCategoryFields(category_id=category_id))

    async def get_autoload_profile(self) -> AutoloadProfile:
        return await self(GetAutoloadProfile())

    async def update_autoload_profile(
        self,
        *,
        feed_url: str | None = None,
        schedule: str | None = None,
        format: str = "xml",
    ) -> AutoloadProfile:
        """Persist the account's autoload profile (idempotent)."""
        return await self(
            UpdateAutoloadProfile(
                feed_url=feed_url,
                schedule=schedule,
                format=format,
            ),
        )

    async def upload_autoload_file(
        self,
        filename: str,
        file_bytes: bytes,
    ) -> AutoloadUploadResult:
        """Push a feed file (XML / CSV) into Avito's autoload pipeline."""
        return await self(
            UploadAutoloadFile(filename=filename, file_bytes=file_bytes),
        )

    async def convert_autoload_id(self, ad_id: str) -> AutoloadIdConversion:
        return await self(ConvertAutoloadId(ad_id=ad_id))

    async def get_call(self, call_id: str) -> Call:
        return await self(GetCall(call_id=call_id))

    async def list_calls(
        self,
        *,
        date_from: datetime,
        date_to: datetime,
    ) -> CallList:
        """All calls in a time window (single call — Avito doesn't paginate this surface)."""
        return await self(ListCalls(date_from=date_from, date_to=date_to))

    async def get_call_recording(self, call_id: str) -> bytes:
        """Fetch the raw ``audio/mpeg`` recording for a call."""
        return await self(GetCallRecording(call_id=call_id))

    def search_resumes(
        self,
        query: str,
        *,
        region: str | None = None,
        salary_from: int | None = None,
        per_page: int = 25,
        max_pages: int | None = None,
    ) -> MethodPaginator[Resume]:
        """Async-iterate résumé search results."""

        method = SearchResumes(
            query=query,
            region=region,
            salary_from=salary_from,
            per_page=per_page,
        )
        paginator: MethodPaginator[Resume] = self(method)
        return paginator if max_pages is None else paginator.with_max_pages(max_pages)

    async def get_resume(self, resume_id: str) -> Resume:
        return await self(GetResume(resume_id=resume_id))

    async def get_resume_contacts(self, resume_id: str) -> ResumeContact:
        """Reveal candidate email + phone (PII; idempotent to avoid double-charge)."""
        return await self(GetResumeContacts(resume_id=resume_id))

    async def list_bookings(
        self,
        *,
        date_from: date,
        date_to: date,
    ) -> BookingList:
        return await self(ListBookings(date_from=date_from, date_to=date_to))

    async def get_calendar(self, item_id: int) -> Calendar:
        return await self(GetCalendar(item_id=item_id))

    async def get_period_prices(self, item_id: int) -> PeriodPriceList:
        return await self(GetPeriodPrices(item_id=item_id))

    async def update_period_prices(
        self,
        item_id: int,
        prices: list[Any],
    ) -> None:
        """Replace period-price rules for one realty item (idempotent)."""

        await self(UpdatePeriodPrices(item_id=item_id, prices=prices))

    async def item_bookings(self, item_id: int) -> BookingList:
        return await self(
            ItemBookings(user_id=self._user_id(None), item_id=item_id),
        )

    async def autoteka_preview_by_vin(self, vin: str) -> AutotekaPreview:
        """Free Autoteka preview keyed by VIN."""
        return await self(AutotekaPreviewByVin(vin=vin))

    async def autoteka_preview_by_regnum(self, regnum: str) -> AutotekaPreview:
        """Free Autoteka preview keyed by Russian registration plate."""
        return await self(AutotekaPreviewByRegnum(regnum=regnum))

    async def autoteka_full_report(
        self,
        *,
        vin: str | None = None,
        regnum: str | None = None,
    ) -> AutotekaFullReportDoc:
        """Paid Autoteka full report — exactly one of ``vin`` / ``regnum`` required."""
        return await self(AutotekaFullReport(vin=vin, regnum=regnum))

    async def check_ah_user(self) -> AhUserStatus:
        return await self(CheckAhUser())

    async def get_employees(self) -> EmployeeList:
        return await self(GetEmployees())

    async def link_items(self, employee_id: int, item_ids: list[int]) -> LinkItemsResult:
        """Re-assign items to an employee (idempotent)."""
        return await self(LinkItems(employee_id=employee_id, item_ids=item_ids))

    async def list_company_phones(self) -> PhoneList:
        return await self(ListCompanyPhones())

    async def list_items_by_employee(
        self,
        employee_id: int,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> ItemList:
        return await self(
            ListItemsByEmployee(employee_id=employee_id, limit=limit, offset=offset),
        )

    async def get_auction_bids(self) -> AuctionBidList:
        return await self(GetAuctionBids())

    async def set_auction_bids(self, bids: list[AuctionBid]) -> SetAuctionBidsResult:
        """Replace CPA auction bids (idempotent)."""
        return await self(SetAuctionBids(bids=bids))

    async def get_market_price_correspondence(
        self,
        item_id: int,
        price: int,
    ) -> MarketPriceCorrespondence:
        return await self(
            GetMarketPriceCorrespondence(itemId=item_id, price=price),
        )

    async def create_realty_report(self, item_id: int) -> RealtyReportTask:
        """Kick off a realty report; returns a task handle (idempotent)."""
        return await self(CreateRealtyReport(itemId=item_id))

    async def get_stock_info(self, item_ids: list[int]) -> StockInfoList:
        return await self(GetStockInfo(item_ids=item_ids))

    async def update_stocks(self, stocks: list[StockInfo]) -> StockUpdateResult:
        """Bulk-update inventory rows (idempotent)."""
        return await self(UpdateStocks(stocks=stocks))

    async def get_tariff_info(self) -> TariffInfo:
        return await self(GetTariffInfo())

    async def get_available_offers(self, item_ids: list[int]) -> AvailableOfferList:
        return await self(GetAvailableOffers(item_ids=item_ids))

    async def multi_create_offers(self, offers: list[OfferDraft]) -> OfferCreateResultList:
        """Draft multiple offers in one call (idempotent)."""
        return await self(MultiCreateOffers(offers=offers))

    async def multi_confirm_offers(self, offer_ids: list[str]) -> OfferConfirmationList:
        """Commit previously-drafted offers in one call (idempotent)."""
        return await self(MultiConfirmOffers(offer_ids=offer_ids))

    async def get_offers_stats(self, offer_ids: list[str]) -> OfferStatList:
        return await self(GetOffersStats(offer_ids=offer_ids))

    async def get_offer_tariff_info(self) -> OfferTariffInfo:
        return await self(GetOfferTariffInfo())

    async def subscribe_webhook(
        self,
        url: str,
        *,
        secret: str | None = None,
    ) -> WebhookActionResult:
        """Register a messenger webhook (v3, idempotent)."""
        return await self(SubscribeWebhook(url=url, secret=secret))

    async def unsubscribe_webhook(self, url: str) -> WebhookActionResult:
        """Unregister a messenger webhook (idempotent)."""
        return await self(UnsubscribeWebhook(url=url))

    async def list_subscriptions(self) -> SubscriptionList:
        return await self(ListSubscriptions())

    async def create_parcel(self, payload: dict[str, Any] | None = None) -> Parcel:
        """Register a parcel via the legacy ``POST /createParcel`` surface."""
        return await self(CreateParcel(payload=payload or {}))

    async def list_tariff_areas(
        self,
        tariff_id: str,
        *,
        filters: dict[str, Any] | None = None,
    ) -> TariffAreaList:
        return await self(ListTariffAreas(tariff_id=tariff_id, filters=filters or {}))

    async def list_tariff_terms(
        self,
        tariff_id: str,
        *,
        filters: dict[str, Any] | None = None,
    ) -> TariffTermList:
        return await self(ListTariffTerms(tariff_id=tariff_id, filters=filters or {}))

    async def list_tariffs_v2(self, *, filters: dict[str, Any] | None = None) -> TariffList:
        return await self(ListTariffsV2(filters=filters or {}))

    async def set_area_custom_schedule(
        self,
        area_id: str,
        *,
        schedule: dict[str, Any] | None = None,
    ) -> GenericDeliveryResult:
        return await self(SetAreaCustomSchedule(area_id=area_id, schedule=schedule or {}))

    async def list_tariff_terminals(
        self,
        tariff_id: str,
        *,
        filters: dict[str, Any] | None = None,
    ) -> TerminalList:
        return await self(ListTariffTerminals(tariff_id=tariff_id, filters=filters or {}))

    async def get_delivery_task(self, task_id: str) -> DeliveryTask:
        return await self(GetDeliveryTask(task_id=task_id))

    async def cancel_parcel(
        self, parcel_id: str, *, reason: str | None = None
    ) -> ParcelChangeResult:
        return await self(CancelParcel(parcel_id=parcel_id, reason=reason))

    async def check_delivery_confirmation_code(self, order_id: str, code: str) -> ConfirmationCheck:
        return await self(CheckConfirmationCode(order_id=order_id, code=code))

    async def set_delivery_order_properties(
        self,
        order_id: str,
        properties: dict[str, Any],
    ) -> OrderProperties:
        return await self(SetOrderProperties(order_id=order_id, properties=properties))

    async def get_order_real_address(self, order_id: str) -> RealAddress:
        return await self(GetOrderRealAddress(order_id=order_id))

    async def get_order_tracking(self, order_id: str) -> ParcelTracking:
        return await self(GetOrderTracking(order_id=order_id))

    async def prohibit_order_acceptance(
        self,
        order_id: str,
        *,
        reason: str | None = None,
    ) -> GenericDeliveryResult:
        return await self(ProhibitOrderAcceptance(order_id=order_id, reason=reason))

    async def change_parcel_result(
        self,
        parcel_id: str,
        result: dict[str, Any],
    ) -> ParcelChangeResult:
        return await self(ChangeParcelResult(parcel_id=parcel_id, result=result))

    async def batch_change_parcels(
        self,
        parcels: list[dict[str, Any]],
    ) -> ParcelChangeResult:
        return await self(BatchChangeParcels(parcels=parcels))

    async def cancel_announcement(self, announcement_id: str) -> AnnouncementId:
        return await self(CancelAnnouncement(announcement_id=announcement_id))

    async def create_announcement(self, payload: dict[str, Any] | None = None) -> Announcement:
        return await self(CreateAnnouncement(payload=payload or {}))

    async def create_announcement_v1(self, payload: dict[str, Any] | None = None) -> Announcement:
        return await self(CreateAnnouncementV1(payload=payload or {}))

    async def track_announcement_v1(self, announcement_id: str) -> AnnouncementEvent:
        return await self(TrackAnnouncementV1(announcement_id=announcement_id))

    async def get_sorting_center(self, sorting_center_id: str) -> SortingCenter:
        return await self(GetSortingCenter(sorting_center_id=sorting_center_id))

    async def set_sorting_center_tariff(
        self,
        sorting_center_id: str,
        tariff_id: str,
    ) -> Tariff:
        return await self(
            SetSortingCenterTariff(sorting_center_id=sorting_center_id, tariff_id=tariff_id),
        )

    async def list_tariff_sorting_centers(
        self,
        tariff_id: str,
        *,
        filters: dict[str, Any] | None = None,
    ) -> SortingCenterList:
        return await self(
            ListTariffSortingCenters(tariff_id=tariff_id, filters=filters or {}),
        )

    async def cancel_announcement_v1(self, announcement_id: str) -> AnnouncementId:
        return await self(CancelAnnouncementV1(announcement_id=announcement_id))

    async def cancel_parcel_v1(
        self, parcel_id: str, *, reason: str | None = None
    ) -> ParcelChangeResult:
        return await self(CancelParcelV1(parcel_id=parcel_id, reason=reason))

    async def change_parcel_v1(
        self,
        parcel_id: str,
        changes: dict[str, Any],
    ) -> ParcelChangeResult:
        return await self(ChangeParcelV1(parcel_id=parcel_id, changes=changes))

    async def create_announcement_v1_alt(
        self,
        payload: dict[str, Any] | None = None,
    ) -> Announcement:
        return await self(CreateAnnouncementV1Alt(payload=payload or {}))

    async def get_announcement_event_v1(
        self,
        announcement_id: str,
        *,
        event_id: str | None = None,
    ) -> AnnouncementEvent:
        return await self(
            GetAnnouncementEventV1(announcement_id=announcement_id, event_id=event_id),
        )

    async def get_change_parcel_info_v1(self, parcel_id: str) -> ChangeParcelInfo:
        return await self(GetChangeParcelInfoV1(parcel_id=parcel_id))

    async def get_parcel_info_v1(self, parcel_id: str) -> ParcelInfo:
        return await self(GetParcelInfoV1(parcel_id=parcel_id))

    async def get_registered_parcel_id_v1(self, external_id: str) -> RegisteredParcelId:
        return await self(GetRegisteredParcelIdV1(external_id=external_id))

    async def create_parcel_v2(self, payload: dict[str, Any] | None = None) -> Parcel:
        return await self(CreateParcelV2(payload=payload or {}))

    async def set_order_markings(
        self,
        order_id: str,
        markings: list[OrderMarking],
    ) -> MarkingResult:
        return await self(SetOrderMarkings(order_id=order_id, markings=markings))

    async def accept_return_order(
        self,
        order_id: str,
        *,
        comment: str | None = None,
    ) -> CncDetailsResult:
        return await self(AcceptReturnOrder(order_id=order_id, comment=comment))

    async def apply_order_transition(
        self,
        order_id: str,
        transition: OrderTransition | str,
    ) -> CncDetailsResult:
        target = (
            transition if isinstance(transition, OrderTransition) else OrderTransition(transition)
        )
        return await self(ApplyOrderTransition(order_id=order_id, transition=target))

    async def check_order_confirmation_code(
        self,
        order_id: str,
        code: str,
    ) -> OrderConfirmationCheck:
        return await self(CheckOrderConfirmationCode(order_id=order_id, code=code))

    async def cnc_set_order_details(
        self,
        order_id: str,
        details: dict[str, Any],
    ) -> CncDetailsResult:
        return await self(CncSetOrderDetails(order_id=order_id, details=details))

    async def get_courier_delivery_range(self, order_id: str) -> CourierDeliveryRange:
        return await self(GetCourierDeliveryRange(order_id=order_id))

    async def set_courier_delivery_range(
        self,
        order_id: str,
        date_from: str,
        date_to: str,
        *,
        comment: str | None = None,
    ) -> CourierDeliveryRange:
        return await self(
            SetCourierDeliveryRange(
                order_id=order_id,
                date_from=date_from,
                date_to=date_to,
                comment=comment,
            ),
        )

    async def set_order_tracking_number(
        self,
        order_id: str,
        carrier: str,
        code: str,
    ) -> CncDetailsResult:
        return await self(
            SetOrderTrackingNumber(order_id=order_id, carrier=carrier, code=code),
        )

    async def list_managed_orders(
        self,
        *,
        page: int = 1,
        per_page: int = 25,
        status: str | None = None,
    ) -> ManagedOrderList:
        """List managed orders (one page)."""
        return await self(ListManagedOrders(page=page, per_page=per_page, status=status))

    async def create_order_labels(self, order_ids: list[str]) -> LabelTaskResult:
        return await self(CreateOrderLabels(order_ids=order_ids))

    async def create_order_labels_extended(
        self,
        order_ids: list[str],
        *,
        options: dict[str, Any] | None = None,
    ) -> LabelTaskResult:
        return await self(
            CreateOrderLabelsExtended(order_ids=order_ids, options=options or {}),
        )

    async def download_order_labels(self, taskID: str) -> bytes:  # noqa: N803 — Avito spelling
        """Download generated labels as raw bytes (PDF / ZIP)."""
        return await self(DownloadOrderLabels(taskID=taskID))

    async def set_autostrategy_budget(
        self,
        campaign_id: str,
        daily_budget: Money,
    ) -> BudgetUpdateResult:
        return await self(
            SetAutostrategyBudget(campaign_id=campaign_id, daily_budget=daily_budget),
        )

    async def create_autostrategy_campaign(
        self,
        name: str,
        daily_budget: Money,
        item_ids: list[int] | None = None,
        category_ids: list[int] | None = None,
        regions: list[str] | None = None,
    ) -> CampaignActionResult:
        return await self(
            CreateAutostrategyCampaign(
                name=name,
                daily_budget=daily_budget,
                item_ids=item_ids or [],
                category_ids=category_ids or [],
                regions=regions or [],
            ),
        )

    async def edit_autostrategy_campaign(
        self,
        campaign_id: str,
        name: str | None = None,
        daily_budget: Money | None = None,
    ) -> CampaignActionResult:
        return await self(
            EditAutostrategyCampaign(
                campaign_id=campaign_id,
                name=name,
                daily_budget=daily_budget,
            ),
        )

    async def get_autostrategy_campaign_info(self, campaign_id: str) -> CampaignInfo:
        return await self(GetAutostrategyCampaignInfo(campaign_id=campaign_id))

    async def stop_autostrategy_campaign(self, campaign_id: str) -> CampaignActionResult:
        return await self(StopAutostrategyCampaign(campaign_id=campaign_id))

    async def list_autostrategy_campaigns(
        self,
        page: int = 1,
        per_page: int = 25,
    ) -> CampaignList:
        """List autostrategy campaigns (paginated)."""
        return await self(ListAutostrategyCampaigns(page=page, per_page=per_page))

    async def get_autostrategy_stats(
        self,
        campaign_id: str,
        date_from: date,
        date_to: date,
    ) -> AutostrategyStatList:
        """Fetch per-day stats for one autostrategy campaign over an inclusive date window."""
        return await self(
            GetAutostrategyStats(
                campaign_id=campaign_id,
                date_from=date_from,
                date_to=date_to,
            ),
        )

    async def get_cpx_bids(self, item_id: int) -> CpxBidList:
        return await self(GetCpxBids(item_id=item_id))

    async def get_cpx_promotions_by_items(
        self,
        item_ids: list[int],
    ) -> CpxPromotionList:
        return await self(GetCpxPromotionsByItems(item_ids=item_ids))

    async def remove_cpx_promotion(self, item_ids: list[int]) -> CpxActionResult:
        return await self(RemoveCpxPromotion(item_ids=item_ids))

    async def set_cpx_auto_promotion(self, item_ids: list[int]) -> CpxActionResult:
        return await self(SetCpxAutoPromotion(item_ids=item_ids))

    async def set_cpx_manual_promotion(
        self,
        item_ids: list[int],
        bid: int,
    ) -> CpxActionResult:
        """Set a manual CpxPromo bid (in rubles) for the given items."""
        return await self(SetCpxManualPromotion(item_ids=item_ids, bid=bid))

    async def apply_trx_promo(
        self,
        promo_code: str,
        category_ids: list[int] | None = None,
    ) -> TrxApplyResult:
        return await self(
            ApplyTrxPromo(promo_code=promo_code, category_ids=category_ids or []),
        )

    async def cancel_trx_promo(self, promo_id: str) -> TrxCancelResult:
        return await self(CancelTrxPromo(promo_id=promo_id))

    async def get_trx_commissions(self) -> TrxCommissionList:
        return await self(GetTrxCommissions())

    def _user_id(self, override: int | None) -> int:
        if override is not None:
            return override
        if self.config.user_id is None:
            raise ValueError(
                "user_id not set: pass `user_id=...` or configure "
                "`ClientConfig.user_id` for the authorization_code grant",
            )
        return self.config.user_id

    def _build_oauth_cache_key(self, client: Any) -> str:
        return self._oauth.cache_key_for(user_id=client.config.user_id)

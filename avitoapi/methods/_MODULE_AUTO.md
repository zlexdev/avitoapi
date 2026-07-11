# methods/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

> Per-domain method-classes. See ``_MODULE.md``.

## _base.py
```
# ``BaseMethod[T]`` — aiogram-style typed endpoint declaration.


cls BaseMethod(BaseModel, Generic[T_co])
  as_(client: Client) -> Self
    # Attach a client and return ``self``. Idempotent; re-binding overwrites.
  async emit(client: Client) -> T_co
    # Execute through the session funnel and return the typed response.

```

## accounts_hierarchy.py
```
# Иерархия Аккаунтов — domain endpoints (auto-generated from the Avito OpenAPI spec).


cls CheckAhUserV1(BaseMethod[CheckAhUserV1Response])

cls CheckAhUserV2(BaseMethod[CheckAhUserV2Response])

cls GetAhInfoV1(BaseMethod[GetAhInfoV1Response])

cls GetEmployeesV1(BaseMethod[GetEmployeesResult])

cls LinkItemsV1(BaseMethod[None])

cls ListCompanyPhonesV1(BaseMethod[CompanyPhonesResult])

cls ListItemsByEmployeeIdV1(BaseMethod[ListItemsByEmployeeIdResult])

```

## ads.py
```
# Авито Реклама — domain endpoints (auto-generated from the Avito OpenAPI spec).


cls V1GetAccountById(BaseMethod[V1GetAccountByIdOut])

cls V1CreateAccount(BaseMethod[V1CreateAccountOut])

cls V1AddUser(BaseMethod[EmptyResponse])

cls V1GetAdvertisersList(BaseMethod[V1GetAdvertisersListOut])

cls V1GetAccountBalanceById(BaseMethod[V1GetAccountBalanceByIdOut])

cls V1TransferBonus(BaseMethod[EmptyResponse])

cls V1GetCampaignsList(BaseMethod[V1GetCampaignsListOut])

cls V1GetCreativesStatistic(BaseMethod[V1GetCreativesStatisticOut])

cls V1GetGroupsStatistic(BaseMethod[V1GetGroupsStatisticOut])

cls V1GetCampaignStatistic(BaseMethod[V1GetCampaignStatisticOut])

cls V1GetChildAccountsList(BaseMethod[V1GetChildAccountsListOut])

cls V1GetChildAccountsWithBalancesList(BaseMethod[V1GetChildAccountsWithBalancesListOut])

cls V1GetContractsList(BaseMethod[V1GetContractsListOut])

cls V1CreateAdvertiser(BaseMethod[IdResponse])

cls V1CreateContract(BaseMethod[IdResponse])

cls V1CreateNonPayerAccount(BaseMethod[V1CreateNonPayerAccountOut])

cls V1GetCreativesList(BaseMethod[V1GetCreativesListOut])

cls V1DeleteUser(BaseMethod[EmptyResponse])

cls V1TransferFunds(BaseMethod[EmptyResponse])

cls V1ChangeBudget(BaseMethod[EmptyResponse])

cls V1ChangePrice(BaseMethod[EmptyResponse])

cls V1GetGroupsList(BaseMethod[V1GetGroupsListOut])

cls V1SetUserRole(BaseMethod[EmptyResponse])

cls V1GetUsersListByAccount(BaseMethod[V1GetUsersListByAccountOut])

```

## auction.py
```
# CPA-аукцион — domain endpoints (auto-generated from the Avito OpenAPI spec).


cls GetUserBids(BaseMethod[GetUserBidsResponse])

cls SaveItemBids(BaseMethod[None])

```

## auth.py
```
# Авторизация — domain endpoints (auto-generated from the Avito OpenAPI spec).


cls GetAccessToken(BaseMethod[GetAccessTokenResponse])

cls GetAccessTokenAuthorizationCode(BaseMethod[GetAccessTokenAuthorizationCodeResponse])

cls RefreshAccessTokenAuthorizationCode(BaseMethod[RefreshAccessTokenAuthorizationCodeResponse])

```

## autoload.py
```
# Автозагрузка — domain endpoints (auto-generated from the Avito OpenAPI spec).


cls GetProfile(BaseMethod[GetProfileResponse])

cls CreateOrUpdateProfile(BaseMethod[None])

cls Upload(BaseMethod[None])

cls UserDocsNodeFields(BaseMethod[ApiFieldsOut])

cls UserDocsTree(BaseMethod[ApiCategoryTreeOut])

cls GetAdIdsByAvitoIds(BaseMethod[GetAdIdsByAvitoIdsResponse])

cls GetAvitoIdsByAdIds(BaseMethod[GetAvitoIdsByAdIdsResponse])

cls GetProfileV2(BaseMethod[GetProfileV2Response])

cls CreateOrUpdateProfileV2(BaseMethod[None])

cls GetReportsV2(BaseMethod[GetReportsV2Response])

cls GetAutoloadItemsInfoV2(BaseMethod[GetAutoloadItemsInfoV2Response])

cls GetLastCompletedReport(BaseMethod[ReportAutoloadV2])

cls GetReportByIdV2(BaseMethod[ReportAutoloadV2])

cls GetReportItemsById(BaseMethod[GetReportItemsByIdResponse])

cls GetReportItemsFeesById(BaseMethod[GetReportItemsFeesByIdResponse])

cls GetLastCompletedReportV3(BaseMethod[ReportAutoloadV3])

cls GetReportByIdV3(BaseMethod[ReportAutoloadV3])

cls GetUploads(BaseMethod[GetUploadsResponse])

cls GetCurrentUpload(BaseMethod[UploadAutoloadV4])

cls GetCurrentUploadItems(BaseMethod[GetCurrentUploadItemsResponse])

cls GetLastSuccessfulUpload(BaseMethod[UploadAutoloadV4])

cls GetLastSuccessfulUploadItems(BaseMethod[GetLastSuccessfulUploadItemsResponse])

```

## autostrategy.py
```
# Автостратегия — domain endpoints (auto-generated from the Avito OpenAPI spec).


cls GetAutostrategyBudget(BaseMethod[GetAutostrategyBudgetResponse])

cls CreateAutostrategyCampaign(BaseMethod[CreateAutostrategyCampaignResponse])

cls EditAutostrategyCampaign(BaseMethod[EditAutostrategyCampaignResponse])

cls GetAutostrategyCampaignInfo(BaseMethod[GetAutostrategyCampaignInfoResponse])

cls StopAutostrategyCampaign(BaseMethod[StopAutostrategyCampaignResponse])

cls GetAutostrategyCampaigns(BaseMethod[Campaigns])

cls GetAutostrategyStat(BaseMethod[GetAutostrategyStatResponse])

```

## autoteka.py
```
# Автотека — domain endpoints (auto-generated from the Avito OpenAPI spec).


cls CatalogsResolve(BaseMethod[CatalogsResolveResponseBodyAutoteka])

cls GetLeads(BaseMethod[ResponseGetLeads])

cls MonitoringBucketAdd(BaseMethod[ResponseMonitoringAddVinBucket])

cls MonitoringBucketDelete(BaseMethod[ResponseMonitoringDeleteVinBucket])

cls MonitoringBucketRemove(BaseMethod[ResponseMonitoringRemoveVinBucket])

cls MonitoringGetRegActions(BaseMethod[ResponseMonitoringGetRegActions])

cls GetActivePackage(BaseMethod[GetActivePackageResponseBodyAutoteka])

cls PostPreviewByVin(BaseMethod[RequestPreviewResponseBodyAutoteka])

cls GetPreview(BaseMethod[GetPreviewResponseBodyAutoteka])

cls PostReport(BaseMethod[CreateReportResponseBodyAutoteka])

cls PostReportByVehicleId(BaseMethod[CreateReportResponseBodyAutoteka])

cls GetReportList(BaseMethod[GetReportsListResponseDataAutoteka])

cls GetReport2(BaseMethod[GetReportAsync])

cls PostPreviewByExternalItem(BaseMethod[RequestPreviewResponseBodyAutoteka])

cls PostPreviewByItemId(BaseMethod[RequestPreviewResponseBodyAutoteka])

cls PostPreviewByRegNumber(BaseMethod[RequestPreviewResponseBodyAutoteka])

cls ScoringByVehicleId(BaseMethod[CreateScoringResponseBodyAutoteka])

cls ScoringGetById(BaseMethod[GetScoring])

cls SpecificationByPlateNumber(BaseMethod[CreateSpecificationResponseBodyAutoteka])

cls SpecificationByVehicleId(BaseMethod[CreateSpecificationResponseBodyAutoteka])

cls SpecificationGetById(BaseMethod[GetSpecificationResponseBodyAutoteka])

cls PostSyncCreateReportByRegNumber(BaseMethod[GetReport])

cls PostSyncCreateReportByVin(BaseMethod[GetReport])

cls PostTeaser(BaseMethod[CreateTeaserResponseBodyAutoteka])

cls GetTeaser(BaseMethod[TeaserResponse])

cls ValuationBySpecification(BaseMethod[ValuationBySpecificationResponseBodyAutoteka])

cls GetAccessToken(BaseMethod[GetAccessTokenResponse])

```

## avito_promo.py
```
# Авито Promo — domain endpoints (auto-generated from the Avito OpenAPI spec).


cls AgencyBalance(BaseMethod[AgencyBalanceResponse])

cls AgencyTransactions(BaseMethod[AgencyTransactionsResponse])

cls AgencyTransaction(BaseMethod[AgencyTransactionResponse])

cls AgencyClients(BaseMethod[AgencyClientsResponse])

cls AgencyClientsTargetCreate(BaseMethod[AgencyClientsTargetCreateResponse])

cls AgencyClientsTargetResult(BaseMethod[AgencyClientsTargetResultResponse])

cls AgencyFinancesBalance(BaseMethod[AgencyFinancesBalanceResponse])

cls AgencyFinancesTransactionsHistory(BaseMethod[AgencyFinancesTransactionsHistoryResponse])

cls AgencyUsersInviteSend(BaseMethod[AgencyUsersInviteSendResponse])

cls AgencyUsersInviteStatus(BaseMethod[AgencyUsersInviteStatusResponse])

cls AgencyUsersVerificationStatus(BaseMethod[AgencyUsersVerificationStatusResponse])

cls StatsAccountsItems(BaseMethod[StatsAccountsItemsResponse])

cls StatsAccountsSpendings(BaseMethod[StatsAccountsSpendingsResponse])

```

## calltracking.py
```
# CallTracking[КТ] — domain endpoints (auto-generated from the Avito OpenAPI spec).


cls GetCallById(BaseMethod[GetCallByIdResponse])

cls GetCalls(BaseMethod[GetCallsResponse])

cls GetRecordByCallId(BaseMethod[None])

```

## cpa.py
```
# CPA Авито — domain endpoints (auto-generated from the Avito OpenAPI spec).


cls GetCall(BaseMethod[None])

cls ChatByActionId(BaseMethod[ChatByActionIdResponse])

cls ChatsByTime(BaseMethod[ChatsByTimeResponse])

cls PostCreateComplaint(BaseMethod[PostCreateComplaintResponse])

cls CreateComplaintByActionId(BaseMethod[CreateComplaintByActionIdResponse])

cls PhonesInfoFromChats(BaseMethod[PhonesInfoFromChatsResponse])

cls BalanceInfoV2(BaseMethod[BalanceInfoV2Response])

cls GetCallByIdV2(BaseMethod[GetCallByIdV2Response])

cls GetCallsByTimeV2(BaseMethod[GetCallsByTimeV2Response])

cls ChatsByTime2(BaseMethod[ChatsByTime2Response])

cls BalanceInfoV3(BaseMethod[BalanceResponse])

```

## cpxpromo.py
```
# Настройка цены целевого действия — domain endpoints (auto-generated from the Avito OpenAPI spec).


cls GetBids(BaseMethod[GetBidsOut])

cls GetPromotionsByItemIds(BaseMethod[GetPromotionsByItemIdsOut])

cls RemovePromotion2(BaseMethod[MessageResponse])

cls SaveAutoBid(BaseMethod[None])

cls SaveManualBid(BaseMethod[None])

```

## delivery.py
```
# Доставка — domain endpoints (auto-generated from the Avito OpenAPI spec).


cls CancelAnnouncement3Pl(BaseMethod[AnnouncementsSuccessResponse])

cls CreateAnnouncement3Pl(BaseMethod[AnnouncementsSuccessResponse])

cls CreateParcel(BaseMethod[CreateParcelResponse])

cls CreateAnnouncement(BaseMethod[AnnouncementsSuccessResponse])

cls TrackAnnouncement(BaseMethod[AnnouncementsSuccessResponse])

cls CustomAreaSchedule(BaseMethod[AddTaskReply])

cls CancelParcel(BaseMethod[CancelParcelReply])

cls CheckConfirmationCode(BaseMethod[CheckConfirmationCodeReply])

cls SetOrderProperties(BaseMethod[DeliverySetOrderPropertiesReply])

cls SetOrderRealAddress(BaseMethod[DeliverySetOrderPropertiesReply])

cls Tracking(BaseMethod[DeliverySetStatusReply])

cls ProhibitOrderAcceptance(BaseMethod[ProhibitOrderAcceptanceReply])

cls GetSortingCenter(BaseMethod[SortingCenterGet])

cls AddSortingCenter(BaseMethod[AddTaskReply])

cls AddAreasSandbox(BaseMethod[AddTariffReply])

cls AddTagsToSortingCenter(BaseMethod[AddTaskReply])

cls AddTerminalsSandbox(BaseMethod[AddTerminalsReply])

cls UpdateTerms(BaseMethod[UpdateTermsReply])

cls AddTariffSandboxV2(BaseMethod[AddTaskReply])

cls GetTask(BaseMethod[GetTaskReply])

cls V1cancelAnnouncement(BaseMethod[SandboxCancelAnnouncementReply])

cls V1CancelParcel(BaseMethod[CancelSandboxParcelReply])

cls V1changeParcel(BaseMethod[ChangeParcelReply])

cls V1createAnnouncement(BaseMethod[SandboxCreateAnnouncementReply])

cls V1getAnnouncementEvent(BaseMethod[SandboxGetAnnouncementEventReply])

cls V1getChangeParcelInfo(BaseMethod[GetChangeParcelInfoReply])

cls V1getParcelInfo(BaseMethod[GetSandboxParcelInfoReply])

cls V1getRegisteredParcelId(BaseMethod[GetRegisteredParcelIdReply])

cls CreateSandboxParcelV22(BaseMethod[CreateParcelReply])

cls ChangeParcelResult(BaseMethod[ChangeParcelResultReply])

cls ChangeParcels(BaseMethod[ChangeParcelsResponse])

```

## items.py
```
# Объявления — domain endpoints (auto-generated from the Avito OpenAPI spec).


cls VasPrices(BaseMethod[None])

cls PostCallsStats(BaseMethod[CallsStatsResponse])

cls GetItemInfo(BaseMethod[ItemInfoAvito])

cls PutItemVas(BaseMethod[VasApplyAvito])

cls GetItemsInfo(PageMethod[ItemsInfoWithCategoryAvito])

cls UpdatePrice(BaseMethod[UpdatePriceResponse])

cls PutItemVasPackageV2(BaseMethod[VasAmountAvito])

cls ApplyVas(BaseMethod[ApplyVasResponse])

cls ItemStatsShallow(BaseMethod[StatisticsResponse])

cls ItemAnalytics(BaseMethod[AnalyticsResponse])

cls AccountSpendings(BaseMethod[SpendingsResponse])

```

## job.py
```
# Авито.Работа — domain endpoints (auto-generated from the Avito OpenAPI spec).


cls ApplicationsApplyActions(BaseMethod[GetApplicationsIdsResult])

cls ApplicationsGetByIds(BaseMethod[GetApplicationsByIdsResult])

cls ApplicationsGetIds(BaseMethod[GetApplicationsIdsResult])

cls ApplicationsGetStates(BaseMethod[ApplicationsGetStatesResult])

cls ApplicationsSetIsViewed(BaseMethod[SetApplicationsIsViewedResult])

cls ApplicationsWebhookDelete(BaseMethod[OkResponse])

cls ApplicationsWebhookGet(BaseMethod[WebhookSubscribeRequestBody])

cls ApplicationsWebhookPut(BaseMethod[WebhookSubscribeRequestBody])

cls ApplicationsWebhooksGet(BaseMethod[WebhooksSubscriptionResultList])

cls ResumesGet(BaseMethod[ResumesGetResponse])

cls ResumeGetContacts(BaseMethod[ResumeContacts])

cls VacancyCreate2(BaseMethod[VacancyCreateResult])

cls VacancyArchive2(BaseMethod[None])

cls VacancyUpdate2(BaseMethod[None])

cls VacancyProlongate2(BaseMethod[None])

cls ResumeGetItem(BaseMethod[Resume20])

cls SearchVacancy(BaseMethod[SearchVacancyResponse])

cls VacancyCreateV2(BaseMethod[None])

cls VacanciesGetByIds(BaseMethod[Vacancies20])

cls VacancyGetStatuses(BaseMethod[VacancyStatusesResult])

cls VacancyUpdateV2(BaseMethod[None])

cls VacancyGetItem(BaseMethod[Vacancy20])

cls VacancyAutoRenewal2(BaseMethod[None])

cls GetDicts(BaseMethod[None])

cls GetDictById(BaseMethod[None])

```

## messenger.py
```
# Мессенджер — domain endpoints (auto-generated from the Avito OpenAPI spec).


cls PostSendMessage(BaseMethod[PostSendMessageResponse])

cls PostSendImageMessage(BaseMethod[PostSendImageMessageResponse])

cls DeleteMessage(BaseMethod[DeleteMessageResponse])

cls ChatRead(BaseMethod[OkResponse])

cls GetVoiceFiles(BaseMethod[VoiceFiles])

cls UploadImages(BaseMethod[UploadImagesResponse])

cls GetSubscriptions(BaseMethod[GetSubscriptionsResponse])

cls PostWebhookUnsubscribe(BaseMethod[OkResponse])

cls PostBlacklistV2(BaseMethod[None])

cls GetChatsV2(BaseMethod[Chats])

cls GetChatByIdV2(BaseMethod[Chat])

cls GetMessagesV3(BaseMethod[Messages])

cls PostWebhookV3(BaseMethod[OkResponse])

```

## order_management.py
```
# Управление заказами — domain endpoints (auto-generated from the Avito OpenAPI spec).


cls Markings(BaseMethod[SetOrderMarkingResponse])

cls AcceptReturnOrder(BaseMethod[SuccessResponse])

cls ApplyTransition(BaseMethod[SuccessResponse])

cls CheckConfirmationCode(BaseMethod[OrderCheckConfirmationCodeResponse])

cls CncSetDetails(BaseMethod[OrderCncSetDetailsResponse])

cls GetCourierDeliveryRange(BaseMethod[GetDeliveryCourierConfirmationResponse])

cls SetCourierDeliveryRange(BaseMethod[SuccessResponse])

cls SetOrderTrackingNumber(BaseMethod[OrderSetTrackingNumberResponse])

cls GetOrders(BaseMethod[OrdersInfo])

cls GenerateLabels(BaseMethod[OrdersLabelsResponse])

cls GenerateLabelsExtended(BaseMethod[OrdersLabelsResponse])

cls DownloadLabel(BaseMethod[bytes])

```

## promotion.py
```
# Продвижение — domain endpoints (auto-generated from the Avito OpenAPI spec).


cls GetBbipForecastsByItemsV1(BaseMethod[GetBbipForecastByItemsV1Resp])

cls CreateBbipOrderForItemsV1(BaseMethod[OrderBbipForItemsV1Resp])

cls GetBbipSuggestsByItemsV1(BaseMethod[GetBbipSuggestsV1Resp])

cls GetDictOfServicesV1(BaseMethod[GetDictOfServicesV1Resp])

cls GetServicesByItemsV1(BaseMethod[GetServicesByItemsV1Resp])

cls ListOrdersByUserV1(BaseMethod[ListOrdersByUserV1Resp])

cls GetOrderStatusV1(BaseMethod[GetOrderStatusV1Resp])

```

## realty_reports.py
```
# Аналитика по недвижимости — domain endpoints (auto-generated from the Avito OpenAPI spec).


cls MarketPriceCorrespondenceV1(BaseMethod[MarketPriceCorrespondenceV1Response])

cls CreateReportForClassified(BaseMethod[CreateReportForClassifiedResponse])

```

## reviews.py
```
# Рейтинги и отзывы — domain endpoints (auto-generated from the Avito OpenAPI spec).


cls CreateReviewAnswerV1(BaseMethod[CreateAnswerResponse])

cls RemoveReviewAnswerV1(BaseMethod[RemoveAnswerResponse])

cls GetRatingsInfoV1(BaseMethod[GetRatingInfoResponse])

cls GetReviewsV1(BaseMethod[GetReviewsResponse])

```

## short_term_rental.py
```
# Краткосрочная аренда — domain endpoints (auto-generated from the Avito OpenAPI spec).


cls PutBookingsInfo(BaseMethod[PutBookingsInfoResponse])

cls GetRealtyBookings(BaseMethod[GetRealtyBookingsResponse])

cls PostRealtyPrices(BaseMethod[PostRealtyPricesResponse])

cls PutIntervals(BaseMethod[PutIntervalsResponse])

cls PostBaseParams(BaseMethod[None])

```

## special_offers.py
```
# Рассылка скидок и спецпредложений в мессенджере (beta-version) — domain endpoints (auto-generated from the Avito OpenAPI spec).


cls OpenApiAvailable(BaseMethod[OpenApiAvailableResponseBody])

cls OpenApiMultiConfirm(BaseMethod[OkResponse])

cls OpenApiMultiCreate(BaseMethod[OpenApiMultiCreateResponseBody])

cls OpenApiStats(BaseMethod[OpenApiStatsResponseBody])

cls OpenApiTariffInfo(BaseMethod[OpenApiTariffInfoResponseBody])

```

## stock_management.py
```
# Управление остатками — domain endpoints (auto-generated from the Avito OpenAPI spec).


```

## tariff.py
```
# Тарифы — domain endpoints (auto-generated from the Avito OpenAPI spec).


cls GetTariffInfo(BaseMethod[TariffInfo])

```

## trxpromo.py
```
# TrxPromo — domain endpoints (auto-generated from the Avito OpenAPI spec).


cls ApiTrxPromoOpenApiApply(BaseMethod[ApplyResponse])

cls ApiTrxPromoOpenApiCancel(BaseMethod[CancelResponse])

cls ApiTrxPromoOpenApiCommissions(BaseMethod[CommissionResponse])

```

## user.py
```
# Информация о пользователе — domain endpoints (auto-generated from the Avito OpenAPI spec).


cls PostOperationsHistory(BaseMethod[ResponseOperationsHistory])

cls GetUserInfoSelf(BaseMethod[UserInfoSelf])

cls GetUserBalance(BaseMethod[Balance])

```

# models/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

> Per-domain Pydantic response DTOs. See ``_MODULE.md``.

## __init__.py
```
# Per-domain Pydantic response DTOs. See ``_MODULE.md``.


```

## _base.py
```
# ``AvitoObject`` — Pydantic base for response DTOs carrying a client reference.

T = TypeVar('T')

cls _AvitoClientMixin
  as_(client: Client) -> Self

cls AvitoObject(_AvitoClientMixin, BaseModel)

cls AvitoRootObject(_AvitoClientMixin, RootModel[T], Generic[T])

_bind_recursive(value: object, client: Client) -> None

```

## _helpers.py
```
# Stable model helpers shared by generated DTOs — hand-written, never regenerated.


_resolve_user_id(client: Any) -> int
  # Resolve the account ``user_id`` from the bound client's config (``0`` if unbound).

```

## _shared.py
```
# Shared models — cross-domain DTOs collapsed by codegen dedup (auto-generated from the Avito OpenAPI spec).


cls AmountResponse(AvitoObject)
  # Информация о балансе аванса тарифа клиента

cls BalanceResponse(AvitoObject)

cls CampaignIdResponse(AvitoObject)

cls CampaignIdsResponse(AvitoObject)

cls CodeResponse(AvitoObject)

cls CountResponse(AvitoObject)

cls CreativeIdResponse(AvitoObject)

cls CreativeIdsResponse(AvitoObject)

cls DataResponse(AvitoObject)

cls EmployeeIdResponse(AvitoObject)

cls ErrorResponse(AvitoObject)
  # ErrorResponse — shared across domains.

cls GetAccessTokenResponse(AvitoObject)

cls GetTokenRequest(AvitoObject)
  # GetTokenRequest — shared across domains.

cls GibddValueResponse(AvitoObject)

cls GroupIdsResponse(AvitoObject)

cls IdResponse(AvitoObject)
  # IdResponse — shared across domains.

cls ItemIdsResponse(AvitoObject)

cls MessageResponse(AvitoObject)

cls NameResponse(AvitoObject)
  # NameResponse — shared across domains.

cls OkResponse(AvitoObject)
  # OkResponse — shared across domains.

cls PreviewIdResponse(AvitoObject)

cls SizesResponse(AvitoObject)

cls StatusResponse(AvitoObject)

cls SuccessResponse(AvitoObject)

cls TaskIdResponse(AvitoObject)
  # Идентификатор задачи проверки ИНН клиентов

cls ValidatingErrorError(AvitoObject)

```

## accounts_hierarchy.py
```
# Иерархия Аккаунтов — domain models (auto-generated from the Avito OpenAPI spec).


cls CompanyPhonesResult(AvitoObject)
  # CompanyPhonesResult response model.

cls CompanyPhonesResultResult(AvitoObject)

cls GetEmployeesResultRoot(AvitoObject)

cls LinkItems(AvitoObject)

cls ListItemsByEmployeeIdBody(AvitoObject)

cls ListItemsByEmployeeIdResult(AvitoObject)

cls OpenApiError(AvitoObject)
  # OpenApiError response model.

cls OpenApiErrorError(AvitoObject)

cls CheckAhUserV1Response(AvitoObject)

cls CheckAhUserV2Response(AvitoObject)

cls GetAhInfoV1Response(AvitoObject)
  # Данные пользователя о статусе в иерархии аккаунтов

cls GetAhInfoV1ResponseCompany(AvitoObject)

cls GetAhInfoV1ResponseEmployees(AvitoObject)

cls GetEmployeesResult(RootModel[list[GetEmployeesResultRoot]])
  # Root wrapper for a top-level ``list[GetEmployeesResultRoot]`` response.

```

## ads.py
```
# Авито Реклама — domain models (auto-generated from the Avito OpenAPI spec).


cls Account(AvitoObject)

cls AccountContact(AvitoObject)
  # Контактное лицо

cls AccountManager(AvitoObject)
  # MSD Менеджер

cls Advertiser(AvitoObject)
  # Advertiser response model.

cls AdvertiserFilter(AvitoObject)

cls Campaign(AvitoObject)

cls CampaignStatistic(AvitoObject)

cls CampaignsFilter(AvitoObject)

cls Contract(AvitoObject)
  # Contract response model.

cls ContractForChildAccount(AvitoObject)
  # ContractForChildAccount response model.

cls ContractsFilter(AvitoObject)

cls CreateGroupActivitySchedule(AvitoObject)
  # Кастомное расписание активности

cls Creative(AvitoObject)

cls CreativeStatistic(AvitoObject)

cls CreativesFilter(AvitoObject)

cls CreteIntermediaryIn(AvitoObject)

cls DateRange(AvitoObject)

cls DetailedError(AvitoObject)
  # DetailedError response model.

cls DetailedErrorItem(AvitoObject)

cls Disclaimer(AvitoObject)
  # Disclaimer response model.

cls DisclaimerInput(AvitoObject)
  # DisclaimerInput response model.

cls EmptyResponse(AvitoObject)
  # EmptyResponse response model.

cls EnumObject(AvitoObject)
  # EnumObject response model.

cls FrequencyRule(AvitoObject)

cls Group(AvitoObject)

cls GroupActivitySchedule(AvitoObject)
  # Расписание активности по дням

cls GroupReferenceData(AvitoObject)
  # GroupReferenceData response model.

cls GroupStatistic(AvitoObject)

cls GroupsFilter(AvitoObject)

cls IdNameObject(AvitoObject)
  # IdNameObject response model.

cls KktuItem(AvitoObject)
  # KktuItem response model.

cls LegalInfo(AvitoObject)

cls ObjectSize(AvitoObject)
  # ObjectSize response model.

cls ShortAccount(AvitoObject)
  # ShortAccount response model.

cls ShortAccountWithBalance(AvitoObject)
  # ShortAccountWithBalance response model.

cls ShortAccountWithContract(AvitoObject)
  # ShortAccountWithContract response model.

cls StatsData(AvitoObject)

cls StringIdNameObject(AvitoObject)
  # StringIdNameObject response model.

cls TemplateData(AvitoObject)
  # TemplateData response model.

cls TemplateField(AvitoObject)
  # TemplateField response model.

cls ThresholdItem(AvitoObject)

cls User(AvitoObject)

cls V1AddUserIn(AvitoObject)

cls V1ChangeBudgetIn(AvitoObject)

cls V1ChangePriceIn(AvitoObject)

cls V1CopyCampaignGroup(AvitoObject)

cls V1CopyCampaignIn(AvitoObject)

cls V1CopyCampaignOut(AvitoObject)

cls V1CopyGroupIn(AvitoObject)

cls V1CopyGroupOut(AvitoObject)

cls V1CreateAccountIn(AvitoObject)

cls V1CreateAccountInContact(AvitoObject)

cls V1CreateAccountOut(AvitoObject)

cls V1CreateAdvertiserIn(AvitoObject)

cls V1CreateCampaignIn(AvitoObject)

cls V1CreateContractIn(AvitoObject)

cls V1CreateGroupIn(AvitoObject)

cls V1CreateNonPayerAccountIn(AvitoObject)

cls V1CreateNonPayerAccountOut(AvitoObject)
  # V1CreateNonPayerAccountOut response model.

cls V1GetAccountBalanceByIdOut(AvitoObject)

cls V1GetAccountByIdOut(AvitoObject)
  # V1GetAccountByIdOut response model.

cls V1GetAdvertisersListIn(AvitoObject)

cls V1GetAdvertisersListOut(AvitoObject)
  # V1GetAdvertisersListOut response model.

cls V1GetCampaignByIdWithFieldsOut(AvitoObject)
  # V1GetCampaignByIdWithFieldsOut response model.

cls V1GetCampaignStatisticIn(AvitoObject)

cls V1GetCampaignStatisticOut(AvitoObject)

cls V1GetCampaignsListIn(AvitoObject)

cls V1GetCampaignsListOut(AvitoObject)
  # V1GetCampaignsListOut response model.

cls V1GetChildAccountsListOut(AvitoObject)
  # V1GetChildAccountsListOut response model.

cls V1GetChildAccountsWithBalancesListOut(AvitoObject)
  # V1GetChildAccountsWithBalancesListOut response model.

cls V1GetContractsListIn(AvitoObject)

cls V1GetContractsListOut(AvitoObject)
  # V1GetContractsListOut response model.

cls V1GetCreativesListIn(AvitoObject)

cls V1GetCreativesListOut(AvitoObject)
  # V1GetCreativesListOut response model.

cls V1GetCreativesStatisticIn(AvitoObject)

cls V1GetCreativesStatisticOut(AvitoObject)

cls V1GetGroupReferenceDataOut(AvitoObject)
  # V1GetGroupReferenceDataOut response model.

cls V1GetGroupsListIn(AvitoObject)

cls V1GetGroupsListOut(AvitoObject)
  # V1GetGroupsListOut response model.

cls V1GetGroupsStatisticIn(AvitoObject)

cls V1GetGroupsStatisticOut(AvitoObject)

cls V1GetHtmlOut(AvitoObject)

cls V1GetImageOut(AvitoObject)

cls V1GetLegalAttachmentsOut(AvitoObject)

cls V1GetUsersListByAccountOut(AvitoObject)
  # V1GetUsersListByAccountOut response model.

cls V1GetVideoOut(AvitoObject)

cls V1LaunchGroupIn(AvitoObject)

cls V1ReferenceDataCreateCreativeOut(AvitoObject)
  # V1ReferenceDataCreateCreativeOut response model.

cls V1SetUserRoleIn(AvitoObject)

cls V1TransferBonusIn(AvitoObject)

cls V1TransferFundsIn(AvitoObject)

cls V1UploadHtmlOut(AvitoObject)

cls V1UploadImageOut(AvitoObject)

cls V1UploadLegalAttachmentsOut(AvitoObject)

cls V1UploadVideoOut(AvitoObject)

cls V1CreateAccountContact(AvitoObject)

cls ActivityScheduleDay(RootModel[list[int]])
  # Root wrapper for a top-level ``list[int]`` response.

cls ActivityScheduleHours(RootModel[list[int]])
  # Root wrapper for a top-level ``list[int]`` response.

cls DetailedErrors(RootModel[list[DetailedErrorItem]])
  # Root wrapper for a top-level ``list[DetailedErrorItem]`` response.

cls FrequencyCount(RootModel[int])
  # Root wrapper for a top-level ``int`` response.

```

## auction.py
```
# CPA-аукцион — domain models (auto-generated from the Avito OpenAPI spec).


cls TooManyRequestsError(AvitoObject)
  # TooManyRequestsError response model.

cls GetUserBidsResponse(AvitoObject)
  # GetUserBidsResponse response model.

cls GetUserBidsResponseItems(AvitoObject)

cls GetUserBidsResponseItemsAvailablePrices(AvitoObject)

cls SaveItemBidsItems(AvitoObject)

```

## auth.py
```
# Авторизация — domain models (auto-generated from the Avito OpenAPI spec).


cls GetTokenOAuthRequest(AvitoObject)
  # GetTokenOAuthRequest response model.

cls RefreshRequest(AvitoObject)

cls GetAccessTokenAuthorizationCodeResponse(AvitoObject)

cls RefreshAccessTokenAuthorizationCodeResponse(AvitoObject)

```

## autoload.py
```
# Автозагрузка — domain models (auto-generated from the Avito OpenAPI spec).


cls ApFieldsNodeAlert(AvitoObject)

cls ApiCategoryNode(AvitoObject)

cls ApiCategoryTreeOut(AvitoObject)
  # ApiCategoryTreeOut response model.

cls ApiDependency(AvitoObject)

cls ApiDependencyPair(AvitoObject)
  # ApiDependencyPair response model.

cls ApiField(AvitoObject)

cls ApiFieldContent(AvitoObject)

cls ApiFieldsNode(AvitoObject)

cls ApiFieldsOut(AvitoObject)

cls CategoryNode(AvitoObject)

cls CategoryTreeOut(AvitoObject)
  # CategoryTreeOut response model.

cls ChildApiField(AvitoObject)

cls ErrorAutoload(AvitoObject)
  # ErrorAutoload response model.

cls ErrorAutoloadError(AvitoObject)

cls ExportScheduleRoot(AvitoObject)

cls FeedsDataRoot(AvitoObject)

cls FieldValue(AvitoObject)

cls FieldValueRange(AvitoObject)
  # Промежуток допустимых значений. Применимо для типов данных int и float. Для типа данных string является ограничением длины строки.

cls FieldWarning(AvitoObject)

cls ItemFeesInfoReportAutoloadV2(AvitoObject)

cls ItemInfoAutoload(AvitoObject)

cls ItemInfoAutoloadFeeInfo(AvitoObject)

cls ItemInfoAutoloadV2(AvitoObject)

cls ItemInfoAutoloadV2FeeInfo(AvitoObject)

cls ItemInfoAutoloadV2Section(AvitoObject)

cls ItemInfoError(AvitoObject)

cls ItemInfoErrorAutoload(AvitoObject)

cls ItemInfoReportAutoloadV2(AvitoObject)

cls ItemInfoReportAutoloadV2Section(AvitoObject)

cls ItemInfoVas(AvitoObject)

cls ItemMessageV4(AvitoObject)

cls ItemSectionV4(AvitoObject)

cls MetaAutoload(AvitoObject)

cls MetaReportItemsAutoloadV2(AvitoObject)

cls MetaReportsAutoloadV2(AvitoObject)

cls PaginationMetaV4(AvitoObject)

cls ReportAutoload(AvitoObject)

cls ReportAutoloadAds(AvitoObject)

cls ReportAutoloadAdsMessages(AvitoObject)

cls ReportAutoloadAdsStatuses(AvitoObject)

cls ReportAutoloadAdsStatusesAvito(AvitoObject)
  # Статус размещения на сайте

cls ReportAutoloadAdsStatusesGeneral(AvitoObject)
  # Общий статус обработки объявления

cls ReportAutoloadAdsStatusesProcessing(AvitoObject)
  # Статус предварительной обработки

cls ReportAutoloadListingFee(AvitoObject)

cls ReportAutoloadVas(AvitoObject)

cls ReportAutoloadV2(AvitoObject)
  get_report_by_id_v2() -> GetReportByIdV2
    # Build an awaitable :class:`GetReportByIdV2` bound to this object (await to execute).
  get_report_items_by_id(per_page: int = 50, page: int = 0, query: str? = None, sections: str? = None) -> GetReportItemsById
    # Build an awaitable :class:`GetReportItemsById` bound to this object (await to execute).
  get_report_items_fees_by_id(per_page: int = 100, page: int = 0, ad_ids: str? = None, avito_ids: str? = None) -> GetReportItemsFeesById
    # Build an awaitable :class:`GetReportItemsFeesById` bound to this object (await to execute).
  get_report_by_id_v3() -> GetReportByIdV3
    # Build an awaitable :class:`GetReportByIdV3` bound to this object (await to execute).

cls ReportAutoloadV2Events(AvitoObject)

cls ReportAutoloadV2ListingFees(AvitoObject)

cls ReportAutoloadV2ListingFeesPackages(AvitoObject)

cls ReportAutoloadV2ListingFeesSingle(AvitoObject)

cls ReportAutoloadV2SectionStats(AvitoObject)

cls ReportAutoloadV2SectionStatsSections(AvitoObject)

cls ReportAutoloadV2SectionStatsSectionsSections(AvitoObject)

cls ReportAutoloadV3(AvitoObject)

cls ReportAutoloadV3Events(AvitoObject)

cls ReportAutoloadV3FeedsUrls(AvitoObject)

cls ReportAutoloadV3ListingFees(AvitoObject)

cls ReportAutoloadV3ListingFeesPackages(AvitoObject)

cls ReportAutoloadV3ListingFeesSingle(AvitoObject)

cls ReportAutoloadV3SectionStats(AvitoObject)

cls ReportAutoloadV3SectionStatsSections(AvitoObject)

cls ReportAutoloadV3SectionStatsSectionsSections(AvitoObject)

cls ReportCollectionAutoloadRoot(AvitoObject)

cls ReportCollectionAutoloadRootStat(AvitoObject)

cls ReportShortAutoloadV2Root(AvitoObject)

cls SectionStatsV4(AvitoObject)

cls SectionStatsV4Sections(AvitoObject)

cls SectionStatsV4SectionsSections(AvitoObject)

cls UploadAutoloadV4(AvitoObject)

cls UploadAutoloadV4FeedUrls(AvitoObject)

cls UploadEventV4(AvitoObject)

cls UploadItemAutoloadV4(AvitoObject)

cls UpsertProfileIn(AvitoObject)

cls ExportScheduleValue(AvitoObject)

cls UpsertProfileInV2(AvitoObject)

cls FeedsDataValue(AvitoObject)

cls GetProfileResponse(AvitoObject)

cls GetAdIdsByAvitoIdsResponse(AvitoObject)

cls GetAdIdsByAvitoIdsResponseItems(AvitoObject)

cls GetAvitoIdsByAdIdsResponse(AvitoObject)

cls GetAvitoIdsByAdIdsResponseItems(AvitoObject)

cls GetProfileV2Response(AvitoObject)

cls GetReportsV2Response(AvitoObject)
  # GetReportsV2Response response model.

cls ReportShortAutoloadV2Value(AvitoObject)

cls GetAutoloadItemsInfoV2Response(AvitoObject)

cls GetReportItemsByIdResponse(AvitoObject)

cls GetReportItemsFeesByIdResponse(AvitoObject)

cls GetReportItemsFeesByIdResponseMeta(AvitoObject)

cls GetUploadsResponse(AvitoObject)

cls GetCurrentUploadItemsResponse(AvitoObject)

cls GetLastSuccessfulUploadItemsResponse(AvitoObject)

cls ExportSchedule(RootModel[list[ExportScheduleRoot]])
  # Root wrapper for a top-level ``list[ExportScheduleRoot]`` response.

cls FeedsData(RootModel[list[FeedsDataRoot]])
  # Root wrapper for a top-level ``list[FeedsDataRoot]`` response.

cls ReportCollectionAutoload(RootModel[list[ReportCollectionAutoloadRoot]])
  # Root wrapper for a top-level ``list[ReportCollectionAutoloadRoot]`` response.

cls ReportShortAutoloadV2(RootModel[list[ReportShortAutoloadV2Root]])
  # Root wrapper for a top-level ``list[ReportShortAutoloadV2Root]`` response.

```

## autostrategy.py
```
# Автостратегия — domain models (auto-generated from the Avito OpenAPI spec).


cls Budget(AvitoObject)

cls BudgetMaximal(AvitoObject)

cls BudgetMinimal(AvitoObject)

cls BudgetPriceRanges(AvitoObject)

cls BudgetRecommended(AvitoObject)

cls Campaign(AvitoObject)

cls Campaigns(AvitoObject)

cls CreateCampaignBadRequestError(AvitoObject)
  # CreateCampaignBadRequestError response model.

cls CreateCampaignBadRequestErrorError(AvitoObject)

cls CreateCampaignBadRequestErrorErrorFieldErrors(AvitoObject)

cls CreateCampaignRequestBody(AvitoObject)

cls EditCampaignBadRequestError(AvitoObject)
  # EditCampaignBadRequestError response model.

cls EditCampaignBadRequestErrorError(AvitoObject)

cls EditCampaignBadRequestErrorErrorFieldErrors(AvitoObject)

cls EditCampaignRequestBody(AvitoObject)

cls GetBudgetBadRequestError(AvitoObject)
  # GetBudgetBadRequestError response model.

cls GetBudgetBadRequestErrorError(AvitoObject)

cls GetBudgetBadRequestErrorErrorFieldErrors(AvitoObject)

cls GetBudgetRequestBody(AvitoObject)

cls GetCampaignInfoBadRequestError(AvitoObject)
  # GetCampaignInfoBadRequestError response model.

cls GetCampaignInfoBadRequestErrorError(AvitoObject)

cls GetCampaignInfoForecastResult(AvitoObject)

cls GetCampaignInfoForecastResultCalls(AvitoObject)

cls GetCampaignInfoForecastResultViews(AvitoObject)

cls GetCampaignInfoRequestBody(AvitoObject)

cls GetCampaignsBadRequestError(AvitoObject)
  # GetCampaignsBadRequestError response model.

cls GetCampaignsBadRequestErrorError(AvitoObject)

cls GetCampaignsBadRequestErrorErrorFieldErrors(AvitoObject)

cls GetCampaignsBadRequestErrorErrorFieldErrorsOrderBy(AvitoObject)

cls GetCampaignsRequestBody(AvitoObject)

cls GetCampaignsRequestBodyFilter(AvitoObject)

cls GetCampaignsRequestBodyFilterByUpdateTime(AvitoObject)

cls GetCampaignsRequestBodyOrderBy(AvitoObject)

cls GetStatRequestBody(AvitoObject)

cls GetStatRequestError(AvitoObject)
  # GetStatRequestError response model.

cls GetStatRequestErrorError(AvitoObject)

cls StatRoot(AvitoObject)

cls StatRootCallsForecast(AvitoObject)

cls StatRootViewsForecast(AvitoObject)

cls StopCampaignBadRequestError(AvitoObject)
  # StopCampaignBadRequestError response model.

cls StopCampaignBadRequestErrorError(AvitoObject)

cls StopCampaignBadRequestErrorErrorFieldErrors(AvitoObject)

cls StopCampaignRequestBody(AvitoObject)

cls AutostrategyAuthError(AvitoObject)
  # AutostrategyAuthError response model.

cls AutostrategyServiceError(AvitoObject)
  # AutostrategyServiceError response model.

cls GetAutostrategyBudgetResponse(AvitoObject)

cls CreateAutostrategyCampaignResponse(AvitoObject)
  # CreateAutostrategyCampaignResponse response model.

cls EditAutostrategyCampaignResponse(AvitoObject)
  # EditAutostrategyCampaignResponse response model.

cls GetAutostrategyCampaignInfoResponse(AvitoObject)

cls GetAutostrategyCampaignInfoResponseItems(AvitoObject)

cls StopAutostrategyCampaignResponse(AvitoObject)
  # StopAutostrategyCampaignResponse response model.

cls GetAutostrategyCampaignsFilter(AvitoObject)

cls GetAutostrategyCampaignsFilterByUpdateTime(AvitoObject)

cls GetAutostrategyCampaignsOrderBy(AvitoObject)

cls GetAutostrategyStatResponse(AvitoObject)

cls StatValue(AvitoObject)

cls StatValueCallsForecast(AvitoObject)

cls StatValueViewsForecast(AvitoObject)

cls GetAutostrategyStatResponseTotals(AvitoObject)

cls Stat(RootModel[list[StatRoot]])
  # Root wrapper for a top-level ``list[StatRoot]`` response.

```

## autoteka.py
```
# Автотека — domain models (auto-generated from the Avito OpenAPI spec).


cls ArbitrationCases(AvitoObject)
  # Арбитражные дела

cls ArbitrationCasesCases(AvitoObject)

cls AutotekaTeaser(AvitoObject)

cls AvitoAuctions(AvitoObject)

cls AvitoAuctionsAuctions(AvitoObject)

cls AvitoItemAutoteka(AvitoObject)

cls AvitoItemAutotekaImages(AvitoObject)

cls AvitoPriceValuation(AvitoObject)

cls AvitoPriceValuationMarketNormalPriceRange(AvitoObject)

cls CarImageAutoteka(AvitoObject)

cls CarsharingDataAutoteka(AvitoObject)

cls CarsharingDataEventAutoteka(AvitoObject)

cls CatalogsFieldAutoteka(AvitoObject)

cls CatalogsFieldAutotekaValues(AvitoObject)

cls CatalogsResolveResponseBodyAutoteka(AvitoObject)
  # CatalogsResolveResponseBodyAutoteka response model.

cls CatalogsResolveResponseDataAutoteka(AvitoObject)
  # CatalogsResolveResponseDataAutoteka response model.

cls CrashesHistoryAutoteka(AvitoObject)

cls CrashesHistoryAutotekaDamageTypes(AvitoObject)

cls CreateEptsResponseDataAutoteka(AvitoObject)
  # CreateEptsResponseDataAutoteka response model.

cls CreateReportResponseBodyAutoteka(AvitoObject)
  # CreateReportResponseBodyAutoteka response model.

cls CreateReportResponseDataAutoteka(AvitoObject)
  # CreateReportResponseDataAutoteka response model.

cls CreateScoringResponseBodyAutoteka(AvitoObject)
  # CreateScoringResponseBodyAutoteka response model.

cls CreateScoringResponseDataAutoteka(AvitoObject)
  # CreateScoringResponseDataAutoteka response model.

cls CreateSpecificationResponseBodyAutoteka(AvitoObject)
  # CreateSpecificationResponseBodyAutoteka response model.

cls CreateSpecificationResponseDataAutoteka(AvitoObject)
  # CreateSpecificationResponseDataAutoteka response model.

cls CreateTeaserResponseBodyAutoteka(AvitoObject)
  # CreateTeaserResponseBodyAutoteka response model.

cls CreateTeaserResponseDataAutoteka(AvitoObject)
  # CreateTeaserResponseDataAutoteka response model.

cls Customs(AvitoObject)

cls Diagnostics(AvitoObject)

cls DiagnosticsEvent(AvitoObject)

cls DiagnosticsEventCondition(AvitoObject)

cls DiagnosticsEventDamage(AvitoObject)

cls DiagnosticsEventPhoto(AvitoObject)

cls DocumentsResultAutoteka(AvitoObject)

cls DocumentsResultAutotekaPts(AvitoObject)

cls DocumentsResultAutotekaSts(AvitoObject)

cls Epts(AvitoObject)

cls EptsAutoteka(AvitoObject)

cls EptsDataAutoteka(AvitoObject)

cls EptsRequestIdResultAutoteka(AvitoObject)

cls EquipmentAutoteka(AvitoObject)

cls EquipmentAutotekaBody(AvitoObject)

cls EquipmentAutotekaBodyNumber(AvitoObject)

cls EquipmentAutotekaBrand(AvitoObject)

cls EquipmentAutotekaChasisNumber(AvitoObject)

cls EquipmentAutotekaColor(AvitoObject)

cls EquipmentAutotekaDrive(AvitoObject)

cls EquipmentAutotekaEngineNumber(AvitoObject)

cls EquipmentAutotekaEngineType(AvitoObject)

cls EquipmentAutotekaEquipment(AvitoObject)

cls EquipmentAutotekaHorsepower(AvitoObject)

cls EquipmentAutotekaMaxWeight(AvitoObject)

cls EquipmentAutotekaModel(AvitoObject)

cls EquipmentAutotekaModification(AvitoObject)

cls EquipmentAutotekaNetWeight(AvitoObject)

cls EquipmentAutotekaTransmission(AvitoObject)

cls EquipmentAutotekaVehicle(AvitoObject)

cls EquipmentAutotekaVehicleCategory(AvitoObject)

cls EquipmentAutotekaVehicleType(AvitoObject)

cls EquipmentAutotekaVolume(AvitoObject)

cls EquipmentAutotekaYear(AvitoObject)

cls EventsAutoteka(AvitoObject)

cls EventsAutotekaAvitoOnSale(AvitoObject)

cls EventsAutotekaAvitoOnSaleAdditionalInfo(AvitoObject)

cls EventsAutotekaBodyRepair(AvitoObject)

cls EventsAutotekaCrashes(AvitoObject)

cls EventsAutotekaDealerDataAvailable(AvitoObject)

cls EventsAutotekaFirstSellDate(AvitoObject)

cls EventsAutotekaLastMileageRecord(AvitoObject)

cls EventsAutotekaOwners(AvitoObject)

cls EventsAutotekaPledge(AvitoObject)

cls EventsAutotekaPublicPerson(AvitoObject)

cls EventsOthersHistoryAutoteka(AvitoObject)

cls ExtendedSpecifications(AvitoObject)

cls ExtendedSpecificationsParam(AvitoObject)

cls ExternalPlacementAutoteka(AvitoObject)

cls FineEventAutoteka(AvitoObject)

cls FinesAutoteka(AvitoObject)

cls GetActivePackageResponseBodyAutoteka(AvitoObject)
  # GetActivePackageResponseBodyAutoteka response model.

cls GetActivePackageResponseDataAutoteka(AvitoObject)
  # GetActivePackageResponseDataAutoteka response model.

cls GetEptsResult(AvitoObject)
  # GetEptsResult response model.

cls GetPreviewResponseBodyAutoteka(AvitoObject)
  # GetPreviewResponseBodyAutoteka response model.

cls GetPreviewResponseDataAutoteka(AvitoObject)
  # GetPreviewResponseDataAutoteka response model.

cls GetReport(AvitoObject)
  # GetReport response model.

cls GetReportAsync(AvitoObject)
  # GetReportAsync response model.

cls GetReportResult(AvitoObject)
  # GetReportResult response model.

cls GetReportResultAsync(AvitoObject)
  # GetReportResultAsync response model.

cls GetReportsListResponseDataAutoteka(AvitoObject)
  # GetReportsListResponseDataAutoteka response model.

cls GetScoring(AvitoObject)
  # GetScoring response model.

cls GetScoringResult(AvitoObject)
  # GetScoringResult response model.

cls GetSpecificationResponseBodyAutoteka(AvitoObject)
  # GetSpecificationResponseBodyAutoteka response model.

cls GetSpecificationResponseDataAutoteka(AvitoObject)

cls HeadAutoteka(AvitoObject)

cls HeadAutotekaRegNumbersHistory(AvitoObject)

cls Insights(AvitoObject)

cls InsurancePaymentsItem(AvitoObject)

cls InsurancePoliciesAutoteka(AvitoObject)

cls InsurancePolicyEventAutoteka(AvitoObject)

cls Leasing(AvitoObject)

cls LeasingContracts(AvitoObject)

cls MaxPosterPriceValuation(AvitoObject)

cls MaxPosterPriceValuationAnalyticByActualSales(AvitoObject)

cls MaxPosterPriceValuationAnalyticByCompletedSales(AvitoObject)

cls MaxPosterPriceValuationLiquidity(AvitoObject)

cls MaxPosterValuationLiquidityRating(AvitoObject)

cls NewCarValuation(AvitoObject)

cls OtherAutoteka(AvitoObject)

cls OwnersHistoryAutoteka(AvitoObject)

cls PackageAutoteka(AvitoObject)

cls PreviewAutoteka(AvitoObject)

cls PreviewDataAutoteka(AvitoObject)

cls PriceStatAutoteka(AvitoObject)

cls PriceStatForNewCarsAutoteka(AvitoObject)

cls PriceStatForNewCarsAutotekaItems(AvitoObject)
  # PriceStatForNewCarsAutotekaItems response model.

cls PriceStatForNewCarsAutotekaItemsPrices(AvitoObject)
  # PriceStatForNewCarsAutotekaItemsPrices response model.

cls PriceStatForNewCarsAutotekaPrice(AvitoObject)

cls PriceStatReportAutoteka(AvitoObject)

cls PriceStatReportAutotekaPrice(AvitoObject)

cls PtsData(AvitoObject)

cls PtsDataPts(AvitoObject)

cls PtsDataSts(AvitoObject)

cls RecallItem(AvitoObject)

cls RecallItemCompleteInfo(AvitoObject)

cls RecapAutoteka(AvitoObject)
  # RecapAutoteka response model.

cls ReportDataAutoteka(AvitoObject)

cls ReportDataAutotekaAccidents(AvitoObject)

cls ReportDataAutotekaRegistrationActions(AvitoObject)

cls SalvageCarAuctionRecordsValue(AvitoObject)

cls ReportItemAutoteka(AvitoObject)

cls ReportWithoutDataAutoteka(AvitoObject)

cls ReportAutoteka(AvitoObject)

cls ReportAutotekaAsync(AvitoObject)

cls RequestByRegNumberAutoteka(AvitoObject)

cls RequestByVinAutoteka(AvitoObject)

cls RequestCatalogsResolve(AvitoObject)

cls RequestCatalogsResolveFieldsValueIds(AvitoObject)

cls RequestGetLeads(AvitoObject)

cls RequestGetLeadsFeed(AvitoObject)

cls RequestPreviewByItemIdAutoteka(AvitoObject)

cls RequestPreviewResponseBodyAutoteka(AvitoObject)
  # RequestPreviewResponseBodyAutoteka response model.

cls RequestPreviewResponseDataAutoteka(AvitoObject)
  # RequestPreviewResponseDataAutoteka response model.

cls RequestReportByPlateNumberAutoteka(AvitoObject)

cls RequestReportByVehicleIdAutoteka(AvitoObject)

cls RequestTeaserByVehicleIdAutoteka(AvitoObject)

cls RequestValuationBySpecificationResolve(AvitoObject)

cls RequestValuationBySpecificationResolveLocation(AvitoObject)
  # RequestValuationBySpecificationResolveLocation response model.

cls RequestValuationBySpecificationResolveSpecification(AvitoObject)

cls RequestValuationBySpecificationResolveSpecificationBodyType(AvitoObject)

cls RequestValuationBySpecificationResolveSpecificationBrand(AvitoObject)

cls RequestValuationBySpecificationResolveSpecificationColor(AvitoObject)

cls RequestValuationBySpecificationResolveSpecificationComplectation(AvitoObject)

cls RequestValuationBySpecificationResolveSpecificationDoorsCount(AvitoObject)

cls RequestValuationBySpecificationResolveSpecificationGeneration(AvitoObject)

cls RequestValuationBySpecificationResolveSpecificationModel(AvitoObject)

cls RequestValuationBySpecificationResolveSpecificationModification(AvitoObject)

cls RequestValuationBySpecificationResolveSpecificationOwnersCount(AvitoObject)

cls RequestValuationBySpecificationResolveSpecificationYear(AvitoObject)

cls ResponseGetLeads(AvitoObject)
  # ResponseGetLeads response model.

cls ResponseGetLeadsPagination(AvitoObject)
  # ResponseGetLeadsPagination response model.

cls ResponseGetLeadsResult(AvitoObject)
  # ResponseGetLeadsResult response model.

cls ResponseGetLeadsResultPayload(AvitoObject)
  # ResponseGetLeadsResultPayload response model.

cls ResponseGetLeadsResultPayloadExtraPayload(AvitoObject)
  # ResponseGetLeadsResultPayloadExtraPayload response model.

cls ResponseGetLeadsResultPayloadExtraPayloadPriceAnalytics(AvitoObject)
  # ResponseGetLeadsResultPayloadExtraPayloadPriceAnalytics response model.

cls ResponseGetLeadsResultPayloadExtraPayloadTeaser(AvitoObject)
  # ResponseGetLeadsResultPayloadExtraPayloadTeaser response model.

cls ResponseGetLeadsResultPayloadTriggerPayload(AvitoObject)
  # ResponseGetLeadsResultPayloadTriggerPayload response model.

cls ResponseGetLeadsResultPayloadTriggerPayloadLastEvents(AvitoObject)
  # ResponseGetLeadsResultPayloadTriggerPayloadLastEvents response model.

cls ResponseMonitoringAddVinBucket(AvitoObject)
  # ResponseMonitoringAddVinBucket response model.

cls ResponseMonitoringAddVinBucketResult(AvitoObject)

cls ResponseMonitoringAddVinBucketResultInvalidVehicles(AvitoObject)

cls ResponseMonitoringDeleteVinBucket(AvitoObject)
  # ResponseMonitoringDeleteVinBucket response model.

cls ResponseMonitoringDeleteVinBucketResult(AvitoObject)
  # ResponseMonitoringDeleteVinBucketResult response model.

cls ResponseMonitoringGetRegAction(AvitoObject)

cls ResponseMonitoringGetRegActions(AvitoObject)

cls ResponseMonitoringGetRegActionsPagination(AvitoObject)

cls ResponseMonitoringRemoveVinBucket(AvitoObject)
  # ResponseMonitoringRemoveVinBucket response model.

cls ResponseMonitoringRemoveVinBucketResult(AvitoObject)

cls ResponseMonitoringRemoveVinBucketResultInvalidVehicles(AvitoObject)

cls RestrictionsAutoteka(AvitoObject)

cls RestrictionsAutotekaPledge(AvitoObject)

cls RestrictionsAutotekaPledgeHistory(AvitoObject)
  # История залогов, подключается в отчёт по дополнительному согласованию

cls RestrictionsAutotekaPledgeHistoryPledges(AvitoObject)

cls RestrictionsAutotekaPledgePledgeAdditionalData(AvitoObject)

cls RestrictionsAutotekaPledgePledgeAdditionalDataData(AvitoObject)

cls RestrictionsAutotekaRegistration(AvitoObject)

cls RestrictionsAutotekaRegistrationAdditionalInfo(AvitoObject)

cls RestrictionsAutotekaStealing(AvitoObject)

cls RestrictionsAutotekaStealingAdditionalInfo(AvitoObject)
  # RestrictionsAutotekaStealingAdditionalInfo response model.

cls SalvageCarAuctionRecordsRoot(AvitoObject)

cls ScoringAccidents(AvitoObject)

cls ScoringAutoteka(AvitoObject)

cls ScoringDataAutoteka(AvitoObject)

cls ScoringDataAutotekaCarsharing(AvitoObject)

cls ScoringDataAutotekaEpts(AvitoObject)

cls ScoringDataAutotekaImport(AvitoObject)

cls ScoringDataAutotekaLeasing(AvitoObject)

cls ScoringDataAutotekaPledges(AvitoObject)

cls ScoringDataAutotekaPriceEvaluation(AvitoObject)

cls ScoringDataAutotekaRegistrations(AvitoObject)

cls ScoringDataAutotekaRestrictions(AvitoObject)

cls ScoringDataAutotekaStealing(AvitoObject)

cls ScoringDataAutotekaTaxi(AvitoObject)

cls ScoringIdResultAutoteka(AvitoObject)

cls ScoringNormalizedValue(AvitoObject)

cls ScoringPlacements(AvitoObject)

cls ScoringSeriousDamage(AvitoObject)

cls ScoringSeriousDamageSalvageCarAuctions(AvitoObject)

cls ScoringTechSpecification(AvitoObject)

cls ScoringTechSpecificationBrand(AvitoObject)

cls ScoringTechSpecificationColor(AvitoObject)

cls ScoringTechSpecificationEngineType(AvitoObject)

cls ScoringTechSpecificationHorsepower(AvitoObject)

cls ScoringTechSpecificationMaxWeight(AvitoObject)

cls ScoringTechSpecificationModel(AvitoObject)

cls ScoringTechSpecificationNetWeight(AvitoObject)

cls ScoringTechSpecificationVehicleCategory(AvitoObject)

cls ScoringTechSpecificationVehicleType(AvitoObject)

cls ScoringTechSpecificationVolume(AvitoObject)

cls ScoringTechSpecificationYear(AvitoObject)

cls ServiceInfoAutoteka(AvitoObject)

cls ServiceInfoAutotekaReportCompleteStatus(AvitoObject)

cls ServiceInfoAutotekaReportCompleteStatusUnavailableSources(AvitoObject)

cls SpecificationEquipmentAutoteka(AvitoObject)

cls SpecificationEquipmentAutotekaBodyNumber(AvitoObject)

cls SpecificationEquipmentAutotekaBodyType(AvitoObject)

cls SpecificationEquipmentAutotekaBrand(AvitoObject)

cls SpecificationEquipmentAutotekaColor(AvitoObject)

cls SpecificationEquipmentAutotekaEngineNumber(AvitoObject)

cls SpecificationEquipmentAutotekaEngineType(AvitoObject)

cls SpecificationEquipmentAutotekaHorsepower(AvitoObject)

cls SpecificationEquipmentAutotekaMaxWeight(AvitoObject)

cls SpecificationEquipmentAutotekaModel(AvitoObject)

cls SpecificationEquipmentAutotekaNetWeight(AvitoObject)

cls SpecificationEquipmentAutotekaVehicleCategory(AvitoObject)

cls SpecificationEquipmentAutotekaVolume(AvitoObject)

cls SpecificationEquipmentAutotekaYear(AvitoObject)

cls SpecificationIdResultAutoteka(AvitoObject)

cls SpecificationNormalizedSpecificationAutoteka(AvitoObject)

cls SpecificationNormalizedSpecificationAutotekaBodyType(AvitoObject)

cls SpecificationNormalizedSpecificationAutotekaBrand(AvitoObject)

cls SpecificationNormalizedSpecificationAutotekaCapacity(AvitoObject)

cls SpecificationNormalizedSpecificationAutotekaComplectation(AvitoObject)

cls SpecificationNormalizedSpecificationAutotekaDoorsCount(AvitoObject)

cls SpecificationNormalizedSpecificationAutotekaDrive(AvitoObject)

cls SpecificationNormalizedSpecificationAutotekaEngine(AvitoObject)

cls SpecificationNormalizedSpecificationAutotekaEngineType(AvitoObject)

cls SpecificationNormalizedSpecificationAutotekaGeneration(AvitoObject)

cls SpecificationNormalizedSpecificationAutotekaModel(AvitoObject)

cls SpecificationNormalizedSpecificationAutotekaModification(AvitoObject)

cls SpecificationNormalizedSpecificationAutotekaTransmission(AvitoObject)

cls SpecificationNormalizedSpecificationAutotekaWheel(AvitoObject)

cls SpecificationNormalizedSpecificationAutotekaYear(AvitoObject)

cls SpecificationResultAutoteka(AvitoObject)

cls TaxiDataAutoteka(AvitoObject)

cls TaxiDataEventAutoteka(AvitoObject)

cls Teaser(AvitoObject)

cls TeaserAvailableInfo(AvitoObject)

cls TeaserAvitoPlacements(AvitoObject)

cls TeaserInsights(AvitoObject)

cls TeaserMileage(AvitoObject)

cls TeaserOwners(AvitoObject)

cls TeaserService(AvitoObject)

cls TeaserResponse(AvitoObject)
  get_teaser() -> GetTeaser
    # Build an awaitable :class:`GetTeaser` bound to this object (await to execute).

cls TeaserWithoutDataAutoteka(AvitoObject)

cls TechInspectionHistory(AvitoObject)

cls TechInspectionHistoryEvent(AvitoObject)

cls ValuationBySpecificationResponseBodyAutoteka(AvitoObject)
  # ValuationBySpecificationResponseBodyAutoteka response model.

cls ValuationBySpecificationResultAutoteka(AvitoObject)

cls VehicleSpecifications(AvitoObject)

cls VehicleSpecificationsParam(AvitoObject)

cls TooManyRequestsError(AvitoObject)
  # TooManyRequestsError response model.

cls CatalogsResolveFieldsValueIds(AvitoObject)

cls ValuationBySpecificationLocation(AvitoObject)
  # ValuationBySpecificationLocation response model.

cls ValuationBySpecificationSpecification(AvitoObject)

cls ValuationBySpecificationSpecificationBodyType(AvitoObject)

cls ValuationBySpecificationSpecificationBrand(AvitoObject)

cls ValuationBySpecificationSpecificationColor(AvitoObject)

cls ValuationBySpecificationSpecificationComplectation(AvitoObject)

cls ValuationBySpecificationSpecificationDoorsCount(AvitoObject)

cls ValuationBySpecificationSpecificationGeneration(AvitoObject)

cls ValuationBySpecificationSpecificationModel(AvitoObject)

cls ValuationBySpecificationSpecificationModification(AvitoObject)

cls ValuationBySpecificationSpecificationOwnersCount(AvitoObject)

cls ValuationBySpecificationSpecificationYear(AvitoObject)

cls InsurancePayments(RootModel[list[InsurancePaymentsItem]])
  # Root wrapper for a top-level ``list[InsurancePaymentsItem]`` response.

cls Recalls(RootModel[list[RecallItem]])
  # Root wrapper for a top-level ``list[RecallItem]`` response.

cls SalvageCarAuctionRecords(RootModel[list[SalvageCarAuctionRecordsRoot]])
  # Root wrapper for a top-level ``list[SalvageCarAuctionRecordsRoot]`` response.

```

## avito_promo.py
```
# Авито Promo — domain models (auto-generated from the Avito OpenAPI spec).


cls DefaultErrorResponse(AvitoObject)

cls ErrorFieldsRoot(AvitoObject)
  # Ошибка валидации поля

cls ErrorResponse(AvitoObject)
  # ErrorResponse response model.

cls InviteId(AvitoObject)
  # Идентификатор приглашения нового клиента

cls AgencyBalanceResponse(AvitoObject)

cls AgencyBalanceResponseResult(AvitoObject)

cls AgencyTransactionsResponse(AvitoObject)

cls AgencyTransactionsResponseResult(AvitoObject)
  # Информация о транзакции

cls AgencyTransactionResponse(AvitoObject)

cls AgencyTransactionResponseResult(AvitoObject)
  # Информация о транзакции

cls AgencyClientsResponse(AvitoObject)

cls AgencyClientsResponseResult(AvitoObject)

cls AgencyClientsResponseResultClients(AvitoObject)

cls AgencyClientsResponseResultClientsStatistics(AvitoObject)
  # Статистика клиента

cls AgencyClientsResponseResultClientsSubscription(AvitoObject)

cls AgencyClientsExtra(AvitoObject)
  # Настройка дополнительной информации о клиентах

cls AgencyClientsTargetCreateResponse(AvitoObject)
  # AgencyClientsTargetCreateResponse response model.

cls AgencyClientsTargetResultResponse(AvitoObject)

cls AgencyClientsTargetResultResponseResult(AvitoObject)

cls AgencyClientsTargetResultResponseResultItems(AvitoObject)

cls AgencyClientsTargetResultResponseResultItemsResults(AvitoObject)

cls AgencyFinancesBalanceResponse(AvitoObject)
  # AgencyFinancesBalanceResponse response model.

cls AgencyFinancesTransactionsHistoryResponse(AvitoObject)

cls AgencyFinancesTransactionsHistoryResponseItems(AvitoObject)

cls AgencyUsersInviteSendResponse(AvitoObject)
  # AgencyUsersInviteSendResponse response model.

cls AgencyUsersInviteStatusResponse(AvitoObject)

cls AgencyUsersInviteStatusResponseResult(AvitoObject)

cls AgencyUsersVerificationStatusResponse(AvitoObject)

cls AgencyUsersVerificationStatusResponseResult(AvitoObject)

cls StatsAccountsItemsResponse(AvitoObject)

cls StatsAccountsItemsResponseResult(AvitoObject)

cls StatsAccountsItemsResponseResultGroupings(AvitoObject)

cls StatsAccountsItemsResponseResultGroupingsMetrics(AvitoObject)
  # Статистический показатель

cls StatsAccountsItemsFilter(AvitoObject)
  # Набор ограничений, по которым будут отфильтрованы данные статистики

cls StatsAccountsItemsSort(AvitoObject)

cls StatsAccountsSpendingsResponse(AvitoObject)

cls StatsAccountsSpendingsResponseResult(AvitoObject)

cls StatsAccountsSpendingsResponseResultGroupings(AvitoObject)

cls StatsAccountsSpendingsResponseResultGroupingsSpendings(AvitoObject)

cls StatsAccountsSpendingsResponseResultGroupingsSpendingsServices(AvitoObject)

cls StatsAccountsSpendingsFilter(AvitoObject)
  # Набор ограничений, по которым будут отфильтрованы данные статистики

cls AmountDouble(RootModel[float])
  # Root wrapper for a top-level ``float`` response.

cls AmountKopecks(RootModel[int])
  # Root wrapper for a top-level ``int`` response.

cls Counter(RootModel[int])
  # Root wrapper for a top-level ``int`` response.

cls Date(RootModel[date])
  # Root wrapper for a top-level ``date`` response.

cls DateTime(RootModel[TZDatetime])
  # Root wrapper for a top-level ``TZDatetime`` response.

cls ErrorField(RootModel[str])
  # Root wrapper for a top-level ``str`` response.

cls ErrorFields(RootModel[list[ErrorFieldsRoot]])
  # Root wrapper for a top-level ``list[ErrorFieldsRoot]`` response.

cls ErrorMessage(RootModel[str])
  # Root wrapper for a top-level ``str`` response.

cls Id(RootModel[int])
  # Root wrapper for a top-level ``int`` response.

cls Ids(RootModel[list[int]])
  # Root wrapper for a top-level ``list[int]`` response.

cls Inn(RootModel[str])
  # Root wrapper for a top-level ``str`` response.

cls Limit(RootModel[int])
  # Root wrapper for a top-level ``int`` response.

cls Offset(RootModel[int])
  # Root wrapper for a top-level ``int`` response.

cls Timestamp(RootModel[int])
  # Root wrapper for a top-level ``int`` response.

cls Toggle(RootModel[bool])
  # Root wrapper for a top-level ``bool`` response.

cls TransactionId(RootModel[str])
  # Root wrapper for a top-level ``str`` response.

```

## calltracking.py
```
# CallTracking[КТ] — domain models (auto-generated from the Avito OpenAPI spec).


cls Call(AvitoObject)

cls GetCallByIdResponse(AvitoObject)
  # GetCallByIdResponse response model.

cls GetCallsResponse(AvitoObject)
  # GetCallsResponse response model.

```

## common.py
```
# Cross-domain value objects: Money, Page envelopes, error body.

T = TypeVar('T', bound=BaseModel)

cls Currency(StrEnum): RUB, USD, EUR
  # ISO-4217 currency codes Avito surfaces in payloads (extend as needed).

cls Money(BaseModel)
  # A monetary amount with explicit currency. Amount is :class:`Decimal`, never ``float``.

cls Page(BaseModel, Generic[T])
  # Page-of-results envelope returned by ``page``/``per_page`` endpoints.

cls AvitoErrorBody(BaseModel)
  # Common Avito error payload (``{"error": {"code": ..., "message": ...}}``).

_require_tz(v: datetime) -> datetime
  # Reject naive datetimes — every wire datetime must carry timezone info.

```

## cpa.py
```
# CPA Авито — domain models (auto-generated from the Avito OpenAPI spec).


cls Call(AvitoObject)

cls CallById(AvitoObject)

cls CallV2(AvitoObject)

cls CallsByTime(AvitoObject)

cls CpaErrorChat(AvitoObject)
  # CpaErrorChat response model.

cls CpaErrorChatResult(AvitoObject)

cls CreateComplaint(AvitoObject)

cls CreateComplaintV4In(AvitoObject)

cls InternalErrorResult(AvitoObject)
  # InternalErrorResult response model.

cls OpenApiChatsByTimeFilters(AvitoObject)
  # OpenApiChatsByTimeFilters response model.

cls OpenApiChatsByTimeIn(AvitoObject)

cls OpenApiChatsByTimeMetaFilters(AvitoObject)
  # OpenApiChatsByTimeMetaFilters response model.

cls OpenApiChatsByTimeOut(AvitoObject)

cls OpenApiChatsByTimeV2In(AvitoObject)

cls OpenApiChatsByTimeV2Out(AvitoObject)

cls OpenApiPhonesInfoFromChatsIn(AvitoObject)

cls OpenApiPhonesInfoFromChatsOut(AvitoObject)

cls OpenApiChat(AvitoObject)

cls OpenApiChatByActionIdIn(AvitoObject)

cls OpenApiChatByActionIdOut(AvitoObject)
  # OpenApiChatByActionIdOut response model.

cls OpenApiChatsBuyer(AvitoObject)

cls OpenApiChatsComposition(AvitoObject)

cls OpenApiChatsItem(AvitoObject)

cls OpenApiError(AvitoObject)
  # OpenApiError response model.

cls OpenApiErrorResult(AvitoObject)
  # OpenApiErrorResult response model.

cls OpenApiErrorResultError(AvitoObject)

cls OpenApiErrorResultErrorPayload(AvitoObject)
  # OpenApiErrorResultErrorPayload response model.

cls OpenApiErrorOld(AvitoObject)
  # OpenApiErrorOld response model.

cls OpenApiErrorOldResult(AvitoObject)

cls TooManyRequestsError(AvitoObject)
  # TooManyRequestsError response model.

cls ChatByActionIdResponse(AvitoObject)
  # ChatByActionIdResponse response model.

cls ChatsByTimeResponse(AvitoObject)
  # ChatsByTimeResponse response model.

cls PostCreateComplaintResponse(AvitoObject)

cls CreateComplaintByActionIdResponse(AvitoObject)

cls PhonesInfoFromChatsResponse(AvitoObject)

cls BalanceInfoV2Response(AvitoObject)

cls GetCallByIdV2Response(AvitoObject)
  # GetCallByIdV2Response response model.

cls GetCallsByTimeV2Response(AvitoObject)

cls ChatsByTime2Response(AvitoObject)
  # ChatsByTime2Response response model.

```

## cpxpromo.py
```
# Настройка цены целевого действия — domain models (auto-generated from the Avito OpenAPI spec).


cls AutoBid(AvitoObject)

cls ManualBid(AvitoObject)

cls RemovePromotion(AvitoObject)

cls Auto(AvitoObject)

cls AutoPromotion(AvitoObject)

cls Bid(AvitoObject)

cls Budget(AvitoObject)

cls BudgetValue(AvitoObject)

cls GetBidsOut(AvitoObject)

cls GetPromotionsByItemIdsIn(AvitoObject)
  # GetPromotionsByItemIdsIn response model.

cls GetPromotionsByItemIdsOut(AvitoObject)
  # GetPromotionsByItemIdsOut response model.

cls GetPromotionsByItemIdsOutItems(AvitoObject)

cls Manual(AvitoObject)

cls ManualPromotion(AvitoObject)

cls TooManyRequestsError(AvitoObject)
  # TooManyRequestsError response model.

```

## delivery.py
```
# Доставка — domain models (auto-generated from the Avito OpenAPI spec).


cls AddTariffReply(AvitoObject)
  # AddTariffReply response model.

cls AddTariffReplyData(AvitoObject)

cls AddTariffRequest(AvitoObject)

cls AddTariffRequestV2(AvitoObject)

cls AddTaskReply(AvitoObject)
  # AddTaskReply response model.

cls AddTaskReplyData(AvitoObject)

cls AddTerminalsReply(AvitoObject)
  # AddTerminalsReply response model.

cls AddTerminalsReplyData(AvitoObject)

cls Address(AvitoObject)

cls AnnouncementDeliveryParticipant(AvitoObject)

cls AnnouncementDeliveryParticipantDelivery(AvitoObject)

cls AnnouncementDeliveryParticipantDeliverySortingCenter(AvitoObject)

cls AnnouncementPackage(AvitoObject)

cls AnnouncementsCancelRequest(AvitoObject)

cls AnnouncementsCreateRequest(AvitoObject)

cls AnnouncementsCreateRequest3Pl(AvitoObject)

cls AnnouncementsPackage3Pl(AvitoObject)

cls AnnouncementsParcel3Pl(AvitoObject)

cls AnnouncementsSuccessResponse(AvitoObject)
  # AnnouncementsSuccessResponse response model.

cls AnnouncementsSuccessResponseData(AvitoObject)

cls AnnouncementsTrackAnnouncementRequest(AvitoObject)

cls Area(AvitoObject)

cls AreasCustomScheduleTaskResult(AvitoObject)
  # AreasCustomScheduleTaskResult response model.

cls AreasTaskResult(AvitoObject)
  # AreasTaskResult response model.

cls CancelSandboxParcelOptions(AvitoObject)
  # CancelSandboxParcelOptions response model.

cls CancelSandboxParcelReply(AvitoObject)
  # CancelSandboxParcelReply response model.

cls CancelSandboxParcelReplyData(AvitoObject)
  # CancelSandboxParcelReplyData response model.

cls CancelSandxobParcelRequest(AvitoObject)
  # CancelSandxobParcelRequest response model.

cls ChangeParcelReply(AvitoObject)
  # ChangeParcelReply response model.

cls ChangeParcelReplyData(AvitoObject)

cls ChangeParcelRequest(AvitoObject)

cls ChangeParcelRequestApplication(AvitoObject)

cls ChangeParcelRequestOptions(AvitoObject)

cls ChangeParcelResultReply(AvitoObject)
  # ChangeParcelResultReply response model.

cls ChangeParcelResultRequest(AvitoObject)

cls ChangeParcelResultRequestOptions(AvitoObject)

cls ChangeParcelsApplication(AvitoObject)

cls ChangeParcelsClient(AvitoObject)

cls ChangeParcelsData(AvitoObject)

cls ChangeParcelsRequest(AvitoObject)

cls ChangeParcelsResponse(AvitoObject)
  # ChangeParcelsResponse response model.

cls ChangeParcelsTerminal(AvitoObject)

cls CheckConfirmationCodeReply(AvitoObject)
  # CheckConfirmationCodeReply response model.

cls CheckConfirmationCodeReplyData(AvitoObject)
  # CheckConfirmationCodeReplyData response model.

cls CheckConfirmationCodeRequest(AvitoObject)
  # CheckConfirmationCodeRequest response model.

cls CreateParcelClient(AvitoObject)

cls CreateParcelClientDelivery(AvitoObject)

cls CreateParcelClientDeliveryCourier(AvitoObject)

cls CreateParcelClientDeliveryCourierAddress(AvitoObject)

cls CreateParcelClientDeliveryCourierAddressDetails(AvitoObject)

cls CreateParcelClientDeliveryCourierCoordinates(AvitoObject)

cls CreateParcelClientDeliveryCourierDateTimeInterval(AvitoObject)

cls CreateParcelClientDeliveryCourierOptions(AvitoObject)

cls CreateParcelClientDeliveryCourierPickupContact(AvitoObject)

cls CreateParcelClientDeliverySecondPartyLogist(AvitoObject)

cls CreateParcelClientDeliverySortingCenter(AvitoObject)

cls CreateParcelClientDeliveryTerminal(AvitoObject)

cls CreateParcelCourierAddress(AvitoObject)

cls CreateParcelCourierAddressDetails(AvitoObject)

cls CreateParcelCourierCoordinates(AvitoObject)

cls CreateParcelCourierDateTimeInterval(AvitoObject)

cls CreateParcelCourierOptions(AvitoObject)

cls CreateParcelData(AvitoObject)

cls CreateParcelDeliveryCourier(AvitoObject)
  # CreateParcelDeliveryCourier response model.

cls CreateParcelItem(AvitoObject)

cls CreateParcelItemDimensions(AvitoObject)

cls CreateParcelItemImagesUrls(AvitoObject)

cls CreateParcelItemWeight(AvitoObject)

cls CreateParcelOptions(AvitoObject)

cls CreateParcelOptionsReturn(AvitoObject)
  # Опции возврата. Опции определяют политику возвратов. Доступен ли возврат, или что делать в определенных случаях.

cls CreateParcelOptionsReturnPolicy(AvitoObject)

cls CreateParcelOptionsReturnPolicyAfter(AvitoObject)

cls CreateParcelPackage(AvitoObject)
  # CreateParcelPackage response model.

cls CreateParcelPayment(AvitoObject)
  # CreateParcelPayment response model.

cls CreateParcelPaymentDelivery(AvitoObject)

cls CreateParcelPaymentItems(AvitoObject)

cls CreateParcelReply(AvitoObject)
  # CreateParcelReply response model.

cls CreateParcelReplyData(AvitoObject)

cls CreateParcelRequest(AvitoObject)

cls CreateParcelResponse(AvitoObject)
  # CreateParcelResponse response model.

cls CreateParcelUserDeliveryTerminal(AvitoObject)

cls CreateSandboxParcelItem(AvitoObject)

cls CreateSandboxParcelItemDimensions(AvitoObject)
  # Габариты товара в сантиметрах. Порядок [ширина, высота, длина]. Например, [15, 25, 35].

cls CreateSandboxParcelItemWeight(AvitoObject)
  # CreateSandboxParcelItemWeight response model.

cls CreateSandboxParcelOptions(AvitoObject)

cls CreateSandboxParcelOptionsXDelivery(AvitoObject)

cls CreateSandboxParcelReceiverDelivery(AvitoObject)
  # CreateSandboxParcelReceiverDelivery response model.

cls CreateSandboxParcelUserDelivery(AvitoObject)
  # CreateSandboxParcelUserDelivery response model.

cls CreateSandboxParcelV2(AvitoObject)
  # CreateSandboxParcelV2 response model.

cls CreateSandboxParcelV2Receiver(AvitoObject)
  # CreateSandboxParcelV2Receiver response model.

cls CreateSandboxParcelV2Sender(AvitoObject)

cls CreateSandboxV2Options(AvitoObject)

cls DeliveryCoordinates(AvitoObject)

cls DeliveryDateInterval(AvitoObject)

cls DeliveryParams(AvitoObject)
  # DeliveryParams response model.

cls DeliveryTerms(AvitoObject)
  # DeliveryTerms response model.

cls DeliveryError4Xx(AvitoObject)

cls DeliveryIntervalInDate(AvitoObject)

cls DeliverySetOrderPropertiesReply(AvitoObject)
  # DeliverySetOrderPropertiesReply response model.

cls DeliverySetOrderPropertiesRequest(AvitoObject)
  # DeliverySetOrderPropertiesRequest response model.

cls DeliverySetOrderRealAddresseReply(AvitoObject)
  # DeliverySetOrderRealAddresseReply response model.

cls DeliverySetRealAddressRequest(AvitoObject)
  # DeliverySetRealAddressRequest response model.

cls DeliverySetRealAddressRequestAddress(AvitoObject)

cls DeliverySetStatusDetails(AvitoObject)

cls DeliverySetStatusReply(AvitoObject)
  # DeliverySetStatusReply response model.

cls DeliverySetStatusReplyData(AvitoObject)

cls DeliveryTariffZoneServiceDeliveryB2C(AvitoObject)

cls DeliveryTariffZoneServiceDeliveryB2CWithStepCost(AvitoObject)

cls DeliveryTariffZoneServiceDeliveryB2CWithStepCostValues(AvitoObject)

cls DeliveryTariffZoneServiceDeliveryB2CWithStepMinCost(AvitoObject)

cls DeliveryTariffZoneServiceDeliveryB2CWithStepMinCostValues(AvitoObject)

cls DeliveryTariffZoneServiceDeliveryC2C(AvitoObject)

cls DeliveryTariffZoneServiceDeliveryC2CWithStepCost(AvitoObject)

cls DeliveryTariffZoneServiceDeliveryC2CWithStepCostValues(AvitoObject)

cls DeliveryTariffZoneServiceDeliveryC2CWithStepMinCost(AvitoObject)

cls DeliveryTariffZoneServiceDeliveryC2CWithStepMinCostValues(AvitoObject)

cls DeliveryTariffZoneServiceInsuranceB2C(AvitoObject)

cls DeliveryTariffZoneServiceInsuranceB2CValues(AvitoObject)

cls DeliveryTariffZoneServiceInsuranceC2C(AvitoObject)

cls DeliveryTariffZoneServiceInsuranceC2CValues(AvitoObject)

cls DeliveryTrackingRequest(AvitoObject)

cls DeliveryTrackingRequestOptions(AvitoObject)

cls Direction(AvitoObject)

cls DirectionV2(AvitoObject)

cls GetChangeParcelInfoReply(AvitoObject)
  # GetChangeParcelInfoReply response model.

cls GetChangeParcelInfoReplyData(AvitoObject)

cls GetChangeParcelInfoReplyDataReceiver(AvitoObject)

cls GetChangeParcelInfoRequest(AvitoObject)

cls GetInfoByOrderIdErrorReply(AvitoObject)

cls GetRegisteredParcelIdReply(AvitoObject)
  # GetRegisteredParcelIdReply response model.

cls GetRegisteredParcelIdReplyData(AvitoObject)
  # GetRegisteredParcelIdReplyData response model.

cls GetRegisteredParcelIdRequest(AvitoObject)
  # GetRegisteredParcelIdRequest response model.

cls GetSandboxParcelInfoDimensions(AvitoObject)
  # GetSandboxParcelInfoDimensions response model.

cls GetSandboxParcelInfoParcelHistory(AvitoObject)
  # GetSandboxParcelInfoParcelHistory response model.

cls GetSandboxParcelInfoReply(AvitoObject)
  # GetSandboxParcelInfoReply response model.

cls GetSandboxParcelInfoReplyData(AvitoObject)

cls GetSandboxParcelInfoReplyDataReceiver(AvitoObject)
  # GetSandboxParcelInfoReplyDataReceiver response model.

cls GetSandboxParcelInfoReplyDataSender(AvitoObject)
  # GetSandboxParcelInfoReplyDataSender response model.

cls GetSandboxParcelInfoRequest(AvitoObject)
  # GetSandboxParcelInfoRequest response model.

cls GetSandboxParcelInfoTerminals(AvitoObject)

cls GetTariffTaskReply(AvitoObject)
  # GetTariffTaskReply response model.

cls GetTariffTaskReplyData(AvitoObject)

cls GetTaskData(AvitoObject)

cls GetTaskReply(AvitoObject)
  # GetTaskReply response model.

cls GetTerminalsTaskReply(AvitoObject)
  # GetTerminalsTaskReply response model.

cls GetTerminalsTaskReplyData(AvitoObject)

cls ImageUrls(AvitoObject)

cls Restriction(AvitoObject)

cls SandboxCancelAnnouncementOptions(AvitoObject)

cls SandboxCancelAnnouncementReply(AvitoObject)
  # SandboxCancelAnnouncementReply response model.

cls SandboxCancelAnnouncementReplyData(AvitoObject)

cls SandboxCancelAnnouncementRequest(AvitoObject)

cls SandboxCreateAnnouncementDeliveryPoint(AvitoObject)

cls SandboxCreateAnnouncementOptions(AvitoObject)

cls SandboxCreateAnnouncementPackage(AvitoObject)

cls SandboxCreateAnnouncementParticipant(AvitoObject)

cls SandboxCreateAnnouncementParticipantDelivery(AvitoObject)

cls SandboxCreateAnnouncementReply(AvitoObject)
  # SandboxCreateAnnouncementReply response model.

cls SandboxCreateAnnouncementReplyData(AvitoObject)

cls SandboxCreateAnnouncementRequest(AvitoObject)

cls SandboxGetAnnouncementEventReply(AvitoObject)
  # SandboxGetAnnouncementEventReply response model.

cls SandboxGetAnnouncementEventReplyData(AvitoObject)

cls SandboxGetAnnouncementEventRequest(AvitoObject)

cls Schedule(AvitoObject)
  # Значения интервала времени в течение дня должны быть в диапазоне от `00:00:00` до `23:59:59`. Интервал работы после полуночи необходимо переносить в следующий день недели. Правильно: - `"fri": ["09:00:00/12:00:00", "13:00:00/18:00:00"]` – расписание в пятницу с 9 до 18 с перерывом с 12 до 13 - `"sun": []` – выходной в воскресенье Неправильно: - `"mon": ["09:00/18:00"]` – не хватает значения секунд - `"tue": ["09:00:00/01:00:00"]` – интервал заходит на следующий день - `"wen": ["09:00:00/00:00:00"]` – максимальное значение границы должно быть `23:59:59`

cls SetStatusErrorReply(AvitoObject)

cls SetStatusReply(AvitoObject)

cls SetStatusRequest(AvitoObject)

cls SortingCenterGet(AvitoObject)
  # SortingCenterGet response model.

cls SortingCenterGetData(AvitoObject)

cls SortingCenterId(AvitoObject)

cls SortingCenterPost(AvitoObject)

cls TaggedSortingCenter(AvitoObject)
  # TaggedSortingCenter response model.

cls TariffTaskResult(AvitoObject)

cls TariffZone(AvitoObject)

cls Terminal(AvitoObject)

cls TerminalsTaskResult(AvitoObject)

cls TermsZone(AvitoObject)

cls UpdateTermsReply(AvitoObject)
  # UpdateTermsReply response model.

cls ValuesByDimension(AvitoObject)

cls ValuesByDimensionValues(AvitoObject)

cls ValuesByPaidWeight(AvitoObject)

cls ValuesByPaidWeightValues(AvitoObject)

cls ValuesByWeight(AvitoObject)

cls ValuesByWeightValues(AvitoObject)

cls Zone(AvitoObject)

cls CancelParcelReply(AvitoObject)
  # CancelParcelReply response model.

cls CancelParcelReplyData(AvitoObject)

cls CancelParcelRequest(AvitoObject)

cls CustomAreaScheduleRequestObject(AvitoObject)

cls CutoffAndSchedule(AvitoObject)
  # CutoffAndSchedule response model.

cls CutoffAndScheduleCutoff(AvitoObject)

cls ProhibitOrderAcceptanceReply(AvitoObject)
  # ProhibitOrderAcceptanceReply response model.

cls ProhibitOrderAcceptanceReplyData(AvitoObject)

cls ProhibitOrderAcceptanceRequest(AvitoObject)
  # ProhibitOrderAcceptanceRequest response model.

cls UpdateReceiverInfoReply(AvitoObject)
  # UpdateReceiverInfoReply response model.

cls UpdateReturnInfoReply(AvitoObject)
  # UpdateReturnInfoReply response model.

cls SetOrderRealAddressAddress(AvitoObject)

cls TrackingOptions(AvitoObject)

cls CreateSandboxParcelV22Receiver(AvitoObject)
  # CreateSandboxParcelV22Receiver response model.

cls CreateSandboxParcelV22Sender(AvitoObject)

cls ChangeParcelResultOptions(AvitoObject)

cls AddAreasRequest(RootModel[list[Area]])
  # Root wrapper for a top-level ``list[Area]`` response.

cls AddSortingCentersRequest(RootModel[list[SortingCenterPost]])
  # Root wrapper for a top-level ``list[SortingCenterPost]`` response.

cls AddTerminalsRequest(RootModel[list[Terminal]])
  # Root wrapper for a top-level ``list[Terminal]`` response.

cls Cost(RootModel[int])
  # Root wrapper for a top-level ``int`` response.

cls DateWithTz(RootModel[str])
  # Root wrapper for a top-level ``str`` response.

cls DeliveryDimensions(RootModel[list[int]])
  # Root wrapper for a top-level ``list[int]`` response.

cls DeliveryDirectControlDate(RootModel[str])
  # Root wrapper for a top-level ``str`` response.

cls DeliveryDirectionTag(RootModel[DeliveryDirectionTagRoot])
  # Root wrapper for a top-level ``DeliveryDirectionTagRoot`` response.

cls DeliveryEventDateTime(RootModel[str])
  # Root wrapper for a top-level ``str`` response.

cls DeliveryOrderIdString(RootModel[str])
  # Root wrapper for a top-level ``str`` response.

cls DeliveryPhones(RootModel[list[str]])
  # Root wrapper for a top-level ``list[str]`` response.

cls DeliveryReceiverTerminalCode(RootModel[DeliveryReceiverTerminalCodeRoot])
  # Root wrapper for a top-level ``DeliveryReceiverTerminalCodeRoot`` response.

cls DeliveryReturnControlDate(RootModel[str])
  # Root wrapper for a top-level ``str`` response.

cls DeliverySenderReceiveTerminalCode(RootModel[DeliverySenderReceiveTerminalCodeRoot])
  # Root wrapper for a top-level ``DeliverySenderReceiveTerminalCodeRoot`` response.

cls DeliveryToughWrap(RootModel[bool])
  # Root wrapper for a top-level ``bool`` response.

cls DeliveryWeight(RootModel[Any])
  # Root wrapper for a top-level ``Any`` response.

cls DeliveryZipCode(RootModel[str])
  # Root wrapper for a top-level ``str`` response.

cls DeliveryDayTimeInterval(RootModel[str])
  # Root wrapper for a top-level ``str`` response.

cls DeliveryDayTimeIntervals(RootModel[list[str]])
  # Root wrapper for a top-level ``list[str]`` response.

cls DeliveryProviderAreaNumber(RootModel[str])
  # Root wrapper for a top-level ``str`` response.

cls DeliveryTariffZoneServiceDeliveryB2CByDimension(RootModel[Any])
  # Root wrapper for a top-level ``Any`` response.

cls DeliveryTariffZoneServiceDeliveryB2CByPaidWeight(RootModel[Any])
  # Root wrapper for a top-level ``Any`` response.

cls DeliveryTariffZoneServiceDeliveryB2CByWeight(RootModel[Any])
  # Root wrapper for a top-level ``Any`` response.

cls DeliveryTariffZoneServiceDeliveryC2CByDimension(RootModel[Any])
  # Root wrapper for a top-level ``Any`` response.

cls DeliveryTariffZoneServiceDeliveryC2CByPaidWeight(RootModel[Any])
  # Root wrapper for a top-level ``Any`` response.

cls DeliveryTariffZoneServiceDeliveryC2CByWeight(RootModel[Any])
  # Root wrapper for a top-level ``Any`` response.

cls TaggedSortingCenterRequest(RootModel[list[TaggedSortingCenter]])
  # Root wrapper for a top-level ``list[TaggedSortingCenter]`` response.

cls Uuid(RootModel[str])
  # Root wrapper for a top-level ``str`` response.

cls UpdateTermsRequest(RootModel[list[TermsZone]])
  # Root wrapper for a top-level ``list[TermsZone]`` response.

cls CustomAreaScheduleRequest(RootModel[list[CustomAreaScheduleRequestObject]])
  # Root wrapper for a top-level ``list[CustomAreaScheduleRequestObject]`` response.

```

## items.py
```
# Объявления — domain models (auto-generated from the Avito OpenAPI spec).


cls AnalyticsRequest(AvitoObject)

cls AnalyticsRequestFilter(AvitoObject)

cls AnalyticsRequestSort(AvitoObject)

cls AnalyticsResponse(AvitoObject)
  # AnalyticsResponse response model.

cls AnalyticsResponseResult(AvitoObject)
  # AnalyticsResponseResult response model.

cls AnalyticsResponseResultGroupings(AvitoObject)
  # AnalyticsResponseResultGroupings response model.

cls AnalyticsResponseResultGroupingsMetrics(AvitoObject)
  # AnalyticsResponseResultGroupingsMetrics response model.

cls ApplyVasResp(AvitoObject)

cls CallsStatsDay(AvitoObject)

cls CallsStatsItem(AvitoObject)

cls CallsStatsRequest(AvitoObject)

cls CallsStatsResponse(AvitoObject)
  # CallsStatsResponse response model.

cls CallsStatsResponseResult(AvitoObject)

cls ErrorResponse(AvitoObject)
  # ErrorResponse response model.

cls InfoVas(AvitoObject)

cls ItemInfoAvito(AvitoObject)
  get_item_info() -> GetItemInfo
    # Build an awaitable :class:`GetItemInfo` bound to this object (await to execute).
  put_item_vas(vas_id: PutItemVasVasId) -> PutItemVas
    # Build an awaitable :class:`PutItemVas` bound to this object (await to execute).
  update_price(price: int) -> UpdatePrice
    # Build an awaitable :class:`UpdatePrice` bound to this object (await to execute).
  put_item_vas_package_v2(package_id: PutItemVasPackageV2PackageId) -> PutItemVasPackageV2
    # Build an awaitable :class:`PutItemVasPackageV2` bound to this object (await to execute).
  apply_vas(slugs: list[str, stickers: list[int]? = None) -> ApplyVas
    # Build an awaitable :class:`ApplyVas` bound to this object (await to execute).

cls ItemVasPricesResp(AvitoObject)

cls ItemsInfoWithCategoryAvito(AvitoObject)
  # ItemsInfoWithCategoryAvito response model.

cls ItemsInfoWithCategoryAvitoMeta(AvitoObject)

cls ItemsInfoWithCategoryAvitoResources(AvitoObject)

cls ItemsInfoWithCategoryAvitoResourcesCategory(AvitoObject)

cls SpendingsRequest(AvitoObject)

cls SpendingsRequestFilter(AvitoObject)

cls SpendingsResponse(AvitoObject)
  # SpendingsResponse response model.

cls SpendingsResponseResult(AvitoObject)

cls SpendingsResponseResultGroupings(AvitoObject)

cls SpendingsResponseResultGroupingsSpendings(AvitoObject)

cls SpendingsResponseResultGroupingsSpendingsServices(AvitoObject)

cls StatisticsCountersRoot(AvitoObject)

cls StatisticsCountersRootStats(AvitoObject)

cls StatisticsResponse(AvitoObject)

cls StatisticsResponseResult(AvitoObject)
  # Статистические счетчики объявления

cls StatisticsCountersValue(AvitoObject)

cls StatisticsCountersValueStats(AvitoObject)

cls StatisticsShallowRequestBody(AvitoObject)
  # StatisticsShallowRequestBody response model.

cls StickerResp(AvitoObject)

cls UpdatePriceRequest(AvitoObject)

cls UpdatePriceResponse(AvitoObject)
  # UpdatePriceResponse response model.

cls VasAmountAvito(AvitoObject)

cls VasApplyAvito(AvitoObject)

cls VasResp(AvitoObject)

cls ItemIdsRequestBody(AvitoObject)

cls PackageIdRequestBodyV2(AvitoObject)

cls TooManyRequests(AvitoObject)
  # TooManyRequests response model.

cls VasIdRequestBody(AvitoObject)

cls ApplyVasResponse(AvitoObject)
  # ApplyVasResponse response model.

cls ItemAnalyticsFilter(AvitoObject)

cls ItemAnalyticsSort(AvitoObject)

cls AccountSpendingsFilter(AvitoObject)

cls ErrorItemsVas(RootModel[list[int]])
  # Root wrapper for a top-level ``list[int]`` response.

cls StatisticsCounters(RootModel[list[StatisticsCountersRoot]])
  # Root wrapper for a top-level ``list[StatisticsCountersRoot]`` response.

cls StatisticsDateFrom(RootModel[str])
  # Root wrapper for a top-level ``str`` response.

cls StatisticsDateTo(RootModel[str])
  # Root wrapper for a top-level ``str`` response.

cls StatisticsFields(RootModel[list[StatisticsFieldsRoot]])
  # Root wrapper for a top-level ``list[StatisticsFieldsRoot]`` response.

cls StatisticsItemIds(RootModel[list[int]])
  # Root wrapper for a top-level ``list[int]`` response.

cls VasPricesResp(RootModel[list[ItemVasPricesResp]])
  # Root wrapper for a top-level ``list[ItemVasPricesResp]`` response.

```

## job.py
```
# Авито.Работа — domain models (auto-generated from the Avito OpenAPI spec).


cls ActivationForbiddenError(AvitoObject)
  # ActivationForbiddenError response model.

cls ActivationForbiddenErrorError(AvitoObject)

cls AddressDetails(AvitoObject)

cls AgeCriteria(AvitoObject)
  # Возраст кандидата. Если выберите значения, в данных кандидата будет отметка, что кандидат соответствует этому критерию или нет. Кандидаты не увидят этого в вакансии.

cls ApplicationsApplyActionsRequestBody(AvitoObject)

cls ApplicationsGetStatesResult(AvitoObject)

cls ApplicationsGetStatesResultStates(AvitoObject)

cls ApplyProcessing(AvitoObject)

cls BadRequest(AvitoObject)
  # BadRequest response model.

cls BadRequestOnVacancy(AvitoObject)
  # BadRequestOnVacancy response model.

cls BadRequestShort(AvitoObject)
  # BadRequestShort response model.

cls BadRequestShortError(AvitoObject)

cls Citizenship(AvitoObject)

cls ConflictErrorError(AvitoObject)

cls Contacts(AvitoObject)

cls Coordinates(AvitoObject)

cls CreationForbiddenError(AvitoObject)
  # CreationForbiddenError response model.

cls CreationForbiddenErrorError(AvitoObject)

cls EditingForbiddenError(AvitoObject)
  # EditingForbiddenError response model.

cls EditingForbiddenErrorError(AvitoObject)

cls EnrichedProperties(AvitoObject)

cls EnrichedPropertiesAge(AvitoObject)

cls EnrichedPropertiesCitizenship(AvitoObject)

cls EnrichedPropertiesExperience(AvitoObject)

cls EnrichedPropertiesFullName(AvitoObject)

cls EnrichedPropertiesGender(AvitoObject)

cls EnrichedPropertiesPhone(AvitoObject)

cls GetApplicationsByIdsResult(AvitoObject)

cls GetApplicationsByIdsResultApplies(AvitoObject)

cls GetApplicationsByIdsResultAppliesApplicant(AvitoObject)
  # Данные соискателя

cls GetApplicationsByIdsResultAppliesApplicantData(AvitoObject)

cls GetApplicationsByIdsResultAppliesApplicantDataFullName(AvitoObject)

cls GetApplicationsByIdsResultAppliesContacts(AvitoObject)

cls GetApplicationsByIdsResultAppliesContactsChat(AvitoObject)

cls GetApplicationsByIdsResultAppliesContactsPhones(AvitoObject)

cls GetApplicationsByIdsResultAppliesPrevalidation(AvitoObject)

cls GetApplicationsByIdsResultAppliesPrice(AvitoObject)

cls GetApplicationsIdsResult(AvitoObject)

cls GetApplicationsIdsResultApplies(AvitoObject)

cls ItemNotFoundError(AvitoObject)
  # ItemNotFoundError response model.

cls ItemNotFoundErrorError(AvitoObject)

cls Location(AvitoObject)

cls LocationAddress(AvitoObject)

cls NotFoundErrorError(AvitoObject)

cls PaymentError(AvitoObject)
  # PaymentError response model.

cls PaymentErrorError(AvitoObject)

cls Phone(AvitoObject)

cls Photo(AvitoObject)

cls PrevalidationAnswer(AvitoObject)

cls Resume20(AvitoObject)

cls Resume20Params(AvitoObject)

cls Resume20ParamsEducationList(AvitoObject)

cls Resume20ParamsExperienceList(AvitoObject)

cls Resume20ParamsLanguageList(AvitoObject)

cls ResumeContact(AvitoObject)

cls ResumeContacts(AvitoObject)

cls ResumeContactsFullName(AvitoObject)

cls ResumeSearchMeta(AvitoObject)

cls SalaryBaseRange(AvitoObject)

cls SalaryDetail(AvitoObject)

cls SalaryDetailBase(AvitoObject)
  # Оклад

cls SetApplicationsIsViewedResult(AvitoObject)

cls SetApplicationsIsViewedResultApplies(AvitoObject)

cls SimplifiedResume(AvitoObject)

cls SimplifiedVacancy(AvitoObject)
  # SimplifiedVacancy response model.

cls SimplifiedVacancyAddressDetails(AvitoObject)
  # SimplifiedVacancyAddressDetails response model.

cls Specialization(AvitoObject)

cls StoppingForbiddenError(AvitoObject)
  # StoppingForbiddenError response model.

cls StoppingForbiddenErrorError(AvitoObject)

cls VacanciesGetByIdsBody(AvitoObject)

cls Vacancy20(AvitoObject)

cls Vacancy20AddressDetails(AvitoObject)

cls Vacancy20AddressDetailsCoordinates(AvitoObject)

cls Vacancy20Contacts(AvitoObject)

cls Vacancy20Params(AvitoObject)

cls Vacancy20ParamsCoordinates(AvitoObject)

cls Vacancy20ParamsSalary(AvitoObject)

cls Vacancy20ParamsSalaryBaseRange(AvitoObject)

cls VacancyAutoRenewal(AvitoObject)
  # VacancyAutoRenewal response model.

cls VacancyCreate(AvitoObject)

cls VacancyCreateDrivingExperience(AvitoObject)
  # Стаж вождения

cls VacancyCreateExperience(AvitoObject)
  # Опыт работы

cls VacancyCreatePayoutFrequency(AvitoObject)
  # Частота выплат Возможные значения: - "dailyPay" - Каждый день; - "biweeklyPay" - Дважды в месяц; - "weeklyPay" - Раз в неделю; - "thriceMonthlyPay" - три раза в месяц; - "monthlyPay" - Раз в месяц. Для paid_period равным month и week недоступно для выбора dailyPay. deprecated значение hourlyPay будет заменено на dailyPay

cls VacancyCreateSalaryRange(AvitoObject)

cls VacancyCreateSchedule(AvitoObject)
  # Режим работы Возможные значения: - flyInFlyOut - Вахта - fixed - Фиксированный - flexible - Гибкий - shift - Сменный deprecated значения fiveDay, sixDay, partTime, fullDay и remote будут заменены на fixed flyInFlyOut - Вахта, при выборе данного режима работы, адрес вакансии может быть только "Город", если адрес передается полноценный, то улица будет отрезана и адрес будет до "Города".

cls VacancyCreateResult(AvitoObject)

cls VacancyProlongate(AvitoObject)

cls VacancySearchMeta(AvitoObject)

cls VacancyStatusesBody(AvitoObject)
  # VacancyStatusesBody response model.

cls VacancyStatusesResultRoot(AvitoObject)

cls VacancyStatusesResultRootLastAction(AvitoObject)

cls VacancyStatusesResultRootVacancy(AvitoObject)

cls VacancyUpdate(AvitoObject)

cls VacancyUpdateDrivingExperience(AvitoObject)
  # Стаж вождения

cls VacancyUpdateExperience(AvitoObject)
  # Опыт работы

cls VacancyUpdatePayoutFrequency(AvitoObject)
  # Частота выплат Возможные значения: - "dailyPay" - Каждый день; - "biweeklyPay" - Дважды в месяц; - "weeklyPay" - Раз в неделю; - "thriceMonthlyPay" - три раза в месяц - "monthlyPay" - Раз в месяц. deprecated значение hourlyPay будет заменено на dailyPay

cls VacancyUpdateSalaryRange(AvitoObject)

cls VacancyV2Create(AvitoObject)

cls VacancyV2CreateContacts(AvitoObject)

cls VacancyV2CreateLocation(AvitoObject)
  # Геолокация вакансии (как минимум одно из значений)

cls VacancyV2CreateSalary(AvitoObject)

cls VacancyV2CreateResult(AvitoObject)

cls WebhookSubscribeRequestBody(AvitoObject)

cls WebhooksSubscriptionResultList(AvitoObject)

cls TooManyRequestsError(AvitoObject)
  # TooManyRequestsError response model.

cls ApplicationsSetIsViewedApplies(AvitoObject)

cls ResumesGetResponse(AvitoObject)

cls ResumesGetRadius(AvitoObject)

cls ResumesGetRadiusPoint(AvitoObject)

cls VacancyCreate2DrivingExperience(AvitoObject)
  # Стаж вождения

cls VacancyCreate2Experience(AvitoObject)
  # Опыт работы

cls VacancyCreate2PayoutFrequency(AvitoObject)
  # Частота выплат Возможные значения: - "dailyPay" - Каждый день; - "biweeklyPay" - Дважды в месяц; - "weeklyPay" - Раз в неделю; - "thriceMonthlyPay" - три раза в месяц; - "monthlyPay" - Раз в месяц. Для paid_period равным month и week недоступно для выбора dailyPay. deprecated значение hourlyPay будет заменено на dailyPay

cls VacancyCreate2SalaryRange(AvitoObject)

cls VacancyCreate2Schedule(AvitoObject)
  # Режим работы Возможные значения: - flyInFlyOut - Вахта - fixed - Фиксированный - flexible - Гибкий - shift - Сменный deprecated значения fiveDay, sixDay, partTime, fullDay и remote будут заменены на fixed flyInFlyOut - Вахта, при выборе данного режима работы, адрес вакансии может быть только "Город", если адрес передается полноценный, то улица будет отрезана и адрес будет до "Города".

cls VacancyUpdate2DrivingExperience(AvitoObject)
  # Стаж вождения

cls VacancyUpdate2Experience(AvitoObject)
  # Опыт работы

cls VacancyUpdate2PayoutFrequency(AvitoObject)
  # Частота выплат Возможные значения: - "dailyPay" - Каждый день; - "biweeklyPay" - Дважды в месяц; - "weeklyPay" - Раз в неделю; - "thriceMonthlyPay" - три раза в месяц - "monthlyPay" - Раз в месяц. deprecated значение hourlyPay будет заменено на dailyPay

cls VacancyUpdate2SalaryRange(AvitoObject)

cls SearchVacancyResponse(AvitoObject)

cls VacancyCreateV2Contacts(AvitoObject)

cls VacancyCreateV2Hierarchy(AvitoObject)

cls VacancyCreateV2Location(AvitoObject)
  # Геолокация вакансии (как минимум одно из значений)

cls VacancyCreateV2Salary(AvitoObject)

cls VacancyUpdateV2Contacts(AvitoObject)

cls VacancyUpdateV2Hierarchy(AvitoObject)

cls VacancyUpdateV2Location(AvitoObject)
  # Геолокация вакансии (как минимум одно из значений)

cls VacancyUpdateV2Salary(AvitoObject)

cls AdministratorOrganizationType(RootModel[int])
  # Root wrapper for a top-level ``int`` response.

cls AllowCalls(RootModel[bool])
  # Root wrapper for a top-level ``bool`` response.

cls Bonuses(RootModel[list[BonusesRoot]])
  # Root wrapper for a top-level ``list[BonusesRoot]`` response.

cls BusinessArea(RootModel[int])
  # Root wrapper for a top-level ``int`` response.

cls CitizenshipCriteria(RootModel[list[CitizenshipCriteriaRoot]])
  # Root wrapper for a top-level ``list[CitizenshipCriteriaRoot]`` response.

cls ConstructionWorkType(RootModel[list[ConstructionWorkTypeRoot]])
  # Root wrapper for a top-level ``list[ConstructionWorkTypeRoot]`` response.

cls Cuisine(RootModel[list[CuisineRoot]])
  # Root wrapper for a top-level ``list[CuisineRoot]`` response.

cls DriverLicenceCategory(RootModel[list[DriverLicenceCategoryRoot]])
  # Root wrapper for a top-level ``list[DriverLicenceCategoryRoot]`` response.

cls DrivingLicenseCategory(RootModel[list[DrivingLicenseCategoryRoot]])
  # Root wrapper for a top-level ``list[DrivingLicenseCategoryRoot]`` response.

cls EateryType(RootModel[list[EateryTypeRoot]])
  # Root wrapper for a top-level ``list[EateryTypeRoot]`` response.

cls FacilityType(RootModel[list[FacilityTypeRoot]])
  # Root wrapper for a top-level ``list[FacilityTypeRoot]`` response.

cls FoodProductionShopType(RootModel[list[FoodProductionShopTypeRoot]])
  # Root wrapper for a top-level ``list[FoodProductionShopTypeRoot]`` response.

cls HtmlTags(RootModel[bool])
  # Root wrapper for a top-level ``bool`` response.

cls MedicalSpecialization(RootModel[list[str]])
  # Root wrapper for a top-level ``list[str]`` response.

cls MedicalSpecializationIds(RootModel[list[int]])
  # Root wrapper for a top-level ``list[int]`` response.

cls Profession(RootModel[int])
  # Root wrapper for a top-level ``int`` response.

cls RegistrationMethod(RootModel[list[RegistrationMethodRoot]])
  # Root wrapper for a top-level ``list[RegistrationMethodRoot]`` response.

cls RetailEquipmentType(RootModel[list[RetailEquipmentTypeRoot]])
  # Root wrapper for a top-level ``list[RetailEquipmentTypeRoot]`` response.

cls RetailShopType(RootModel[list[RetailShopTypeRoot]])
  # Root wrapper for a top-level ``list[RetailShopTypeRoot]`` response.

cls SalaryBaseBonus(RootModel[str])
  # Root wrapper for a top-level ``str`` response.

cls Shifts(RootModel[list[int]])
  # Root wrapper for a top-level ``list[int]`` response.

cls Vacancies20(RootModel[list[Vacancy20]])
  # Root wrapper for a top-level ``list[Vacancy20]`` response.

cls VacancyStatusesResult(RootModel[list[VacancyStatusesResultRoot]])
  # Root wrapper for a top-level ``list[VacancyStatusesResultRoot]`` response.

cls VehicleType(RootModel[int])
  # Root wrapper for a top-level ``int`` response.

cls WorkDaysPerWeek(RootModel[list[int]])
  # Root wrapper for a top-level ``list[int]`` response.

cls WorkHoursPerDay(RootModel[list[int]])
  # Root wrapper for a top-level ``list[int]`` response.

cls WorkerClass(RootModel[list[WorkerClassRoot]])
  # Root wrapper for a top-level ``list[WorkerClassRoot]`` response.

```

## messenger.py
```
# Мессенджер — domain models (auto-generated from the Avito OpenAPI spec).


cls Chat(AvitoObject)
  send_message(message: PostSendMessageMessage? = None, type_: PostSendMessageType? = None) -> PostSendMessage
    # Build an awaitable :class:`PostSendMessage` bound to this object (await to execute).
  send_image_message(image_id: str) -> PostSendImageMessage
    # Build an awaitable :class:`PostSendImageMessage` bound to this object (await to execute).
  chat_read() -> ChatRead
    # Build an awaitable :class:`ChatRead` bound to this object (await to execute).
  get_chat_by_id_v2() -> GetChatByIdV2
    # Build an awaitable :class:`GetChatByIdV2` bound to this object (await to execute).
  get_messages_v3(limit: int = 100, offset: int = 0) -> GetMessagesV3
    # Build an awaitable :class:`GetMessagesV3` bound to this object (await to execute).

cls ChatContext(AvitoObject)

cls ChatContextValue(AvitoObject)

cls ChatContextValueImages(AvitoObject)

cls ChatContextValueImagesMain(AvitoObject)

cls ChatLastMessage(AvitoObject)

cls ChatUsers(AvitoObject)

cls ChatUsersPublicUserProfile(AvitoObject)

cls ChatUsersPublicUserProfileAvatar(AvitoObject)
  # Фотография пользователя (аватар)

cls ChatUsersPublicUserProfileAvatarImages(AvitoObject)

cls Chats(AvitoObject)

cls MessageContent(AvitoObject)

cls MessageContentCall(AvitoObject)
  # Объект, описывающий звонок, для сообщения типа call

cls MessageContentItem(AvitoObject)
  # Объект, описывающий объявление, для сообщения типа item

cls MessageContentLink(AvitoObject)
  # Объект, описывающий ссылку, для сообщения типа link

cls MessageContentLinkPreview(AvitoObject)

cls MessageContentLocation(AvitoObject)
  # Объект, описывающий геометку, для сообщения типа location

cls MessageContentVoice(AvitoObject)
  # Объект, описывающий голосовое сообщение, для сообщения типа voice

cls MessageQuote(AvitoObject)
  # цитируемое сообщение

cls MessagesRoot(AvitoObject)

cls PayloadStruct(AvitoObject)

cls VoiceFiles(AvitoObject)
  # VoiceFiles response model.

cls WebhookMessage(AvitoObject)

cls AddBlacklistRequestBody(AvitoObject)
  # AddBlacklistRequestBody response model.

cls AddBlacklistRequestBodyUsers(AvitoObject)

cls AddBlacklistRequestBodyUsersContext(AvitoObject)

cls SendImageMessageRequestBody(AvitoObject)

cls SendMessageRequestBody(AvitoObject)

cls SendMessageRequestBodyMessage(AvitoObject)

cls WebhookSubscribeRequestBody(AvitoObject)

cls PostSendMessageResponse(AvitoObject)
  # PostSendMessageResponse response model.

cls PostSendMessageResponseContent(AvitoObject)
  # PostSendMessageResponseContent response model.

cls PostSendMessageMessage(AvitoObject)

cls PostSendImageMessageResponse(AvitoObject)
  # PostSendImageMessageResponse response model.

cls PostSendImageMessageResponseContent(AvitoObject)
  # PostSendImageMessageResponseContent response model.

cls DeleteMessageResponse(AvitoObject)
  # DeleteMessageResponse response model.

cls UploadImagesResponse(AvitoObject)
  # UploadImagesResponse response model.

cls GetSubscriptionsResponse(AvitoObject)
  # GetSubscriptionsResponse response model.

cls GetSubscriptionsResponseSubscriptions(AvitoObject)

cls PostBlacklistV2Users(AvitoObject)

cls PostBlacklistV2UsersContext(AvitoObject)

cls Messages(RootModel[list[MessagesRoot]])
  # Root wrapper for a top-level ``list[MessagesRoot]`` response.

```

## order_management.py
```
# Управление заказами — domain models (auto-generated from the Avito OpenAPI spec).


cls Action(AvitoObject)

cls BuyerInfo(AvitoObject)

cls CourierInfo(AvitoObject)

cls Delivery(AvitoObject)

cls Discount(AvitoObject)

cls GetDeliveryCourierConfirmationResponse(AvitoObject)

cls GetDeliveryCourierConfirmationResponseResult(AvitoObject)

cls GetDeliveryCourierConfirmationResponseResultDateOptions(AvitoObject)

cls GetDeliveryCourierConfirmationResponseResultDateOptionsTimeIntervals(AvitoObject)

cls Item(AvitoObject)

cls ItemPrices(AvitoObject)

cls Marking(AvitoObject)

cls Order(AvitoObject)

cls OrderAcceptReturnOrderRequest(AvitoObject)

cls OrderAcceptReturnOrderRequestRecipient(AvitoObject)

cls OrderApplyTransitionRequest(AvitoObject)

cls OrderApplyTransitionRequestParams(AvitoObject)

cls OrderApplyTransitionRequestParamsCnc(AvitoObject)

cls OrderCncSetDetailsRequest(AvitoObject)

cls OrderCncSetDetailsResponse(AvitoObject)
  # Ответ ручки подготовки заказа с самовывозом

cls OrderCheckConfirmationCodeRequest(AvitoObject)

cls OrderCheckConfirmationCodeResponse(AvitoObject)
  # Ответ ручки проверки кода подтверждения

cls OrderCheckConfirmationCodeResponseData(AvitoObject)
  # OrderCheckConfirmationCodeResponseData response model.

cls OrderPrices(AvitoObject)

cls OrderSetTrackingNumberRequest(AvitoObject)

cls OrderSetTrackingNumberResponse(AvitoObject)

cls OrdersInfo(AvitoObject)

cls OrdersLabelsRequest(AvitoObject)

cls OrdersLabelsResponse(AvitoObject)

cls ReturnPolicy(AvitoObject)

cls Schedules(AvitoObject)

cls SetCourierDeliveryRangeRequest(AvitoObject)

cls SetOrderMarkingRequest(AvitoObject)

cls SetOrderMarkingResponse(AvitoObject)

cls SetOrderMarkingResponseResults(AvitoObject)

cls TerminalInfo(AvitoObject)

cls AcceptReturnOrderRecipient(AvitoObject)

cls ApplyTransitionParams(AvitoObject)

cls ApplyTransitionParamsCnc(AvitoObject)

```

## promotion.py
```
# Продвижение — domain models (auto-generated from the Avito OpenAPI spec).


cls BbipForecastByItemV1(AvitoObject)

cls BbipForecastRequestByItemV1(AvitoObject)

cls BbipOrderByItemV1(AvitoObject)

cls BbipSuggestBudgetV1(AvitoObject)

cls BbipSuggestByItemV1(AvitoObject)

cls BbipSuggestDurationRangeV1(AvitoObject)

cls CommonError(AvitoObject)

cls CommonErrorDetails(AvitoObject)

cls ErrorByItemV1(AvitoObject)

cls GetBbipForecastByItemsV1Req(AvitoObject)

cls GetBbipForecastByItemsV1Resp(AvitoObject)

cls GetBbipSuggestsV1Req(AvitoObject)

cls GetBbipSuggestsV1Resp(AvitoObject)

cls GetOrderStatusV1Req(AvitoObject)

cls GetOrderStatusV1Resp(AvitoObject)

cls GetServicesByItemsV1Req(AvitoObject)

cls GetServicesByItemsV1Resp(AvitoObject)

cls ListOrdersByUserV1Req(AvitoObject)

cls ListOrdersByUserV1ReqPagination(AvitoObject)

cls ListOrdersByUserV1Resp(AvitoObject)

cls ListOrdersByUserV1RespPagination(AvitoObject)

cls OrderBbipForItemsV1Req(AvitoObject)

cls OrderBbipForItemsV1Resp(AvitoObject)

cls OrderBrief(AvitoObject)

cls OrderService(AvitoObject)

cls OrderStatusByItemV1(AvitoObject)

cls ServiceInfoV1(AvitoObject)

cls ServiceV1(AvitoObject)

cls ServicesByItemV1(AvitoObject)

cls ListOrdersByUserV1Pagination(AvitoObject)

cls GetDictOfServicesV1Resp(RootModel[list[ServiceInfoV1]])
  # Root wrapper for a top-level ``list[ServiceInfoV1]`` response.

```

## realty_reports.py
```
# Аналитика по недвижимости — domain models (auto-generated from the Avito OpenAPI spec).


cls MarketPriceCorrespondenceV1Response(AvitoObject)

cls CreateReportForClassifiedResponse(AvitoObject)
  # CreateReportForClassifiedResponse response model.

cls CreateReportForClassifiedResponseSuccess(AvitoObject)
  # CreateReportForClassifiedResponseSuccess response model.

cls CreateReportForClassifiedResponseSuccessErrors(AvitoObject)

cls CreateReportForClassifiedResponseSuccessSuccess(AvitoObject)

```

## reviews.py
```
# Рейтинги и отзывы — domain models (auto-generated from the Avito OpenAPI spec).


cls CreateAnswerRequestBody(AvitoObject)

cls CreateAnswerResponse(AvitoObject)

cls GetRatingInfoResponse(AvitoObject)

cls GetReviewsResponse(AvitoObject)

cls Rating(AvitoObject)

cls RejectReason(AvitoObject)

cls RemoveAnswerResponse(AvitoObject)

cls Review(AvitoObject)

cls ReviewExtraParams(AvitoObject)

cls ReviewAnswer(AvitoObject)

cls ReviewImage(AvitoObject)

cls ReviewImageSize(AvitoObject)

cls ReviewItem(AvitoObject)

cls ReviewSender(AvitoObject)

cls TooManyRequestsError(AvitoObject)
  # TooManyRequestsError response model.

```

## short_term_rental.py
```
# Краткосрочная аренда — domain models (auto-generated from the Avito OpenAPI spec).


cls AvitoBooking(AvitoObject)

cls BaseParams(AvitoObject)

cls BaseParamsDiscount(AvitoObject)

cls BaseParamsFees(AvitoObject)

cls BaseParamsFeesCleaning(AvitoObject)

cls BaseParamsFeesPets(AvitoObject)

cls BaseParamsInstant(AvitoObject)

cls BaseParamsRefund(AvitoObject)

cls ConflictedInterval(AvitoObject)

cls ConflictedIntervalInterval(AvitoObject)

cls DatesOverlapBookingError(AvitoObject)
  # DatesOverlapBookingError response model.

cls DatesOverlapBookingErrorError(AvitoObject)

cls ParamPriceItemRealty(AvitoObject)

cls ParamPricesRealty(AvitoObject)
  # Диапазоны дат и соответствующие им ценовые параметры

cls PostCalendarData(AvitoObject)

cls PostCalendarDataBookings(AvitoObject)

cls PostCalendarDataV2(AvitoObject)

cls PostCalendarDataV2Intervals(AvitoObject)

cls RealtyBooking(AvitoObject)

cls RealtyBookingContact(AvitoObject)

cls RealtyBookingSafeDeposit(AvitoObject)

cls PutBookingsInfoResponse(AvitoObject)

cls PutBookingsInfoBookings(AvitoObject)

cls GetRealtyBookingsResponse(AvitoObject)

cls PostRealtyPricesResponse(AvitoObject)

cls PutIntervalsResponse(AvitoObject)

cls PutIntervalsIntervals(AvitoObject)

cls PostBaseParamsDiscount(AvitoObject)

cls PostBaseParamsFees(AvitoObject)

cls PostBaseParamsFeesCleaning(AvitoObject)

cls PostBaseParamsFeesPets(AvitoObject)

cls PostBaseParamsInstant(AvitoObject)

cls PostBaseParamsRefund(AvitoObject)

```

## special_offers.py
```
# Рассылка скидок и спецпредложений в мессенджере (beta-version) — domain models (auto-generated from the Avito OpenAPI spec).


cls OpenApiAvailableResponseBody(AvitoObject)

cls OpenApiAvailableResponseBodyItems(AvitoObject)

cls OpenApiBadRequestError(AvitoObject)
  # OpenApiBadRequestError response model.

cls OpenApiForbiddenError(AvitoObject)
  # OpenApiForbiddenError response model.

cls OpenApiInternalError(AvitoObject)
  # OpenApiInternalError response model.

cls OpenApiMultiConfirmRequestBody(AvitoObject)

cls OpenApiMultiConfirmRequestBodyDispatches(AvitoObject)

cls OpenApiMultiCreateResponseBody(AvitoObject)

cls OpenApiMultiCreateResponseBodyCommon(AvitoObject)

cls OpenApiMultiCreateResponseBodyCommonOffers(AvitoObject)

cls OpenApiMultiCreateResponseBodyCommonOffersExpiresAt(AvitoObject)

cls OpenApiMultiCreateResponseBodyCommonTariff(AvitoObject)

cls OpenApiMultiCreateResponseBodyDispatches(AvitoObject)

cls OpenApiMultiCreateResponseBodyDispatchesDiscount(AvitoObject)

cls OpenApiMultiCreateResponseBodyDispatchesError(AvitoObject)

cls OpenApiMultiCreateResponseBodyDispatchesItem(AvitoObject)

cls OpenApiStatsRequestBody(AvitoObject)

cls OpenApiStatsResponseBody(AvitoObject)
  # OpenApiStatsResponseBody response model.

cls OpenApiStatsResponseBodyStats(AvitoObject)

cls OpenApiTariffInfoResponseBody(AvitoObject)

cls OpenApiTariffInfoResponseBodyTariffInfo(AvitoObject)

cls OpenApiUnauthorizedError(AvitoObject)
  # OpenApiUnauthorizedError response model.

cls OpenApiMultiConfirmDispatches(AvitoObject)

```

## stock_management.py
```
# Управление остатками — domain models (auto-generated from the Avito OpenAPI spec).


cls StockEditResult(AvitoObject)
  # StockEditResult response model.

cls StockEditResultStocks(AvitoObject)

cls StocksInfoResult(AvitoObject)
  # StocksInfoResult response model.

cls StocksInfoResultStocks(AvitoObject)

```

## tariff.py
```
# Тарифы — domain models (auto-generated from the Avito OpenAPI spec).


cls TariffContract(AvitoObject)

cls TariffContractPrice(AvitoObject)

cls TariffContractPackage(AvitoObject)

cls TariffContractPackageCategories(AvitoObject)

cls TariffContractPackagePriceConditions(AvitoObject)

cls TariffInfo(AvitoObject)
  # Информация по текущему и запланированному контракту

```

## trxpromo.py
```
# TrxPromo — domain models (auto-generated from the Avito OpenAPI spec).


cls ApplyReq(AvitoObject)
  # ApplyReq response model.

cls ApplyReqItems(AvitoObject)

cls ApplyResponse(AvitoObject)
  # ApplyResponse response model.

cls ApplyResponseSuccess(AvitoObject)
  # ApplyResponseSuccess response model.

cls ApplyResponseSuccessResult(AvitoObject)
  # ApplyResponseSuccessResult response model.

cls ApplyResponseSuccessResultValidCommissionRange(AvitoObject)

cls CancelResponse(AvitoObject)
  # CancelResponse response model.

cls CancelResponseSuccess(AvitoObject)
  # CancelResponseSuccess response model.

cls CancelResponseSuccessResult(AvitoObject)
  # CancelResponseSuccessResult response model.

cls CommissionResponse(AvitoObject)
  # CommissionResponse response model.

cls CommissionResponseSuccess(AvitoObject)
  # CommissionResponseSuccess response model.

cls CommissionResponseSuccessResult(AvitoObject)

cls CommissionResponseSuccessResultSettings(AvitoObject)

cls ApiV3error400(AvitoObject)
  # ApiV3error400 response model.

cls ApiV3error401(AvitoObject)
  # ApiV3error401 response model.

cls ApiV3error403(AvitoObject)
  # ApiV3error403 response model.

cls ApiV3error500(AvitoObject)
  # ApiV3error500 response model.

cls ApiTrxPromoOpenApiApplyItems(AvitoObject)

```

## user.py
```
# Информация о пользователе — domain models (auto-generated from the Avito OpenAPI spec).


cls Balance(AvitoObject)

cls RequestOperationsHistory(AvitoObject)

cls ResponseOperationsHistory(AvitoObject)
  # ResponseOperationsHistory response model.

cls ResponseOperationsHistoryResult(AvitoObject)
  # ResponseOperationsHistoryResult response model.

cls ResponseOperationsHistoryItem(AvitoObject)

cls UserInfoSelf(AvitoObject)

```

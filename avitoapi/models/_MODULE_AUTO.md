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


cls ErrorMessage(AvitoObject)
  # ErrorMessage — shared across domains.

cls GetTokenRequest(AvitoObject)
  # GetTokenRequest — shared across domains.

cls TooManyRequestsErrorError(AvitoObject)

```

## accounts_hierarchy.py
```
# Иерархия Аккаунтов — domain models (auto-generated from the Avito OpenAPI spec).


cls CompanyPhonesResult(AvitoObject)

cls CompanyPhonesResultResult(AvitoObject)

cls GetEmployeesResultRoot(AvitoObject)

cls LinkItems(AvitoObject)

cls ListItemsByEmployeeIdBody(AvitoObject)

cls ListItemsByEmployeeIdResult(AvitoObject)

cls OpenApiError(AvitoObject)

cls OpenApiErrorError(AvitoObject)

cls CheckAhUserV1Response(AvitoObject)

cls CheckAhUserV2Response(AvitoObject)

cls GetAhInfoV1Response(AvitoObject)

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

cls AccountManager(AvitoObject)

cls Advertiser(AvitoObject)

cls AdvertiserFilter(AvitoObject)

cls Campaign(AvitoObject)

cls CampaignStatistic(AvitoObject)

cls CampaignsFilter(AvitoObject)

cls Contract(AvitoObject)

cls ContractForChildAccount(AvitoObject)

cls ContractsFilter(AvitoObject)

cls CreateGroupActivitySchedule(AvitoObject)

cls Creative(AvitoObject)

cls CreativeStatistic(AvitoObject)

cls CreativesFilter(AvitoObject)

cls CreteIntermediaryIn(AvitoObject)

cls DateRange(AvitoObject)

cls DetailedError(AvitoObject)

cls DetailedErrorItem(AvitoObject)

cls Disclaimer(AvitoObject)

cls DisclaimerInput(AvitoObject)

cls EmptyResponse(AvitoObject)

cls EnumObject(AvitoObject)

cls FrequencyRule(AvitoObject)

cls Group(AvitoObject)

cls GroupActivitySchedule(AvitoObject)

cls GroupReferenceData(AvitoObject)

cls GroupStatistic(AvitoObject)

cls GroupsFilter(AvitoObject)

cls IdNameObject(AvitoObject)

cls KktuItem(AvitoObject)

cls LegalInfo(AvitoObject)

cls ObjectSize(AvitoObject)

cls ShortAccount(AvitoObject)

cls ShortAccountWithBalance(AvitoObject)

cls ShortAccountWithContract(AvitoObject)

cls StatsData(AvitoObject)

cls StringIdNameObject(AvitoObject)

cls TemplateData(AvitoObject)

cls TemplateField(AvitoObject)

cls ThresholdItem(AvitoObject)

cls User(AvitoObject)

cls V1AddUserIn(AvitoObject)

cls V1ChangeBudgetIn(AvitoObject)

cls V1ChangePriceIn(AvitoObject)

cls V1CopyCampaignGroup(AvitoObject)

cls V1CopyCampaignIn(AvitoObject)

cls V1CopyCampaignOut(AvitoObject)

cls V1CopyCreativeIn(AvitoObject)

cls V1CopyCreativeOut(AvitoObject)

cls V1CopyGroupIn(AvitoObject)

cls V1CopyGroupOut(AvitoObject)

cls V1CreateAccountIn(AvitoObject)

cls V1CreateAccountInContact(AvitoObject)

cls V1CreateAccountOut(AvitoObject)

cls V1CreateAdvertiserIn(AvitoObject)

cls V1CreateAdvertiserOut(AvitoObject)

cls V1CreateCampaignIn(AvitoObject)

cls V1CreateCampaignOut(AvitoObject)

cls V1CreateContractIn(AvitoObject)

cls V1CreateContractOut(AvitoObject)

cls V1CreateGroupIn(AvitoObject)

cls V1CreateGroupOut(AvitoObject)

cls V1CreateNonPayerAccountIn(AvitoObject)

cls V1CreateNonPayerAccountOut(AvitoObject)

cls V1DeleteCampaignsIn(AvitoObject)

cls V1DeleteCreativesIn(AvitoObject)

cls V1DeleteGroupsIn(AvitoObject)

cls V1GetAccountBalanceByIdOut(AvitoObject)

cls V1GetAccountByIdOut(AvitoObject)
  v1_get_account_by_id() -> V1GetAccountById
    # Build an awaitable :class:`V1GetAccountById` bound to this object (await to execute).
  v1_create_account(contact: V1CreateAccountContact, inn: str, legal_address: str, legal_type: LegalType, long_name: str, ogrn: str, short_name: str, actual_address: str? = None, kpp: str? = None) -> V1CreateAccount
    # Build an awaitable :class:`V1CreateAccount` bound to this object (await to execute).
  v1_add_user(role: UserRole, user_id: int) -> V1AddUser
    # Build an awaitable :class:`V1AddUser` bound to this object (await to execute).
  v1_get_advertisers_list(filter: AdvertiserFilter, limit: int, page: int) -> V1GetAdvertisersList
    # Build an awaitable :class:`V1GetAdvertisersList` bound to this object (await to execute).
  v1_get_account_balance_by_id() -> V1GetAccountBalanceById
    # Build an awaitable :class:`V1GetAccountBalanceById` bound to this object (await to execute).
  v1_transfer_bonus(account_id_to: int, amount: int) -> V1TransferBonus
    # Build an awaitable :class:`V1TransferBonus` bound to this object (await to execute).
  v1_get_campaigns_list(filter: CampaignsFilter, limit: int, page: int) -> V1GetCampaignsList
    # Build an awaitable :class:`V1GetCampaignsList` bound to this object (await to execute).
  v1_get_child_accounts_list() -> V1GetChildAccountsList
    # Build an awaitable :class:`V1GetChildAccountsList` bound to this object (await to execute).
  v1_get_child_accounts_with_balances_list() -> V1GetChildAccountsWithBalancesList
    # Build an awaitable :class:`V1GetChildAccountsWithBalancesList` bound to this object (await to execute).
  v1_get_contracts_list(filter: ContractsFilter, limit: int, page: int) -> V1GetContractsList
    # Build an awaitable :class:`V1GetContractsList` bound to this object (await to execute).
  v1_create_advertiser(inn: str, legal_address: str, legal_role: LegalRole, legal_type: LegalType, long_name: str, ogrn: str, short_name: str, actual_address: str? = None, kpp: str? = None) -> V1CreateAdvertiser
    # Build an awaitable :class:`V1CreateAdvertiser` bound to this object (await to execute).
  v1_create_contract(advertiser_id: int, description: ContractCounterpartyType, type_: ContractType, cid: str? = None, date_: date? = None, intermediary: CreteIntermediaryIn? = None, is_funds_allocation_to_principal: bool? = None, is_reporting_required: bool? = None, number: str? = None, object: ContractAction? = None, parent_id: int? = None, subject: ContractSubject? = None) -> V1CreateContract
    # Build an awaitable :class:`V1CreateContract` bound to this object (await to execute).
  v1_create_non_payer_account(is_self_advertising_enabled: bool, short_name: str) -> V1CreateNonPayerAccount
    # Build an awaitable :class:`V1CreateNonPayerAccount` bound to this object (await to execute).
  v1_get_creatives_list(filter: CreativesFilter, limit: int, page: int) -> V1GetCreativesList
    # Build an awaitable :class:`V1GetCreativesList` bound to this object (await to execute).
  v1_delete_user() -> V1DeleteUser
    # Build an awaitable :class:`V1DeleteUser` bound to this object (await to execute).
  v1_transfer_funds(account_id_to: int, amount: int) -> V1TransferFunds
    # Build an awaitable :class:`V1TransferFunds` bound to this object (await to execute).
  v1_get_groups_list(filter: GroupsFilter, limit: int, page: int) -> V1GetGroupsList
    # Build an awaitable :class:`V1GetGroupsList` bound to this object (await to execute).
  v1_set_user_role(role: UserRole, user_id: int) -> V1SetUserRole
    # Build an awaitable :class:`V1SetUserRole` bound to this object (await to execute).
  v1_get_users_list_by_account() -> V1GetUsersListByAccount
    # Build an awaitable :class:`V1GetUsersListByAccount` bound to this object (await to execute).

cls V1GetAdvertisersListIn(AvitoObject)

cls V1GetAdvertisersListOut(AvitoObject)

cls V1GetCampaignByIdWithFieldsOut(AvitoObject)

cls V1GetCampaignStatisticIn(AvitoObject)

cls V1GetCampaignStatisticOut(AvitoObject)

cls V1GetCampaignsListIn(AvitoObject)

cls V1GetCampaignsListOut(AvitoObject)

cls V1GetChildAccountsListOut(AvitoObject)

cls V1GetChildAccountsWithBalancesListOut(AvitoObject)

cls V1GetContractsListIn(AvitoObject)

cls V1GetContractsListOut(AvitoObject)

cls V1GetCreativesListIn(AvitoObject)

cls V1GetCreativesListOut(AvitoObject)

cls V1GetCreativesStatisticIn(AvitoObject)

cls V1GetCreativesStatisticOut(AvitoObject)

cls V1GetGroupReferenceDataOut(AvitoObject)

cls V1GetGroupsListIn(AvitoObject)

cls V1GetGroupsListOut(AvitoObject)

cls V1GetGroupsStatisticIn(AvitoObject)

cls V1GetGroupsStatisticOut(AvitoObject)

cls V1GetHtmlOut(AvitoObject)

cls V1GetImageOut(AvitoObject)

cls V1GetLegalAttachmentsOut(AvitoObject)

cls V1GetUsersListByAccountOut(AvitoObject)

cls V1GetVideoOut(AvitoObject)

cls V1LaunchCampaignsIn(AvitoObject)

cls V1LaunchGroupIn(AvitoObject)

cls V1PauseCampaignsIn(AvitoObject)

cls V1PauseCreativesIn(AvitoObject)

cls V1PauseGroupsIn(AvitoObject)

cls V1ReferenceDataCreateCreativeOut(AvitoObject)

cls V1SetUserRoleIn(AvitoObject)

cls V1StopCampaignsIn(AvitoObject)

cls V1TransferBonusIn(AvitoObject)

cls V1TransferFundsIn(AvitoObject)

cls V1UnpauseCampaignsIn(AvitoObject)

cls V1UnpauseCreativesIn(AvitoObject)

cls V1UnpauseGroupsIn(AvitoObject)

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


cls Error(AvitoObject)

cls TooManyRequestsError(AvitoObject)

cls GetUserBidsResponse(AvitoObject)

cls GetUserBidsResponseItems(AvitoObject)

cls GetUserBidsResponseItemsAvailablePrices(AvitoObject)

cls SaveItemBidsItems(AvitoObject)

```

## auth.py
```
# Авторизация — domain models (auto-generated from the Avito OpenAPI spec).


cls GetTokenOAuthRequest(AvitoObject)

cls RefreshRequest(AvitoObject)

cls GetAccessTokenResponse(AvitoObject)

cls GetAccessTokenAuthorizationCodeResponse(AvitoObject)

cls RefreshAccessTokenAuthorizationCodeResponse(AvitoObject)

```

## autoload.py
```
# Автозагрузка — domain models (auto-generated from the Avito OpenAPI spec).


cls ApFieldsNodeAlert(AvitoObject)

cls ApiCategoryNode(AvitoObject)

cls ApiCategoryTreeOut(AvitoObject)

cls ApiDependency(AvitoObject)

cls ApiDependencyPair(AvitoObject)

cls ApiField(AvitoObject)

cls ApiFieldContent(AvitoObject)

cls ApiFieldsNode(AvitoObject)

cls ApiFieldsOut(AvitoObject)

cls CategoryNode(AvitoObject)

cls CategoryTreeOut(AvitoObject)

cls ChildApiField(AvitoObject)

cls ErrorAutoload(AvitoObject)

cls ErrorAutoloadError(AvitoObject)

cls ExportScheduleRoot(AvitoObject)

cls FeedsDataRoot(AvitoObject)

cls FieldErrorV2(AvitoObject)

cls FieldValue(AvitoObject)

cls FieldValueRange(AvitoObject)

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

cls ReportAutoloadAdsStatusesGeneral(AvitoObject)

cls ReportAutoloadAdsStatusesProcessing(AvitoObject)

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

cls ConflictError(AvitoObject)

cls CreateCampaignBadRequestError(AvitoObject)

cls CreateCampaignBadRequestErrorError(AvitoObject)

cls CreateCampaignBadRequestErrorErrorFieldErrors(AvitoObject)

cls CreateCampaignConflictError(AvitoObject)

cls CreateCampaignRequestBody(AvitoObject)

cls EditCampaignBadRequestError(AvitoObject)

cls EditCampaignBadRequestErrorError(AvitoObject)

cls EditCampaignBadRequestErrorErrorFieldErrors(AvitoObject)

cls EditCampaignConflictError(AvitoObject)

cls EditCampaignRequestBody(AvitoObject)

cls GetBudgetBadRequestError(AvitoObject)

cls GetBudgetBadRequestErrorError(AvitoObject)

cls GetBudgetBadRequestErrorErrorFieldErrors(AvitoObject)

cls GetBudgetConflictError(AvitoObject)

cls GetBudgetRequestBody(AvitoObject)

cls GetCampaignInfoBadRequestError(AvitoObject)

cls GetCampaignInfoBadRequestErrorError(AvitoObject)

cls GetCampaignInfoBadRequestErrorErrorFieldErrors(AvitoObject)

cls GetCampaignInfoForecastResult(AvitoObject)

cls GetCampaignInfoForecastResultCalls(AvitoObject)

cls GetCampaignInfoForecastResultViews(AvitoObject)

cls GetCampaignInfoRequestBody(AvitoObject)

cls GetCampaignsBadRequestError(AvitoObject)

cls GetCampaignsBadRequestErrorError(AvitoObject)

cls GetCampaignsBadRequestErrorErrorFieldErrors(AvitoObject)

cls GetCampaignsBadRequestErrorErrorFieldErrorsOrderBy(AvitoObject)

cls GetCampaignsRequestBody(AvitoObject)

cls GetCampaignsRequestBodyFilter(AvitoObject)

cls GetCampaignsRequestBodyFilterByUpdateTime(AvitoObject)

cls GetCampaignsRequestBodyOrderBy(AvitoObject)

cls GetStatRequestBody(AvitoObject)

cls GetStatRequestError(AvitoObject)

cls GetStatRequestErrorError(AvitoObject)

cls GetStatRequestErrorErrorFieldErrors(AvitoObject)

cls StatRoot(AvitoObject)

cls StatRootCallsForecast(AvitoObject)

cls StatRootViewsForecast(AvitoObject)

cls StopCampaignBadRequestError(AvitoObject)

cls StopCampaignBadRequestErrorError(AvitoObject)

cls StopCampaignBadRequestErrorErrorFieldErrors(AvitoObject)

cls StopCampaignRequestBody(AvitoObject)

cls AuthError(AvitoObject)

cls AutostrategyAuthError(AvitoObject)

cls AutostrategyAuthErrorError(AvitoObject)

cls AutostrategyServiceError(AvitoObject)

cls AutostrategyServiceErrorError(AvitoObject)

cls NotFoundError(AvitoObject)

cls ServiceError(AvitoObject)

cls GetAutostrategyBudgetResponse(AvitoObject)

cls CreateAutostrategyCampaignResponse(AvitoObject)

cls EditAutostrategyCampaignResponse(AvitoObject)

cls GetAutostrategyCampaignInfoResponse(AvitoObject)

cls GetAutostrategyCampaignInfoResponseItems(AvitoObject)

cls StopAutostrategyCampaignResponse(AvitoObject)

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

cls CatalogsResolveResponseDataAutoteka(AvitoObject)

cls CrashesHistoryAutoteka(AvitoObject)

cls CrashesHistoryAutotekaDamageTypes(AvitoObject)

cls CreateEptsResponseDataAutoteka(AvitoObject)

cls CreateReportResponseBodyAutoteka(AvitoObject)

cls CreateReportResponseDataAutoteka(AvitoObject)

cls CreateScoringResponseBodyAutoteka(AvitoObject)

cls CreateScoringResponseDataAutoteka(AvitoObject)

cls CreateSpecificationResponseBodyAutoteka(AvitoObject)

cls CreateSpecificationResponseDataAutoteka(AvitoObject)

cls CreateTeaserResponseBodyAutoteka(AvitoObject)

cls CreateTeaserResponseDataAutoteka(AvitoObject)

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

cls GetActivePackageResponseDataAutoteka(AvitoObject)

cls GetEptsResult(AvitoObject)

cls GetPreviewResponseBodyAutoteka(AvitoObject)
  get_preview() -> GetPreview
    # Build an awaitable :class:`GetPreview` bound to this object (await to execute).

cls GetPreviewResponseDataAutoteka(AvitoObject)

cls GetReport(AvitoObject)

cls GetReportAsync(AvitoObject)
  get_report2() -> GetReport2
    # Build an awaitable :class:`GetReport2` bound to this object (await to execute).

cls GetReportResult(AvitoObject)

cls GetReportResultAsync(AvitoObject)

cls GetReportsListResponseDataAutoteka(AvitoObject)

cls GetScoring(AvitoObject)
  scoring_get_by_id() -> ScoringGetById
    # Build an awaitable :class:`ScoringGetById` bound to this object (await to execute).

cls GetScoringResult(AvitoObject)

cls GetSpecificationResponseBodyAutoteka(AvitoObject)
  specification_get_by_id() -> SpecificationGetById
    # Build an awaitable :class:`SpecificationGetById` bound to this object (await to execute).

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

cls PreviewIdOnlyAutoteka(AvitoObject)

cls PriceStatAutoteka(AvitoObject)

cls PriceStatForNewCarsAutoteka(AvitoObject)

cls PriceStatForNewCarsAutotekaItems(AvitoObject)

cls PriceStatForNewCarsAutotekaItemsPrices(AvitoObject)

cls PriceStatForNewCarsAutotekaPrice(AvitoObject)

cls PriceStatReportAutoteka(AvitoObject)

cls PriceStatReportAutotekaPrice(AvitoObject)

cls PtsData(AvitoObject)

cls PtsDataPts(AvitoObject)

cls PtsDataSts(AvitoObject)

cls RecallItem(AvitoObject)

cls RecallItemCompleteInfo(AvitoObject)

cls RecapAutoteka(AvitoObject)

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

cls RequestMonitoringAddVinBucket(AvitoObject)

cls RequestMonitoringRemoveVinBucket(AvitoObject)

cls RequestPreviewByItemIdAutoteka(AvitoObject)

cls RequestPreviewResponseBodyAutoteka(AvitoObject)

cls RequestPreviewResponseDataAutoteka(AvitoObject)

cls RequestReportByPlateNumberAutoteka(AvitoObject)

cls RequestReportByPreviewIdAutoteka(AvitoObject)

cls RequestReportByVehicleIdAutoteka(AvitoObject)

cls RequestTeaserByVehicleIdAutoteka(AvitoObject)

cls RequestValuationBySpecificationResolve(AvitoObject)

cls RequestValuationBySpecificationResolveLocation(AvitoObject)

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

cls ResponseGetLeadsPagination(AvitoObject)

cls ResponseGetLeadsResult(AvitoObject)

cls ResponseGetLeadsResultPayload(AvitoObject)

cls ResponseGetLeadsResultPayloadExtraPayload(AvitoObject)

cls ResponseGetLeadsResultPayloadExtraPayloadPriceAnalytics(AvitoObject)

cls ResponseGetLeadsResultPayloadExtraPayloadTeaser(AvitoObject)

cls ResponseGetLeadsResultPayloadTriggerPayload(AvitoObject)

cls ResponseGetLeadsResultPayloadTriggerPayloadLastEvents(AvitoObject)

cls ResponseMonitoringAddVinBucket(AvitoObject)

cls ResponseMonitoringAddVinBucketResult(AvitoObject)

cls ResponseMonitoringAddVinBucketResultInvalidVehicles(AvitoObject)

cls ResponseMonitoringDeleteVinBucket(AvitoObject)

cls ResponseMonitoringDeleteVinBucketResult(AvitoObject)

cls ResponseMonitoringGetRegAction(AvitoObject)

cls ResponseMonitoringGetRegActions(AvitoObject)

cls ResponseMonitoringGetRegActionsPagination(AvitoObject)

cls ResponseMonitoringRemoveVinBucket(AvitoObject)

cls ResponseMonitoringRemoveVinBucketResult(AvitoObject)

cls ResponseMonitoringRemoveVinBucketResultInvalidVehicles(AvitoObject)

cls RestrictionsAutoteka(AvitoObject)

cls RestrictionsAutotekaPledge(AvitoObject)

cls RestrictionsAutotekaPledgeHistory(AvitoObject)

cls RestrictionsAutotekaPledgeHistoryPledges(AvitoObject)

cls RestrictionsAutotekaPledgePledgeAdditionalData(AvitoObject)

cls RestrictionsAutotekaPledgePledgeAdditionalDataData(AvitoObject)

cls RestrictionsAutotekaRegistration(AvitoObject)

cls RestrictionsAutotekaRegistrationAdditionalInfo(AvitoObject)

cls RestrictionsAutotekaStealing(AvitoObject)

cls RestrictionsAutotekaStealingAdditionalInfo(AvitoObject)

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

cls ScoringTechSpecificationBodyNumber(AvitoObject)

cls ScoringTechSpecificationBrand(AvitoObject)

cls ScoringTechSpecificationChasisNumber(AvitoObject)

cls ScoringTechSpecificationColor(AvitoObject)

cls ScoringTechSpecificationEngineNumber(AvitoObject)

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

cls ValuationBySpecificationResultAutoteka(AvitoObject)

cls VehicleSpecifications(AvitoObject)

cls VehicleSpecificationsParam(AvitoObject)

cls ForbiddenError(AvitoObject)

cls InternalError(AvitoObject)

cls NotFoundError(AvitoObject)

cls TooManyRequestsError(AvitoObject)

cls ValidatingError(AvitoObject)

cls CatalogsResolveFieldsValueIds(AvitoObject)

cls ValuationBySpecificationLocation(AvitoObject)

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

cls GetAccessTokenResponse(AvitoObject)

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

cls ErrorResponse(AvitoObject)

cls ErrorResult(AvitoObject)

cls InviteId(AvitoObject)

cls TargetTaskId(AvitoObject)

cls AgencyBalanceResponse(AvitoObject)

cls AgencyBalanceResponseResult(AvitoObject)

cls AgencyTransactionsResponse(AvitoObject)

cls AgencyTransactionsResponseResult(AvitoObject)

cls AgencyTransactionResponse(AvitoObject)

cls AgencyTransactionResponseResult(AvitoObject)

cls AgencyClientsResponse(AvitoObject)

cls AgencyClientsResponseResult(AvitoObject)

cls AgencyClientsResponseResultClients(AvitoObject)

cls AgencyClientsResponseResultClientsAdvance(AvitoObject)

cls AgencyClientsResponseResultClientsBalance(AvitoObject)

cls AgencyClientsResponseResultClientsStatistics(AvitoObject)

cls AgencyClientsResponseResultClientsSubscription(AvitoObject)

cls AgencyClientsExtra(AvitoObject)

cls AgencyClientsTargetCreateResponse(AvitoObject)

cls AgencyClientsTargetResultResponse(AvitoObject)

cls AgencyClientsTargetResultResponseResult(AvitoObject)

cls AgencyClientsTargetResultResponseResultItems(AvitoObject)

cls AgencyClientsTargetResultResponseResultItemsResults(AvitoObject)

cls AgencyFinancesBalanceResponse(AvitoObject)

cls AgencyFinancesTransactionsHistoryResponse(AvitoObject)

cls AgencyFinancesTransactionsHistoryResponseItems(AvitoObject)

cls AgencyUsersInviteSendResponse(AvitoObject)

cls AgencyUsersInviteStatusResponse(AvitoObject)

cls AgencyUsersInviteStatusResponseResult(AvitoObject)

cls AgencyUsersVerificationStatusResponse(AvitoObject)

cls AgencyUsersVerificationStatusResponseResult(AvitoObject)

cls StatsAccountsItemsResponse(AvitoObject)

cls StatsAccountsItemsResponseResult(AvitoObject)

cls StatsAccountsItemsResponseResultGroupings(AvitoObject)

cls StatsAccountsItemsResponseResultGroupingsMetrics(AvitoObject)

cls StatsAccountsItemsFilter(AvitoObject)

cls StatsAccountsItemsSort(AvitoObject)

cls StatsAccountsSpendingsResponse(AvitoObject)

cls StatsAccountsSpendingsResponseResult(AvitoObject)

cls StatsAccountsSpendingsResponseResultGroupings(AvitoObject)

cls StatsAccountsSpendingsResponseResultGroupingsSpendings(AvitoObject)

cls StatsAccountsSpendingsResponseResultGroupingsSpendingsServices(AvitoObject)

cls StatsAccountsSpendingsFilter(AvitoObject)

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

cls GetCallsResponse(AvitoObject)

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

cls CpaErrorChatResult(AvitoObject)

cls CreateComplaint(AvitoObject)

cls CreateComplaintV4In(AvitoObject)

cls CreateComplaintV4Out(AvitoObject)

cls Error(AvitoObject)

cls ErrorPayload(AvitoObject)

cls InternalError(AvitoObject)

cls InternalErrorResult(AvitoObject)

cls OpenApiChatsByTimeFilters(AvitoObject)

cls OpenApiChatsByTimeIn(AvitoObject)

cls OpenApiChatsByTimeMetaFilters(AvitoObject)

cls OpenApiChatsByTimeOut(AvitoObject)

cls OpenApiChatsByTimeV2In(AvitoObject)

cls OpenApiChatsByTimeV2Out(AvitoObject)

cls OpenApiPhonesInfoFromChatsIn(AvitoObject)

cls OpenApiPhonesInfoFromChatsOut(AvitoObject)

cls OpenApiChat(AvitoObject)

cls OpenApiChatByActionIdIn(AvitoObject)

cls OpenApiChatByActionIdOut(AvitoObject)

cls OpenApiChatsBuyer(AvitoObject)

cls OpenApiChatsComposition(AvitoObject)

cls OpenApiChatsItem(AvitoObject)

cls OpenApiError(AvitoObject)

cls OpenApiErrorResult(AvitoObject)

cls OpenApiErrorResultError(AvitoObject)

cls OpenApiErrorResultErrorPayload(AvitoObject)

cls OpenApiErrorOld(AvitoObject)

cls OpenApiErrorOldResult(AvitoObject)

cls NotFoundError(AvitoObject)

cls ServiceError(AvitoObject)

cls TooManyRequestsError(AvitoObject)

cls ValidatingError(AvitoObject)

cls ValidatingErrorError(AvitoObject)

cls ChatByActionIdResponse(AvitoObject)

cls ChatsByTimeResponse(AvitoObject)

cls PostCreateComplaintResponse(AvitoObject)

cls CreateComplaintByActionIdResponse(AvitoObject)

cls PhonesInfoFromChatsResponse(AvitoObject)

cls BalanceInfoV2Response(AvitoObject)

cls GetCallByIdV2Response(AvitoObject)

cls GetCallsByTimeV2Response(AvitoObject)

cls ChatsByTime2Response(AvitoObject)

cls BalanceInfoV3Response(AvitoObject)

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

cls Error(AvitoObject)

cls GetBidsOut(AvitoObject)

cls GetPromotionsByItemIdsIn(AvitoObject)

cls GetPromotionsByItemIdsOut(AvitoObject)

cls GetPromotionsByItemIdsOutItems(AvitoObject)

cls Manual(AvitoObject)

cls ManualPromotion(AvitoObject)

cls TooManyRequestsError(AvitoObject)

cls RemovePromotion2Response(AvitoObject)

```

## delivery.py
```
# Доставка — domain models (auto-generated from the Avito OpenAPI spec).


cls AddTariffReply(AvitoObject)

cls AddTariffReplyData(AvitoObject)

cls AddTariffRequest(AvitoObject)

cls AddTariffRequestV2(AvitoObject)

cls AddTaskReply(AvitoObject)

cls AddTaskReplyData(AvitoObject)

cls AddTerminalsReply(AvitoObject)

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

cls AnnouncementsSuccessResponseData(AvitoObject)

cls AnnouncementsTrackAnnouncementRequest(AvitoObject)

cls Area(AvitoObject)

cls AreasCustomScheduleTaskResult(AvitoObject)

cls AreasTaskResult(AvitoObject)

cls Breadcrumb(AvitoObject)

cls CancelSandboxParcelOptions(AvitoObject)

cls CancelSandboxParcelReply(AvitoObject)

cls CancelSandboxParcelReplyData(AvitoObject)

cls CancelSandxobParcelRequest(AvitoObject)

cls ChangeParcelReply(AvitoObject)

cls ChangeParcelReplyData(AvitoObject)

cls ChangeParcelRequest(AvitoObject)

cls ChangeParcelRequestApplication(AvitoObject)

cls ChangeParcelRequestOptions(AvitoObject)

cls ChangeParcelResultReply(AvitoObject)

cls ChangeParcelResultRequest(AvitoObject)

cls ChangeParcelResultRequestOptions(AvitoObject)

cls ChangeParcelsApplication(AvitoObject)

cls ChangeParcelsClient(AvitoObject)

cls ChangeParcelsData(AvitoObject)

cls ChangeParcelsRequest(AvitoObject)

cls ChangeParcelsResponse(AvitoObject)

cls ChangeParcelsTerminal(AvitoObject)

cls CheckConfirmationCodeReply(AvitoObject)

cls CheckConfirmationCodeReplyData(AvitoObject)

cls CheckConfirmationCodeRequest(AvitoObject)

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

cls CreateParcelItem(AvitoObject)

cls CreateParcelItemBreadcrumb(AvitoObject)

cls CreateParcelItemDimensions(AvitoObject)

cls CreateParcelItemImagesUrls(AvitoObject)

cls CreateParcelItemWeight(AvitoObject)

cls CreateParcelOptions(AvitoObject)

cls CreateParcelOptionsReturn(AvitoObject)

cls CreateParcelOptionsReturnPolicy(AvitoObject)

cls CreateParcelOptionsReturnPolicyAfter(AvitoObject)

cls CreateParcelPackage(AvitoObject)

cls CreateParcelPayment(AvitoObject)

cls CreateParcelPaymentDelivery(AvitoObject)

cls CreateParcelPaymentItems(AvitoObject)

cls CreateParcelReply(AvitoObject)

cls CreateParcelReplyData(AvitoObject)

cls CreateParcelRequest(AvitoObject)

cls CreateParcelResponse(AvitoObject)

cls CreateParcelUserDeliveryTerminal(AvitoObject)

cls CreateSandboxParcelItem(AvitoObject)

cls CreateSandboxParcelItemDimensions(AvitoObject)

cls CreateSandboxParcelItemWeight(AvitoObject)

cls CreateSandboxParcelOptions(AvitoObject)

cls CreateSandboxParcelOptionsXDelivery(AvitoObject)

cls CreateSandboxParcelReceiverDelivery(AvitoObject)

cls CreateSandboxParcelUserDelivery(AvitoObject)

cls CreateSandboxParcelV2(AvitoObject)

cls CreateSandboxParcelV2Receiver(AvitoObject)

cls CreateSandboxParcelV2Sender(AvitoObject)

cls CreateSandboxV2Options(AvitoObject)

cls DeliveryCoordinates(AvitoObject)

cls DeliveryDateInterval(AvitoObject)

cls DeliveryParams(AvitoObject)

cls DeliveryTerms(AvitoObject)

cls DeliveryError4Xx(AvitoObject)

cls DeliveryIntervalInDate(AvitoObject)

cls DeliverySetOrderPropertiesReply(AvitoObject)

cls DeliverySetOrderPropertiesReplyData(AvitoObject)

cls DeliverySetOrderPropertiesRequest(AvitoObject)

cls DeliverySetOrderRealAddresseReply(AvitoObject)

cls DeliverySetOrderRealAddresseReplyData(AvitoObject)

cls DeliverySetRealAddressRequest(AvitoObject)

cls DeliverySetRealAddressRequestAddress(AvitoObject)

cls DeliverySetStatusDetails(AvitoObject)

cls DeliverySetStatusReply(AvitoObject)

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

cls GetChangeParcelInfoReplyData(AvitoObject)

cls GetChangeParcelInfoReplyDataReceiver(AvitoObject)

cls GetChangeParcelInfoRequest(AvitoObject)

cls GetInfoByOrderIdErrorReply(AvitoObject)

cls GetRegisteredParcelIdReply(AvitoObject)

cls GetRegisteredParcelIdReplyData(AvitoObject)

cls GetRegisteredParcelIdRequest(AvitoObject)

cls GetSandboxParcelInfoDimensions(AvitoObject)

cls GetSandboxParcelInfoParcelHistory(AvitoObject)

cls GetSandboxParcelInfoReply(AvitoObject)

cls GetSandboxParcelInfoReplyData(AvitoObject)

cls GetSandboxParcelInfoReplyDataReceiver(AvitoObject)

cls GetSandboxParcelInfoReplyDataSender(AvitoObject)

cls GetSandboxParcelInfoRequest(AvitoObject)

cls GetSandboxParcelInfoTerminals(AvitoObject)

cls GetTariffTaskReply(AvitoObject)

cls GetTariffTaskReplyData(AvitoObject)

cls GetTaskData(AvitoObject)

cls GetTaskReply(AvitoObject)
  get_task() -> GetTask
    # Build an awaitable :class:`GetTask` bound to this object (await to execute).

cls GetTerminalsTaskReply(AvitoObject)

cls GetTerminalsTaskReplyData(AvitoObject)

cls ImageUrls(AvitoObject)

cls Restriction(AvitoObject)

cls SandboxCancelAnnouncementOptions(AvitoObject)

cls SandboxCancelAnnouncementReply(AvitoObject)

cls SandboxCancelAnnouncementReplyData(AvitoObject)

cls SandboxCancelAnnouncementRequest(AvitoObject)

cls SandboxCreateAnnouncementDeliveryPoint(AvitoObject)

cls SandboxCreateAnnouncementOptions(AvitoObject)

cls SandboxCreateAnnouncementPackage(AvitoObject)

cls SandboxCreateAnnouncementParticipant(AvitoObject)

cls SandboxCreateAnnouncementParticipantDelivery(AvitoObject)

cls SandboxCreateAnnouncementReply(AvitoObject)

cls SandboxCreateAnnouncementReplyData(AvitoObject)

cls SandboxCreateAnnouncementRequest(AvitoObject)

cls SandboxGetAnnouncementEventReply(AvitoObject)

cls SandboxGetAnnouncementEventReplyData(AvitoObject)

cls SandboxGetAnnouncementEventRequest(AvitoObject)

cls Schedule(AvitoObject)

cls SetStatusErrorReply(AvitoObject)

cls SetStatusReply(AvitoObject)

cls SetStatusRequest(AvitoObject)

cls SortingCenterGet(AvitoObject)

cls SortingCenterGetData(AvitoObject)

cls SortingCenterId(AvitoObject)

cls SortingCenterPost(AvitoObject)

cls SortingCentersTagsTaskResult(AvitoObject)

cls SortingCentersTaskResult(AvitoObject)

cls TaggedSortingCenter(AvitoObject)

cls TariffTaskResult(AvitoObject)

cls TariffZone(AvitoObject)

cls Terminal(AvitoObject)

cls TerminalsTaskResult(AvitoObject)

cls TermsZone(AvitoObject)

cls UpdateTermsReply(AvitoObject)

cls UpdateTermsReplyData(AvitoObject)

cls ValuesByDimension(AvitoObject)

cls ValuesByDimensionValues(AvitoObject)

cls ValuesByPaidWeight(AvitoObject)

cls ValuesByPaidWeightValues(AvitoObject)

cls ValuesByWeight(AvitoObject)

cls ValuesByWeightValues(AvitoObject)

cls Zone(AvitoObject)

cls CancelParcelReply(AvitoObject)

cls CancelParcelReplyData(AvitoObject)

cls CancelParcelRequest(AvitoObject)

cls CustomAreaScheduleRequestObject(AvitoObject)

cls CutoffAndSchedule(AvitoObject)

cls CutoffAndScheduleCutoff(AvitoObject)

cls ProhibitOrderAcceptanceReply(AvitoObject)

cls ProhibitOrderAcceptanceReplyData(AvitoObject)

cls ProhibitOrderAcceptanceRequest(AvitoObject)

cls UpdateReceiverInfoReply(AvitoObject)

cls UpdateReceiverInfoReplyData(AvitoObject)

cls UpdateReturnInfoReply(AvitoObject)

cls UpdateReturnInfoReplyData(AvitoObject)

cls SetOrderRealAddressAddress(AvitoObject)

cls TrackingOptions(AvitoObject)

cls CreateSandboxParcelV22Receiver(AvitoObject)

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

cls AnalyticsResponseResult(AvitoObject)

cls AnalyticsResponseResultGroupings(AvitoObject)

cls AnalyticsResponseResultGroupingsMetrics(AvitoObject)

cls ApplyVasResp(AvitoObject)

cls CallsStatsDay(AvitoObject)

cls CallsStatsItem(AvitoObject)

cls CallsStatsRequest(AvitoObject)

cls CallsStatsResponse(AvitoObject)

cls CallsStatsResponseResult(AvitoObject)

cls ErrorResponse(AvitoObject)

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

cls ItemsInfoWithCategoryAvitoMeta(AvitoObject)

cls ItemsInfoWithCategoryAvitoResources(AvitoObject)

cls ItemsInfoWithCategoryAvitoResourcesCategory(AvitoObject)

cls SpendingsRequest(AvitoObject)

cls SpendingsRequestFilter(AvitoObject)

cls SpendingsResponse(AvitoObject)

cls SpendingsResponseResult(AvitoObject)

cls SpendingsResponseResultGroupings(AvitoObject)

cls SpendingsResponseResultGroupingsSpendings(AvitoObject)

cls SpendingsResponseResultGroupingsSpendingsServices(AvitoObject)

cls StatisticsCountersRoot(AvitoObject)

cls StatisticsCountersRootStats(AvitoObject)

cls StatisticsResponse(AvitoObject)

cls StatisticsResponseResult(AvitoObject)

cls StatisticsCountersValue(AvitoObject)

cls StatisticsCountersValueStats(AvitoObject)

cls StatisticsShallowRequestBody(AvitoObject)

cls StickerResp(AvitoObject)

cls UpdatePriceRequest(AvitoObject)

cls UpdatePriceResponse(AvitoObject)

cls UpdatePriceResponseResult(AvitoObject)

cls VasAmountAvito(AvitoObject)

cls VasApplyAvito(AvitoObject)

cls VasResp(AvitoObject)

cls AuthError(AvitoObject)

cls BadRequestError(AvitoObject)

cls ItemIdsRequestBody(AvitoObject)

cls NotFoundError(AvitoObject)

cls PackageIdRequestBodyV2(AvitoObject)

cls PricesItemIdsRequestBody(AvitoObject)

cls ServiceError(AvitoObject)

cls ServiceUnavailableError(AvitoObject)

cls TooManyRequests(AvitoObject)

cls ValidatingError(AvitoObject)

cls ValidatingErrorError(AvitoObject)

cls VasIdRequestBody(AvitoObject)

cls ApplyVasResponse(AvitoObject)

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

cls StatisticsItemIDs(RootModel[list[int]])
  # Root wrapper for a top-level ``list[int]`` response.

cls VasPricesResp(RootModel[list[ItemVasPricesResp]])
  # Root wrapper for a top-level ``list[ItemVasPricesResp]`` response.

```

## job.py
```
# Авито.Работа — domain models (auto-generated from the Avito OpenAPI spec).


cls ActivationForbiddenError(AvitoObject)

cls ActivationForbiddenErrorError(AvitoObject)

cls AddressDetails(AvitoObject)

cls AgeCriteria(AvitoObject)

cls ApplicationsApplyActionsRequestBody(AvitoObject)

cls ApplicationsGetStatesResult(AvitoObject)

cls ApplicationsGetStatesResultStates(AvitoObject)

cls ApplyProcessing(AvitoObject)

cls BadRequest(AvitoObject)

cls BadRequestError(AvitoObject)

cls BadRequestOnVacancy(AvitoObject)

cls BadRequestShort(AvitoObject)

cls BadRequestShortError(AvitoObject)

cls Citizenship(AvitoObject)

cls ConflictError(AvitoObject)

cls ConflictErrorError(AvitoObject)

cls Contacts(AvitoObject)

cls Coordinates(AvitoObject)

cls CreationForbiddenError(AvitoObject)

cls CreationForbiddenErrorError(AvitoObject)

cls EditingForbiddenError(AvitoObject)

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

cls ItemNotFoundErrorError(AvitoObject)

cls Location(AvitoObject)

cls LocationAddress(AvitoObject)

cls NotFoundError(AvitoObject)

cls NotFoundErrorError(AvitoObject)

cls PaymentError(AvitoObject)

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
  resume_get_contacts(employee_id: int? = None) -> ResumeGetContacts
    # Build an awaitable :class:`ResumeGetContacts` bound to this object (await to execute).
  resume_get_item(fields: ResumeGetItemFields? = None, params: ResumeGetItemParams? = None, photos: bool = False) -> ResumeGetItem
    # Build an awaitable :class:`ResumeGetItem` bound to this object (await to execute).

cls ResumeContactsFullName(AvitoObject)

cls ResumeSearchMeta(AvitoObject)

cls SalaryBaseRange(AvitoObject)

cls SalaryDetail(AvitoObject)

cls SalaryDetailBase(AvitoObject)

cls SetApplicationsIsViewedResult(AvitoObject)

cls SetApplicationsIsViewedResultApplies(AvitoObject)

cls SimplifiedResume(AvitoObject)

cls SimplifiedVacancy(AvitoObject)

cls SimplifiedVacancyAddressDetails(AvitoObject)

cls Specialization(AvitoObject)

cls StoppingForbiddenError(AvitoObject)

cls StoppingForbiddenErrorError(AvitoObject)

cls VacanciesGetByIdsBody(AvitoObject)

cls Vacancy20(AvitoObject)

cls Vacancy20AddressDetails(AvitoObject)

cls Vacancy20AddressDetailsCoordinates(AvitoObject)

cls Vacancy20Contacts(AvitoObject)

cls Vacancy20Hierarchy(AvitoObject)

cls Vacancy20Params(AvitoObject)

cls Vacancy20ParamsCoordinates(AvitoObject)

cls Vacancy20ParamsSalary(AvitoObject)

cls Vacancy20ParamsSalaryBaseRange(AvitoObject)

cls VacancyArchive(AvitoObject)

cls VacancyAutoRenewal(AvitoObject)

cls VacancyCreate(AvitoObject)

cls VacancyCreateDrivingExperience(AvitoObject)

cls VacancyCreateExperience(AvitoObject)

cls VacancyCreatePayoutFrequency(AvitoObject)

cls VacancyCreateSalaryRange(AvitoObject)

cls VacancyCreateSchedule(AvitoObject)

cls VacancyCreateResult(AvitoObject)

cls VacancyProlongate(AvitoObject)

cls VacancySearchMeta(AvitoObject)

cls VacancyStatusesBody(AvitoObject)

cls VacancyStatusesResultRoot(AvitoObject)

cls VacancyStatusesResultRootLastAction(AvitoObject)

cls VacancyStatusesResultRootVacancy(AvitoObject)

cls VacancyUpdate(AvitoObject)

cls VacancyUpdateDrivingExperience(AvitoObject)

cls VacancyUpdateExperience(AvitoObject)

cls VacancyUpdatePayoutFrequency(AvitoObject)

cls VacancyUpdateSalaryRange(AvitoObject)

cls VacancyV2Create(AvitoObject)

cls VacancyV2CreateContacts(AvitoObject)

cls VacancyV2CreateHierarchy(AvitoObject)

cls VacancyV2CreateLocation(AvitoObject)

cls VacancyV2CreateSalary(AvitoObject)

cls VacancyV2CreateResult(AvitoObject)

cls WebhookSubscribeRequestBody(AvitoObject)

cls WebhooksSubscriptionResultList(AvitoObject)

cls AuthError(AvitoObject)

cls ForbiddenError(AvitoObject)

cls PurchasingError(AvitoObject)

cls ServiceError(AvitoObject)

cls ServiceUnavailableError(AvitoObject)

cls TooManyRequestsError(AvitoObject)

cls ValidatingError(AvitoObject)

cls ValidatingErrorError(AvitoObject)

cls VerificationNeededError(AvitoObject)

cls ApplicationsSetIsViewedApplies(AvitoObject)

cls ApplicationsWebhookDeleteResponse(AvitoObject)

cls ResumesGetResponse(AvitoObject)

cls ResumesGetRadius(AvitoObject)

cls ResumesGetRadiusPoint(AvitoObject)

cls VacancyCreate2DrivingExperience(AvitoObject)

cls VacancyCreate2Experience(AvitoObject)

cls VacancyCreate2PayoutFrequency(AvitoObject)

cls VacancyCreate2SalaryRange(AvitoObject)

cls VacancyCreate2Schedule(AvitoObject)

cls VacancyUpdate2DrivingExperience(AvitoObject)

cls VacancyUpdate2Experience(AvitoObject)

cls VacancyUpdate2PayoutFrequency(AvitoObject)

cls VacancyUpdate2SalaryRange(AvitoObject)

cls SearchVacancyResponse(AvitoObject)

cls VacancyCreateV2Contacts(AvitoObject)

cls VacancyCreateV2Hierarchy(AvitoObject)

cls VacancyCreateV2Location(AvitoObject)

cls VacancyCreateV2Salary(AvitoObject)

cls VacancyUpdateV2Contacts(AvitoObject)

cls VacancyUpdateV2Hierarchy(AvitoObject)

cls VacancyUpdateV2Location(AvitoObject)

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
  post_send_message(message: PostSendMessageMessage? = None, type_: PostSendMessageType? = None) -> PostSendMessage
    # Build an awaitable :class:`PostSendMessage` bound to this object (await to execute).
  post_send_image_message(image_id: str) -> PostSendImageMessage
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

cls ChatUsersPublicUserProfileAvatarImages(AvitoObject)

cls Chats(AvitoObject)

cls MessageContent(AvitoObject)

cls MessageContentCall(AvitoObject)

cls MessageContentImage(AvitoObject)

cls MessageContentItem(AvitoObject)

cls MessageContentLink(AvitoObject)

cls MessageContentLinkPreview(AvitoObject)

cls MessageContentLocation(AvitoObject)

cls MessageContentVoice(AvitoObject)

cls MessageQuote(AvitoObject)

cls MessagesRoot(AvitoObject)

cls PayloadStruct(AvitoObject)

cls VoiceFiles(AvitoObject)

cls WebhookMessage(AvitoObject)

cls AddBlacklistRequestBody(AvitoObject)

cls AddBlacklistRequestBodyUsers(AvitoObject)

cls AddBlacklistRequestBodyUsersContext(AvitoObject)

cls AuthError(AvitoObject)

cls BadRequestError(AvitoObject)

cls ForbiddenError(AvitoObject)

cls NotFoundError(AvitoObject)

cls PurchasingError(AvitoObject)

cls SendImageMessageRequestBody(AvitoObject)

cls SendMessageRequestBody(AvitoObject)

cls SendMessageRequestBodyMessage(AvitoObject)

cls ServiceError(AvitoObject)

cls ServiceUnavailableError(AvitoObject)

cls ValidatingError(AvitoObject)

cls ValidatingErrorError(AvitoObject)

cls WebhookSubscribeRequestBody(AvitoObject)

cls PostSendMessageResponse(AvitoObject)

cls PostSendMessageResponseContent(AvitoObject)

cls PostSendMessageMessage(AvitoObject)

cls PostSendImageMessageResponse(AvitoObject)

cls PostSendImageMessageResponseContent(AvitoObject)

cls PostSendImageMessageResponseContentImage(AvitoObject)

cls DeleteMessageResponse(AvitoObject)

cls ChatReadResponse(AvitoObject)

cls UploadImagesResponse(AvitoObject)

cls GetSubscriptionsResponse(AvitoObject)

cls GetSubscriptionsResponseSubscriptions(AvitoObject)

cls PostWebhookUnsubscribeResponse(AvitoObject)

cls PostBlacklistV2Users(AvitoObject)

cls PostBlacklistV2UsersContext(AvitoObject)

cls PostWebhookV3Response(AvitoObject)

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

cls OrderAcceptReturnOrderResponse(AvitoObject)

cls OrderApplyTransitionRequest(AvitoObject)

cls OrderApplyTransitionRequestParams(AvitoObject)

cls OrderApplyTransitionRequestParamsCnc(AvitoObject)

cls OrderApplyTransitionResponse(AvitoObject)

cls OrderCncSetDetailsRequest(AvitoObject)

cls OrderCncSetDetailsResponse(AvitoObject)

cls OrderCncSetDetailsResponseResult(AvitoObject)

cls OrderCheckConfirmationCodeRequest(AvitoObject)

cls OrderCheckConfirmationCodeResponse(AvitoObject)

cls OrderCheckConfirmationCodeResponseData(AvitoObject)

cls OrderPrices(AvitoObject)

cls OrderSetTrackingNumberRequest(AvitoObject)

cls OrderSetTrackingNumberResponse(AvitoObject)

cls OrdersInfo(AvitoObject)

cls OrdersLabelsRequest(AvitoObject)

cls OrdersLabelsResponse(AvitoObject)

cls ReturnPolicy(AvitoObject)

cls Schedules(AvitoObject)

cls SetCourierDeliveryRangeRequest(AvitoObject)

cls SetCourierDeliveryRangeResponse(AvitoObject)

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

cls NotEnoughMoneyError(AvitoObject)

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


cls Error(AvitoObject)

cls MarketPriceCorrespondenceV1Response(AvitoObject)

cls CreateReportForClassifiedResponse(AvitoObject)

cls CreateReportForClassifiedResponseSuccess(AvitoObject)

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

cls ForbiddenError(AvitoObject)

cls InternalError(AvitoObject)

cls NotFoundError(AvitoObject)

cls TooManyRequestsError(AvitoObject)

cls ValidatingError(AvitoObject)

cls ValidatingErrorError(AvitoObject)

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

cls DatesOverlapBookingErrorError(AvitoObject)

cls Error(AvitoObject)

cls ParamPriceItemRealty(AvitoObject)

cls ParamPricesRealty(AvitoObject)

cls PostCalendarData(AvitoObject)

cls PostCalendarDataBookings(AvitoObject)

cls PostCalendarDataV2(AvitoObject)

cls PostCalendarDataV2Intervals(AvitoObject)

cls RealtyBooking(AvitoObject)

cls RealtyBookingContact(AvitoObject)

cls RealtyBookingSafeDeposit(AvitoObject)

cls ValidatingError(AvitoObject)

cls ValidatingErrorError(AvitoObject)

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


cls OpenApiAvailableRequestBody(AvitoObject)

cls OpenApiAvailableResponseBody(AvitoObject)

cls OpenApiAvailableResponseBodyItems(AvitoObject)

cls OpenApiBadRequestError(AvitoObject)

cls OpenApiForbiddenError(AvitoObject)

cls OpenApiInternalError(AvitoObject)

cls OpenApiMultiConfirmRequestBody(AvitoObject)

cls OpenApiMultiConfirmRequestBodyDispatches(AvitoObject)

cls OpenApiMultiConfirmResponseBody(AvitoObject)

cls OpenApiMultiCreateRequestBody(AvitoObject)

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

cls OpenApiStatsResponseBodyStats(AvitoObject)

cls OpenApiTariffInfoResponseBody(AvitoObject)

cls OpenApiTariffInfoResponseBodyTariffInfo(AvitoObject)

cls OpenApiUnauthorizedError(AvitoObject)

cls OpenApiMultiConfirmDispatches(AvitoObject)

```

## stock_management.py
```
# Управление остатками — domain models (auto-generated from the Avito OpenAPI spec).


cls StockEditResult(AvitoObject)

cls StockEditResultStocks(AvitoObject)

cls StocksInfoResult(AvitoObject)

cls StocksInfoResultStocks(AvitoObject)

cls UnauthError(AvitoObject)

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

cls AuthError(AvitoObject)

cls NotFoundError(AvitoObject)

cls ServiceError(AvitoObject)

```

## trxpromo.py
```
# TrxPromo — domain models (auto-generated from the Avito OpenAPI spec).


cls ApplyReq(AvitoObject)

cls ApplyReqItems(AvitoObject)

cls ApplyResponse(AvitoObject)

cls ApplyResponseSuccess(AvitoObject)

cls ApplyResponseSuccessResult(AvitoObject)

cls ApplyResponseSuccessResultValidCommissionRange(AvitoObject)

cls CancelResponse(AvitoObject)

cls CancelResponseSuccess(AvitoObject)

cls CancelResponseSuccessResult(AvitoObject)

cls CommissionResponse(AvitoObject)

cls CommissionResponseSuccess(AvitoObject)

cls CommissionResponseSuccessResult(AvitoObject)

cls CommissionResponseSuccessResultSettings(AvitoObject)

cls ApiV3error400(AvitoObject)

cls ApiV3error400BadRequest(AvitoObject)

cls ApiV3error401(AvitoObject)

cls ApiV3error401Unauthenticated(AvitoObject)

cls ApiV3error403(AvitoObject)

cls ApiV3error403Forbidden(AvitoObject)

cls ApiV3error500(AvitoObject)

cls ApiV3error500InternalError(AvitoObject)

cls ApiTrxPromoOpenApiApplyItems(AvitoObject)

```

## user.py
```
# Информация о пользователе — domain models (auto-generated from the Avito OpenAPI spec).


cls Balance(AvitoObject)

cls RequestOperationsHistory(AvitoObject)

cls ResponseOperationsHistory(AvitoObject)

cls ResponseOperationsHistoryResult(AvitoObject)

cls ResponseOperationsHistoryItem(AvitoObject)

cls UserInfoSelf(AvitoObject)

cls AuthError(AvitoObject)

cls ForbiddenError(AvitoObject)

cls NotFoundError(AvitoObject)

cls ServiceError(AvitoObject)

cls ServiceUnavailableError(AvitoObject)

```

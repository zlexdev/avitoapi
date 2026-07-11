# enums/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

> Auto-generated domain enums — one module per Avito API domain (see ``avitoapi.codegen``).

## accounts_hierarchy.py
```
# Иерархия Аккаунтов — domain enums (auto-generated from the Avito OpenAPI spec).


```

## ads.py
```
# Авито Реклама — domain enums (auto-generated from the Avito OpenAPI spec).


cls AudienceType(StrEnum): BASIC, READY, AUTOTARGETING
  # AudienceType values.

cls BannerFormat(StrEnum): STANDARD, PREMIUM, ROOT, SELLER_PROFILE
  # BannerFormat values.

cls BudgetFrequency(StrEnum): WEEKLY, ENTIREPERIOD
  # BudgetFrequency values.

cls CampaignFieldName(StrEnum): NAME, ADVERTISERID, CONTRACTID, ADDITIONALAGREEMENTID, PERFORMANCEADDITIONALAGREEMENTID, MANAGERID, CAMPAIGNTYPE, PAYMENTMODEL
  # CampaignFieldName values.

cls CampaignGoalType(StrEnum): PERFORMANCE, REACH
  # CampaignGoalType values.

cls CampaignLandingType(StrEnum): EXTERNAL
  # CampaignLandingType values.

cls CampaignPaymentModel(StrEnum): CPM, CPC
  # CampaignPaymentModel values.

cls CampaignStatus(StrEnum): DRAFT, IN_MODERATION, MODERATION_FAILED, PARTIAL_MODERATION, ACTIVE, WILL_LAUNCH_SOON, PARTIALLY_ACTIVE, WILL_STOP_SOON, PAUSING, PAUSED, UNPAUSING, STOPPED, FINISHED, ARCHIVED
  # CampaignStatus values.

cls CampaignStrategy(StrEnum): MAXCLICKS, MAXVIEWS
  # CampaignStrategy values.

cls CampaignType(StrEnum): TEXTIMAGE, HTML, VIDEO
  # CampaignType values.

cls ContractAction(StrEnum): DISTRIBUTION, CONCLUDE, COMMERCIAL, OTHER
  # ContractAction values.

cls ContractCounterpartyType(StrEnum): DIRECT_WITH_ADVERTISER, ADVERTISER_INTERMEDIARY
  # ContractCounterpartyType values.

cls ContractSubject(StrEnum): ORG_DISTRIBUTION, MEDIATION, DISTRIBUTION, REPRESENTATION, OTHER
  # ContractSubject values.

cls ContractType(StrEnum): SERVICE, INTERMEDIARY, EXTERNAL
  # ContractType values.

cls CreateCampaignPaymentModel(StrEnum): CPC, CPM
  # CreateCampaignPaymentModel values.

cls CreateCampaignType(StrEnum): TEXTIMG, HTML, VIDEO
  # CreateCampaignType values.

cls CreativesStatus(StrEnum): DRAFT, READY_FOR_MODERATION, IN_MODERATION, MODERATION_FAILED, ERIR_REGISTRATION, ACTIVE, PAUSING, PAUSED, UNPAUSING, STOPPED, FINISHED, ARCHIVED
  # CreativesStatus values.

cls FrequencyPeriod(StrEnum): NO_LIMIT, DAY, WEEK, MONTH
  # FrequencyPeriod values.

cls GroupFormat(StrEnum): MEDIAROOT, MEDIASELLERPROFILE, MEDIAPREMIUM, MEDIA, NATIVE, HTMLPREMIUM, HTML, VIDEO
  # GroupFormat values.

cls GroupPriceControl(StrEnum): MANUAL, AUTO
  # GroupPriceControl values.

cls GroupsStatus(StrEnum): DRAFT, IN_MODERATION, MODERATION_FAILED, WILL_LAUNCH_SOON, ACTIVE, WILL_STOP_SOON, PAUSING, PAUSED, UNPAUSING, STOPPED, FINISHED, ARCHIVED
  # GroupsStatus values.

cls LegalRole(StrEnum): RD, RA, RR
  # LegalRole values.

cls LegalType(StrEnum): UL, IP
  # LegalType values.

cls Paces(StrEnum): ASAP, EVEN
  # Paces values.

cls PeriodTimezone(StrEnum): EUROPE_KALININGRAD, EUROPE_MOSCOW, EUROPE_SAMARA, ASIA_YEKATERINBURG, ASIA_OMSK, ASIA_KRASNOYARSK, ASIA_IRKUTSK, ASIA_YAKUTSK, ASIA_VLADIVOSTOK, ASIA_MAGADAN, ASIA_KAMCHATKA
  # PeriodTimezone values.

cls ScheduleType(StrEnum): ALWAYS, WEEKDAYS9TO20, CUSTOM
  # ScheduleType values.

cls UserRole(StrEnum): ADMIN, VIEWER
  # UserRole values.

cls V1GetHtmlOutStatus(StrEnum): UPLOADING, READY, ERROR
  # V1GetHtmlOutStatus values.

```

## auction.py
```
# CPA-аукцион — domain enums (auto-generated from the Avito OpenAPI spec).


```

## auth.py
```
# Авторизация — domain enums (auto-generated from the Avito OpenAPI spec).


```

## autoload.py
```
# Автозагрузка — domain enums (auto-generated from the Avito OpenAPI spec).


cls ApFieldsNodeAlertType(StrEnum): ERROR, WARNING, INFO
  # ApFieldsNodeAlertType values.

cls ApiDependencyAction(StrEnum): VISIBLE, REQUIRED, HIDDEN
  # ApiDependencyAction values.

cls ApiDependencyClause(StrEnum): OR, AND
  # ApiDependencyClause values.

cls ApiDependencyPairClause(StrEnum): VALUE, FILLED, EMPTY
  # ApiDependencyPairClause values.

cls ApiFieldFeedFormat(StrEnum): XML, EXCEL
  # ApiFieldFeedFormat values.

cls ApiFieldContentDataType(StrEnum): STRING, INTEGER, FLOAT
  # ApiFieldContentDataType values.

cls ApiFieldContentFieldType(StrEnum): INPUT, SELECT, CHECKBOX
  # ApiFieldContentFieldType values.

cls ChildApiFieldFeedFormat(StrEnum): XML, EXCEL
  # ChildApiFieldFeedFormat values.

cls ErrorAutoloadErrorCode(StrEnum): FAIL, SUCCESS
  # ErrorAutoloadErrorCode values.

cls ItemFeesInfoReportAutoloadV2FeesType(StrEnum): SINGLE, PACKAGE
  # ItemFeesInfoReportAutoloadV2FeesType values.

cls ItemInfoAutoloadAppliedVas(StrEnum): VIP, HIGHLIGHT, PUSHUP, PREMIUM, TURBO_SALE, QUICK_SALE
  # ItemInfoAutoloadAppliedVas values.

cls ItemInfoAutoloadFeeInfoType(StrEnum): SINGLE, PACKAGE
  # ItemInfoAutoloadFeeInfoType values.

cls ItemInfoAutoloadStatus(StrEnum): SUCCESS, PROBLEM, ERROR, NOT_PUBLISH, WILL_PUBLISH_LATER, DUPLICATE, WITHOUT_ID, DELETED, UNKNOWN
  # ItemInfoAutoloadStatus values.

cls ItemInfoAutoloadStatusDetail(StrEnum): SUCCESS_ADDED, SUCCESS_ACTIVATED, SUCCESS_ACTIVATED_UPDATED, SUCCESS_UPDATED, SUCCESS_SKIPPED, PROBLEM_OBSOLETE, PROBLEM_PARAMS_CRITICAL, PROBLEM_PARAMS, PROBLEM_PHONE, PROBLEM_IMAGES, PROBLEM_VAS, PROBLEM_OTHER, PROBLEM_SEVERAL, ERROR_FEE, ERROR_PARAMS, … (31)
  # ItemInfoAutoloadStatusDetail values.

cls ItemInfoAutoloadV2AvitoStatus(StrEnum): ACTIVE, OLD, BLOCKED, REJECTED, ARCHIVED, REMOVED
  # ItemInfoAutoloadV2AvitoStatus values.

cls ItemInfoAutoloadV2FeeInfoType(StrEnum): SINGLE, PACKAGE
  # ItemInfoAutoloadV2FeeInfoType values.

cls ItemInfoErrorType(StrEnum): ERROR, WARNING, INFO, ALARM
  # ItemInfoErrorType values.

cls ItemInfoReportAutoloadV2AvitoStatus(StrEnum): ACTIVE, OLD, BLOCKED, REJECTED, ARCHIVED, REMOVED
  # ItemInfoReportAutoloadV2AvitoStatus values.

cls ItemInfoVasSlug(StrEnum): XL, HIGHLIGHT, X2_1, X2_7, X5_1, X5_7, X10_1, X10_7, X15_1, X15_7, X20_1, X20_7
  # ItemInfoVasSlug values.

cls ItemMessageV4Type(StrEnum): ERROR, WARNING, ALARM, INFO
  # ItemMessageV4Type values.

cls ReportAutoloadVasType(StrEnum): SERVICE, PACKAGE
  # ReportAutoloadVasType values.

cls ReportAutoloadV2Source(StrEnum): EMAIL, URL, WEB, OPENAPI
  # ReportAutoloadV2Source values.

cls ReportAutoloadV2Status(StrEnum): PROCESSING, SUCCESS, SUCCESS_WARNING, ERROR
  # ReportAutoloadV2Status values.

cls ReportAutoloadV3Source(StrEnum): EMAIL, URL, WEB, OPENAPI
  # ReportAutoloadV3Source values.

cls ReportAutoloadV3Status(StrEnum): PROCESSING, SUCCESS, SUCCESS_WARNING, ERROR
  # ReportAutoloadV3Status values.

cls ReportShortAutoloadV2RootStatus(StrEnum): PROCESSING, SUCCESS, SUCCESS_WARNING, ERROR
  # ReportShortAutoloadV2RootStatus values.

cls UploadAutoloadV4Source(StrEnum): EMAIL, URL, WEB, OPENAPI, UPLOAD
  # UploadAutoloadV4Source values.

cls UploadAutoloadV4Status(StrEnum): PROCESSING, SUCCESS, SUCCESS_WARNING, ERROR
  # UploadAutoloadV4Status values.

cls UploadItemAutoloadV4AvitoStatus(StrEnum): ACTIVE, OLD, BLOCKED, REJECTED, ARCHIVED, REMOVED
  # UploadItemAutoloadV4AvitoStatus values.

cls ReportShortAutoloadV2ValueStatus(StrEnum): PROCESSING, SUCCESS, SUCCESS_WARNING, ERROR
  # ReportShortAutoloadV2ValueStatus values.

```

## autostrategy.py
```
# Автостратегия — domain enums (auto-generated from the Avito OpenAPI spec).


cls CampaignCampaignType(StrEnum): AS, AP
  # CampaignCampaignType values.

cls CreateCampaignRequestBodyCampaignType(StrEnum): AS, AP
  # CreateCampaignRequestBodyCampaignType values.

cls GetBudgetRequestBodyCampaignType(StrEnum): AS, AP
  # GetBudgetRequestBodyCampaignType values.

cls GetCampaignInfoForecastResultCallsLackReason(StrEnum): NOT_ENOUGH_DATA, NO_CALLTRACKING
  # GetCampaignInfoForecastResultCallsLackReason values.

cls GetCampaignInfoForecastResultViewsLackReason(StrEnum): NOT_ENOUGH_DATA
  # GetCampaignInfoForecastResultViewsLackReason values.

cls GetCampaignsRequestBodyOrderByColumn(StrEnum): CAMPAIGNID, USERID, BUDGET, BALANCE, TITLE, STATUSID, STARTTIME, FINISHTIME, CREATETIME, UPDATETIME, ITEMSCOUNT, ISPAID
  # GetCampaignsRequestBodyOrderByColumn values.

cls GetCampaignsRequestBodyOrderByDirection(StrEnum): ASC, DESC
  # GetCampaignsRequestBodyOrderByDirection values.

cls GetAutostrategyBudgetCampaignType(StrEnum): AS, AP
  # GetAutostrategyBudgetCampaignType values.

cls CreateAutostrategyCampaignCampaignType(StrEnum): AS, AP
  # CreateAutostrategyCampaignCampaignType values.

cls GetAutostrategyCampaignsOrderByColumn(StrEnum): CAMPAIGNID, USERID, BUDGET, BALANCE, TITLE, STATUSID, STARTTIME, FINISHTIME, CREATETIME, UPDATETIME, ITEMSCOUNT, ISPAID
  # GetAutostrategyCampaignsOrderByColumn values.

cls GetAutostrategyCampaignsOrderByDirection(StrEnum): ASC, DESC
  # GetAutostrategyCampaignsOrderByDirection values.

```

## autoteka.py
```
# Автотека — domain enums (auto-generated from the Avito OpenAPI spec).


cls CrashesHistoryAutotekaDamageTypesSlug(StrEnum): FRONT_RIGHT, RIGHT_FRONT_DOOR, FRONT_RIGHT_SIDE, LEFT_FRONT, LEFT_FRONT_DOOR, LEFT_FRONT_SIDE, RIGHT_REAR, RIGHT_REAR_DOOR, RIGHT_REAR_SIDE, LEFT_REAR, LEFT_REAR_DOOR, LEFT_REAR_SIDE, ROOF, BOTTOM, FRONT_HOOD, … (16)
  # CrashesHistoryAutotekaDamageTypesSlug values.

cls CrashesHistoryAutotekaDamageTypesType(StrEnum): YELLOW, RED, OTHER
  # CrashesHistoryAutotekaDamageTypesType values.

cls EquipmentAutotekaBodyDescription(StrEnum): MIKROAVTOBUS, KABRIOLET, KUPE, KROSSOVER, UNIVERSAL, MINIVEN, HETCHBEK, VNEDOROZHNIK, PIKAP, SEDAN, FURGON, LIMUZIN
  # EquipmentAutotekaBodyDescription values.

cls EquipmentAutotekaBrandValue(StrEnum): AUDI, BENTLEY, BMW, CADILLAC, CHERY, CHEVROLET, CHRYSLER, CITROEN, DACIA, DAEWOO, DAF, DATSUN, DODGE, FIAT, FORD, … (61)
  # EquipmentAutotekaBrandValue values.

cls EquipmentAutotekaColorValue(StrEnum): BEZHEVO_SERYI, BEZHEVYI, BELYI, BELYI_METALLIK, BELYI_PERLAMUTR, BELYI_CHERNYI, BELYI_ZHELTYI_SERYI, BELYI_CHERNYI_1, BORDOVYI, BRONZOVYI, VISHNEVO_KRASNYI, ZHEMCHUZHNO_BELYI, ZELENYI, ZOLOTISTO_KORICHNEVYI, ZOLOTISTO_OHRISTYI, … (55)
  # EquipmentAutotekaColorValue values.

cls EquipmentAutotekaEngineTypeValue(StrEnum): BENZIN, DIZEL, ELEKTRO, GAZ, GIBRID, BENZINOVYI_NA_SZHIZHENNOM_GAZE, BENZINOVYI_NA_SZHATOM_GAZE, DIZELNYI_NA_SZHIZHENNOM_GAZE, DIZELNYI_NA_SZHATOM_GAZE, ELEKTRO_BENZINOVYI, ELEKTRO_DIZELNYI
  # EquipmentAutotekaEngineTypeValue values.

cls EquipmentAutotekaVehicleCategoryValue(StrEnum): A, B, C, D, E, O_, M1, M1G, N1
  # EquipmentAutotekaVehicleCategoryValue values.

cls EquipmentAutotekaVehicleTypeValue(StrEnum): AVTOBUSY_PROCHIE, GRUZOVOI_BORTOVOI, GRUZOVOI_PROCHII, GRUZOVOI_FURGON, GRUZOVYE_AVTOMOBILI_BORTOVYE, GRUZOVYE_AVTOMOBILI_FURGONY, LEGKOVOE_KUPE, LEGKOVOI_PROCHII, LEGKOVOI_SEDAN, LEGKOVOI_UNIVERSAL, LEGKOVOI_HETCHBEK_KOMBI, LEGKOVYE_AVTOMOBILI_KABRIOLET, LEGKOVYE_AVTOMOBILI_KOMBI_HETCHBEK, LEGKOVYE_AVTOMOBILI_KUPE, LEGKOVYE_AVTOMOBILI_PROCHIE, … (18)
  # EquipmentAutotekaVehicleTypeValue values.

cls EventsAutotekaAvitoOnSaleType(StrEnum): CAUTION, OK, WARNING
  # EventsAutotekaAvitoOnSaleType values.

cls EventsAutotekaBodyRepairType(StrEnum): CAUTION, OK, WARNING
  # EventsAutotekaBodyRepairType values.

cls EventsAutotekaCrashesType(StrEnum): CAUTION, OK, WARNING
  # EventsAutotekaCrashesType values.

cls EventsAutotekaDealerDataAvailableType(StrEnum): CAUTION, OK, WARNING
  # EventsAutotekaDealerDataAvailableType values.

cls EventsAutotekaFirstSellDateType(StrEnum): CAUTION, OK, WARNING
  # EventsAutotekaFirstSellDateType values.

cls EventsAutotekaLastMileageRecordType(StrEnum): CAUTION, OK, WARNING
  # EventsAutotekaLastMileageRecordType values.

cls EventsAutotekaOwnersType(StrEnum): CAUTION, OK, WARNING
  # EventsAutotekaOwnersType values.

cls EventsAutotekaPledgeType(StrEnum): CAUTION, OK, WARNING
  # EventsAutotekaPledgeType values.

cls EventsAutotekaPublicPersonType(StrEnum): CAUTION, OK, WARNING
  # EventsAutotekaPublicPersonType values.

cls EventsOthersHistoryAutotekaType(StrEnum): ACCIDENT, AVITOPLACEMENT, BODYREPAIR, CHANGEINDOCUMENTS, CUSTOMS, DIAGNOSTIC, EMERGENCYCOMMISSIONERCALL, EXTERNALPLACEMENT, INSPECTION, RECALLRECORD, REGISTRATION, REGULATION, REPAIR, REPAIRCALCULATION, SALVAGECARAUCTION, … (21)
  # EventsOthersHistoryAutotekaType values.

cls ExtendedSpecificationsParamKey(StrEnum): BRAND, BRANDID, MODEL, MODELID, BODY_TYPE, KOLICHESTVO_DVEREY, DRIVE, WHEEL, GENERATION, ENGINE_TYPE, TRANSMISSION, COMPLECTATION, MODIFICATION, ENGINE, CAPACITY, … (16)
  # ExtendedSpecificationsParamKey values.

cls ExtendedSpecificationsParamName(StrEnum): BREND, IDENTIFIKATOR_BRENDA, MODEL, IDENTIFIKATOR_MODELI, TIP_AVTOMOBILYA, KOLICHESTVO_DVEREI, PRIVOD, RUL, POKOLENIE, TIP_DVIGATELYA, KOROBKA_PEREDACH, KOMPLEKTATSIYA, MODIFIKATSIYA, MOSCHNOST_DVIGATELYA, OBEM_DVIGATELYA, … (16)
  # ExtendedSpecificationsParamName values.

cls HeadAutotekaBrand(StrEnum): AUDI, BENTLEY, BMW, CADILLAC, CHERY, CHEVROLET, CHRYSLER, CITROEN, DACIA, DAEWOO, DAF, DATSUN, DODGE, FIAT, FORD, … (61)
  # HeadAutotekaBrand values.

cls HeadAutotekaVehicleIdentifierType(StrEnum): VIN, FRAME, UNKNOWN
  # HeadAutotekaVehicleIdentifierType values.

cls OtherAutotekaStatus(StrEnum): OK, WARNING
  # OtherAutotekaStatus values.

cls PreviewAutotekaStatus(StrEnum): SUCCESS, PROCESSING, NOTFOUND
  # PreviewAutotekaStatus values.

cls PriceStatAutotekaStatus(StrEnum): INCOMPLETE, OK
  # PriceStatAutotekaStatus values.

cls ReportWithoutDataAutotekaStatus(StrEnum): SUCCESS, PROCESSING
  # ReportWithoutDataAutotekaStatus values.

cls ReportAutotekaStatus(StrEnum): SUCCESS, PROCESSING, NOTFOUND
  # ReportAutotekaStatus values.

cls ReportAutotekaAsyncStatus(StrEnum): SUCCESS, PROCESSING
  # ReportAutotekaAsyncStatus values.

cls RestrictionsAutotekaPledgePledgeAdditionalDataSource(StrEnum): NBKI, FCIIT
  # RestrictionsAutotekaPledgePledgeAdditionalDataSource values.

cls RestrictionsAutotekaPledgeStatus(StrEnum): OK, WARNING, INCOMPLETE
  # RestrictionsAutotekaPledgeStatus values.

cls RestrictionsAutotekaRegistrationStatus(StrEnum): OK, WARNING, INCOMPLETE
  # RestrictionsAutotekaRegistrationStatus values.

cls RestrictionsAutotekaStealingStatus(StrEnum): OK, WARNING, INCOMPLETE
  # RestrictionsAutotekaStealingStatus values.

cls ScoringDataAutotekaImportOwnerType(StrEnum): UNKNOWN, COMPANY, PERSON
  # ScoringDataAutotekaImportOwnerType values.

cls ScoringTechSpecificationVehicleCategoryGibddValue(StrEnum): A, B, C, D, E, O_, M1, M1G, N1
  # ScoringTechSpecificationVehicleCategoryGibddValue values.

cls ScoringTechSpecificationVehicleTypeGibddValue(StrEnum): AVTOBUSY_PROCHIE, GRUZOVOI_BORTOVOI, GRUZOVOI_PROCHII, GRUZOVOI_FURGON, GRUZOVYE_AVTOMOBILI_BORTOVYE, GRUZOVYE_AVTOMOBILI_FURGONY, LEGKOVOE_KUPE, LEGKOVOI_PROCHII, LEGKOVOI_SEDAN, LEGKOVOI_UNIVERSAL, LEGKOVOI_HETCHBEK_KOMBI, LEGKOVYE_AVTOMOBILI_KABRIOLET, LEGKOVYE_AVTOMOBILI_KOMBI_HETCHBEK, LEGKOVYE_AVTOMOBILI_KUPE, LEGKOVYE_AVTOMOBILI_PROCHIE, … (18)
  # ScoringTechSpecificationVehicleTypeGibddValue values.

cls ServiceInfoAutotekaReportCompleteStatusStatus(StrEnum): INCOMPLETE, OK
  # ServiceInfoAutotekaReportCompleteStatusStatus values.

cls SpecificationEquipmentAutotekaBodyTypeValue(StrEnum): AVTOBUSY_PROCHIE, GRUZOVOI_BORTOVOI, GRUZOVOI_PROCHII, GRUZOVOI_FURGON, GRUZOVYE_AVTOMOBILI_BORTOVYE, GRUZOVYE_AVTOMOBILI_FURGONY, LEGKOVOE_KUPE, LEGKOVOI_PROCHII, LEGKOVOI_SEDAN, LEGKOVOI_UNIVERSAL, LEGKOVOI_HETCHBEK_KOMBI, LEGKOVYE_AVTOMOBILI_KABRIOLET, LEGKOVYE_AVTOMOBILI_KOMBI_HETCHBEK, LEGKOVYE_AVTOMOBILI_KUPE, LEGKOVYE_AVTOMOBILI_PROCHIE, … (18)
  # SpecificationEquipmentAutotekaBodyTypeValue values.

cls SpecificationEquipmentAutotekaBrandValue(StrEnum): AUDI, BENTLEY, BMW, CADILLAC, CHERY, CHEVROLET, CHRYSLER, CITROEN, DACIA, DAEWOO, DAF, DATSUN, DODGE, FIAT, FORD, … (61)
  # SpecificationEquipmentAutotekaBrandValue values.

cls SpecificationEquipmentAutotekaColorValue(StrEnum): BEZHEVO_SERYI, BEZHEVYI, BELYI, BELYI_METALLIK, BELYI_PERLAMUTR, BELYI_CHERNYI, BELYI_ZHELTYI_SERYI, BELYI_CHERNYI_1, BORDOVYI, BRONZOVYI, VISHNEVO_KRASNYI, ZHEMCHUZHNO_BELYI, ZELENYI, ZOLOTISTO_KORICHNEVYI, ZOLOTISTO_OHRISTYI, … (55)
  # SpecificationEquipmentAutotekaColorValue values.

cls SpecificationEquipmentAutotekaEngineTypeValue(StrEnum): BENZIN, DIZEL, ELEKTRO, GAZ, GIBRID, BENZINOVYI_NA_SZHIZHENNOM_GAZE, BENZINOVYI_NA_SZHATOM_GAZE, DIZELNYI_NA_SZHIZHENNOM_GAZE, DIZELNYI_NA_SZHATOM_GAZE, ELEKTRO_BENZINOVYI, ELEKTRO_DIZELNYI
  # SpecificationEquipmentAutotekaEngineTypeValue values.

cls SpecificationEquipmentAutotekaVehicleCategoryValue(StrEnum): A, B, C, D, E, O_, M1, M1G, N1
  # SpecificationEquipmentAutotekaVehicleCategoryValue values.

cls SpecificationResultAutotekaStatus(StrEnum): SUCCESS, PROCESSING, NOTFOUND
  # SpecificationResultAutotekaStatus values.

cls TeaserResponseStatus(StrEnum): SUCCESS, PROCESSING
  # TeaserResponseStatus values.

cls TeaserWithoutDataAutotekaStatus(StrEnum): SUCCESS, PROCESSING
  # TeaserWithoutDataAutotekaStatus values.

cls ValuationBySpecificationResultAutotekaStatus(StrEnum): SUCCESS, NOTFOUND
  # ValuationBySpecificationResultAutotekaStatus values.

cls VehicleSpecificationsParamKey(StrEnum): MAINMODEL, MODEL, TRANSMISSION, DOORS, MANUFACTURED
  # VehicleSpecificationsParamKey values.

cls VehicleSpecificationsParamName(StrEnum): OBOZNACHENIE_MODELI, KOD_MODELI_AVTOMOBILYA, TIP_KOROBKI_PEREDACH, KOLICHESTVO_DVEREI, MODELNYI_GOD
  # VehicleSpecificationsParamName values.

cls VehicleSpecificationsParamValue(StrEnum): LEXUS_NX200T_300H, AGZ15R_AWTLTW, V_6_STUPENCH_AKPP_ZF_6HP28, V_4, V_2008
  # VehicleSpecificationsParamValue values.

```

## avito_promo.py
```
# Авито Promo — domain enums (auto-generated from the Avito OpenAPI spec).


cls BadRequestResponseStatus(StrEnum): BAD_REQUEST
  # BadRequestResponseStatus values.

cls ForbiddenResponseStatus(StrEnum): FORBIDDEN
  # ForbiddenResponseStatus values.

cls LinkType(StrEnum): ADV, TRX
  # LinkType values.

cls NotFoundResponseStatus(StrEnum): NOT_FOUND
  # NotFoundResponseStatus values.

cls OkResponseStatus(StrEnum): OK
  # OkResponseStatus values.

cls StatsMetric(StrEnum): VIEWS, CONTACTS, CONTACTSSHOWPHONE, CONTACTSMESSENGER, CONTACTSSHOWPHONEANDMESSENGER, CONTACTSSBCDISCOUNT, VIEWSTOCONTACTSCONVERSION, FAVORITES, AVERAGEVIEWCOST, AVERAGECONTACTCOST, IMPRESSIONS, IMPRESSIONSTOVIEWSCONVERSION, CLICKPACKAGES, JOBCONTACTS, VIEWSTOORDEREDITEMSCONVERSION, … (35)
  # StatsMetric values.

cls StatsMetricsGrouping(StrEnum): DAY, WEEK, MONTH, TOTALS
  # StatsMetricsGrouping values.

cls StatsSpendingsGrouping(StrEnum): DAY, WEEK, MONTH
  # StatsSpendingsGrouping values.

cls TransactionStatus(StrEnum): PROCESSING, SUCCESS, ERROR
  # TransactionStatus values.

cls UnauthorizedResponseStatus(StrEnum): UNAUTHORIZED
  # UnauthorizedResponseStatus values.

cls AgencyBalanceResponseResultStatus(StrEnum): PROCESSING, ERROR
  # AgencyBalanceResponseResultStatus values.

cls AgencyClientsResponseResultClientsStatus(StrEnum): NEW, ACTIVE
  # AgencyClientsResponseResultClientsStatus values.

cls AgencyClientsResponseResultClientsSubscriptionCategory(StrEnum): AUTO, REALTY, SERVICES, JOB, GOODS
  # AgencyClientsResponseResultClientsSubscriptionCategory values.

cls AgencyClientsResponseResultClientsSubscriptionLevel(StrEnum): BASIC, EXTENDED, MAXIMAL, ULTRA
  # AgencyClientsResponseResultClientsSubscriptionLevel values.

cls AgencyClientsTargetResultResponseResultItemsResultsCategory(StrEnum): GOODS, SERVICES, MACHINERY, JOBS
  # AgencyClientsTargetResultResponseResultItemsResultsCategory values.

cls AgencyClientsTargetResultResponseResultItemsResultsStatus(StrEnum): NEW, UPLIFT, UNAVAILABLE
  # AgencyClientsTargetResultResponseResultItemsResultsStatus values.

cls AgencyClientsTargetResultResponseResultStatus(StrEnum): PENDING, SUCCESS
  # AgencyClientsTargetResultResponseResultStatus values.

cls AgencyFinancesTransactionsHistoryResponseItemsStatus(StrEnum): PENDING, SUCCESS, BLOCKED, FAILED
  # AgencyFinancesTransactionsHistoryResponseItemsStatus values.

cls AgencyUsersInviteStatusResponseResultStatus(StrEnum): PENDING, SUCCESS, DECLINE
  # AgencyUsersInviteStatusResponseResultStatus values.

cls AgencyUsersVerificationStatusResponseResultStatus(StrEnum): VERIFIED, NOT_VERIFIED
  # AgencyUsersVerificationStatusResponseResultStatus values.

cls StatsAccountsItemsSortOrder(StrEnum): ASC, DESC
  # StatsAccountsItemsSortOrder values.

cls StatsAccountsSpendingsResponseResultGroupingsSpendingsServicesSlug(StrEnum): BBIP, PERF_VAS, VAS_XL, VAS_HIGHLIGHT, SBC_DISCOUNT, VAS_STICKER, VAS_PACKAGE, ORDERS_COMMISSION, BOOKINGS_COMMISSION, DELIVERY_SUBSIDY, FBS_COMMISSION, TARIFF_LISTING, LF, TARIFF_REMAINDER, CPA_CLICK_PACKAGE, … (27)
  # StatsAccountsSpendingsResponseResultGroupingsSpendingsServicesSlug values.

cls StatsAccountsSpendingsResponseResultGroupingsSpendingsSlug(StrEnum): PROMOTION, PRESENCE, COMMISSION, REST
  # StatsAccountsSpendingsResponseResultGroupingsSpendingsSlug values.

cls StatsAccountsSpendingsSpendingTypes(StrEnum): ALL, PROMOTION, PRESENCE, COMMISSION, REST
  # StatsAccountsSpendingsSpendingTypes values.

```

## calltracking.py
```
# CallTracking[КТ] — domain enums (auto-generated from the Avito OpenAPI spec).


```

## cpa.py
```
# CPA Авито — domain enums (auto-generated from the Avito OpenAPI spec).


```

## cpxpromo.py
```
# Настройка цены целевого действия — domain enums (auto-generated from the Avito OpenAPI spec).


```

## delivery.py
```
# Доставка — domain enums (auto-generated from the Avito OpenAPI spec).


cls AddTariffRequestV2TariffType(StrEnum): MGT, KGT
  # AddTariffRequestV2TariffType values.

cls AnnouncementDeliveryParticipantDeliverySortingCenterAccuracy(StrEnum): EXACT, APPROXIMATE
  # AnnouncementDeliveryParticipantDeliverySortingCenterAccuracy values.

cls AnnouncementDeliveryParticipantDeliveryType(StrEnum): SORTING_CENTER
  # AnnouncementDeliveryParticipantDeliveryType values.

cls AnnouncementDeliveryParticipantType(StrEnum): V_3PL
  # AnnouncementDeliveryParticipantType values.

cls AnnouncementsCancelRequestReason(StrEnum): CANCELED_BY_DELIVERY_PROVIDER, CANCELED_BY_AVITO
  # AnnouncementsCancelRequestReason values.

cls AnnouncementsCreateRequestAnnouncementType(StrEnum): DELIVERY, PICKUP
  # AnnouncementsCreateRequestAnnouncementType values.

cls AnnouncementsCreateRequest3PlAnnouncementType(StrEnum): DELIVERY, PICKUP
  # AnnouncementsCreateRequest3PlAnnouncementType values.

cls AnnouncementsSuccessResponseDataStatus(StrEnum): SUCCESS
  # AnnouncementsSuccessResponseDataStatus values.

cls AnnouncementsTrackAnnouncementRequestEvent(StrEnum): ACCEPTANCE_DONE, CANCELLED, DELIVERED, RECEIVED
  # AnnouncementsTrackAnnouncementRequestEvent values.

cls DeliveryDirectionTagValue(StrEnum): DIRECTIONTAGFROM, DIRECTIONTAGTO
  # DeliveryDirectionTagValue values.

cls AreaServices(StrEnum): INTAKE, DELIVERY
  # AreaServices values.

cls CancelSandboxParcelErrorCode(StrEnum): VALIDATION_ERROR, INTERNAL_ERROR, UNKNOWN_PROVIDER
  # CancelSandboxParcelErrorCode values.

cls ChangeParcelErrorCode(StrEnum): VALIDATION_ERROR, INTERNAL_ERROR, UNSUITABLE_PARCEL, PARCEL_NOT_FOUND
  # ChangeParcelErrorCode values.

cls ChangeParcelRequestType(StrEnum): CHANGERECEIVER, PROHIBITPARCELRECEIVE, EXTENDPARCELSTORAGE, PROHIBITPARCELACCEPTANCE
  # ChangeParcelRequestType values.

cls ChangeParcelRequestApplicationKind(StrEnum): BUYER, SELLER
  # ChangeParcelRequestApplicationKind values.

cls ChangeParcelResultReplyErrorCode(StrEnum): ID_INVALID, NOT_FOUND, STATUS_INVALID, FAILED_REASON_MISSES, PARCEL_CLOSED
  # ChangeParcelResultReplyErrorCode values.

cls ChangeParcelResultRequestStatus(StrEnum): APPROVED, DECLINED
  # ChangeParcelResultRequestStatus values.

cls ChangeParcelsDataStatus(StrEnum): OK
  # ChangeParcelsDataStatus values.

cls ChangeParcelsErrorCode(StrEnum): VALIDATION_ERROR, UNSUPPORTED_PARAM_ERROR
  # ChangeParcelsErrorCode values.

cls ChangeParcelsRequestType(StrEnum): CHANGERECEIVER, EXTENDPARCELSTORAGE, PROHIBITPARCELRECEIVE, PROHIBITPARCELACCEPTANCE, CHANGERECEIVERTERMINALONCONFIRMED
  # ChangeParcelsRequestType values.

cls CheckConfirmationCodeReplyDataStatus(StrEnum): SUCCESS, FAIL, EXPIRED, ATTEMPTS
  # CheckConfirmationCodeReplyDataStatus values.

cls CreateParcelClientType(StrEnum): PRIVATE, LEGAL, V_3PL
  # CreateParcelClientType values.

cls CreateParcelClientDeliveryCompletenessAndIntegrity(StrEnum): DIRECT_FLOW, RETURN_FLOW
  # CreateParcelClientDeliveryCompletenessAndIntegrity values.

cls CreateParcelClientDeliveryType(StrEnum): TERMINAL, SORTING_CENTER, COURIER
  # CreateParcelClientDeliveryType values.

cls CreateParcelClientDeliveryCourierOptionsDeliveryConfirmationType(StrEnum): PHONE
  # CreateParcelClientDeliveryCourierOptionsDeliveryConfirmationType values.

cls CreateParcelClientDeliveryCourierOptionsDeliveryType(StrEnum): DELIVERY_TO_DOOR, DELIVERY_TO_PORCH, DELIVERY_FROM_DOOR
  # CreateParcelClientDeliveryCourierOptionsDeliveryType values.

cls CreateParcelErrorCode(StrEnum): VALIDATION_ERROR, UNSUPPORTED_PARAM_ERROR, TERMINAL_UNAVAILABLE, SORTING_CENTER_UNAVAILABLE
  # CreateParcelErrorCode values.

cls CreateParcelOptionsReturnPolicyAction(StrEnum): DISABLED, DESTROY, RETURN_TO_DEPARTURE_POINT, RETURN_TO_RECEIVER, MOVE_TO_ON_DEMAND_STORAGE
  # CreateParcelOptionsReturnPolicyAction values.

cls CreateParcelOptionsReturnPolicyAfterUnit(StrEnum): DAY
  # CreateParcelOptionsReturnPolicyAfterUnit values.

cls CreateParcelPaymentStatus(StrEnum): PAID, ON_DELIVERY
  # CreateParcelPaymentStatus values.

cls CreateParcelPropertyAccuracy(StrEnum): EXACT, APPROXIMATE
  # CreateParcelPropertyAccuracy values.

cls CreateSandboxParcelErrorCode(StrEnum): VALIDATION_ERROR, INTERNAL_ERROR, UNKNOWN_PROVIDER
  # CreateSandboxParcelErrorCode values.

cls CreateSandboxParcelOptionsXDeliveryLeg(StrEnum): X_DELIVERY_FIRST_LEG, X_DELIVERY_LAST_LEG
  # CreateSandboxParcelOptionsXDeliveryLeg values.

cls DeliveryDirectionTagRoot(StrEnum): DIRECTIONTAGFROM, DIRECTIONTAGTO
  # DeliveryDirectionTagRoot values.

cls DeliveryReceiverTerminalCodeRoot(StrEnum): IN_TRANSIT, ON_DELIVERY
  # DeliveryReceiverTerminalCodeRoot values.

cls DeliverySenderReceiveTerminalCodeRoot(StrEnum): IN_TRANSIT_RETURN, ON_DELIVERY_RETURN
  # DeliverySenderReceiveTerminalCodeRoot values.

cls DeliveryReceiverTerminalCodeValue(StrEnum): IN_TRANSIT, ON_DELIVERY
  # DeliveryReceiverTerminalCodeValue values.

cls DeliverySenderReceiveTerminalCodeValue(StrEnum): IN_TRANSIT_RETURN, ON_DELIVERY_RETURN
  # DeliverySenderReceiveTerminalCodeValue values.

cls DeliverySetRealAddressRequestAddressAddressType(StrEnum): SENDER_SEND, SENDER_RECEIVE
  # DeliverySetRealAddressRequestAddressAddressType values.

cls DeliveryTariffZoneServiceDeliveryB2CCalculationMechanic(StrEnum): GAP_TO_COST
  # DeliveryTariffZoneServiceDeliveryB2CCalculationMechanic values.

cls DeliveryTariffZoneServiceDeliveryB2CChargeableParameter(StrEnum): WEIGHT, DIMENSIONS, PAID_WEIGHT
  # DeliveryTariffZoneServiceDeliveryB2CChargeableParameter values.

cls DeliveryTariffZoneServiceDeliveryB2CServiceName(StrEnum): DELIVERY_B2C
  # DeliveryTariffZoneServiceDeliveryB2CServiceName values.

cls DeliveryTariffZoneServiceDeliveryB2CWithStepCostCalculationMechanic(StrEnum): WEIGHT_INTERVALS
  # DeliveryTariffZoneServiceDeliveryB2CWithStepCostCalculationMechanic values.

cls DeliveryTariffZoneServiceDeliveryB2CWithStepCostChargeableParameter(StrEnum): WEIGHT
  # DeliveryTariffZoneServiceDeliveryB2CWithStepCostChargeableParameter values.

cls DeliveryTariffZoneServiceDeliveryB2CWithStepCostServiceName(StrEnum): DELIVERY_B2C
  # DeliveryTariffZoneServiceDeliveryB2CWithStepCostServiceName values.

cls DeliveryTariffZoneServiceDeliveryB2CWithStepMinCostCalculationMechanic(StrEnum): WEIGHT_INTERVALS_WITH_MIN_COST
  # DeliveryTariffZoneServiceDeliveryB2CWithStepMinCostCalculationMechanic values.

cls DeliveryTariffZoneServiceDeliveryB2CWithStepMinCostChargeableParameter(StrEnum): WEIGHT, PAID_WEIGHT
  # DeliveryTariffZoneServiceDeliveryB2CWithStepMinCostChargeableParameter values.

cls DeliveryTariffZoneServiceDeliveryB2CWithStepMinCostServiceName(StrEnum): DELIVERY_B2C
  # DeliveryTariffZoneServiceDeliveryB2CWithStepMinCostServiceName values.

cls DeliveryTariffZoneServiceDeliveryC2CCalculationMechanic(StrEnum): GAP_TO_COST
  # DeliveryTariffZoneServiceDeliveryC2CCalculationMechanic values.

cls DeliveryTariffZoneServiceDeliveryC2CChargeableParameter(StrEnum): WEIGHT, DIMENSIONS, PAID_WEIGHT
  # DeliveryTariffZoneServiceDeliveryC2CChargeableParameter values.

cls DeliveryTariffZoneServiceDeliveryC2CServiceName(StrEnum): DELIVERY
  # DeliveryTariffZoneServiceDeliveryC2CServiceName values.

cls DeliveryTariffZoneServiceDeliveryC2CWithStepCostCalculationMechanic(StrEnum): WEIGHT_INTERVALS
  # DeliveryTariffZoneServiceDeliveryC2CWithStepCostCalculationMechanic values.

cls DeliveryTariffZoneServiceDeliveryC2CWithStepCostChargeableParameter(StrEnum): WEIGHT
  # DeliveryTariffZoneServiceDeliveryC2CWithStepCostChargeableParameter values.

cls DeliveryTariffZoneServiceDeliveryC2CWithStepCostServiceName(StrEnum): DELIVERY
  # DeliveryTariffZoneServiceDeliveryC2CWithStepCostServiceName values.

cls DeliveryTariffZoneServiceDeliveryC2CWithStepMinCostCalculationMechanic(StrEnum): WEIGHT_INTERVALS_WITH_MIN_COST
  # DeliveryTariffZoneServiceDeliveryC2CWithStepMinCostCalculationMechanic values.

cls DeliveryTariffZoneServiceDeliveryC2CWithStepMinCostChargeableParameter(StrEnum): WEIGHT, PAID_WEIGHT
  # DeliveryTariffZoneServiceDeliveryC2CWithStepMinCostChargeableParameter values.

cls DeliveryTariffZoneServiceDeliveryC2CWithStepMinCostServiceName(StrEnum): DELIVERY
  # DeliveryTariffZoneServiceDeliveryC2CWithStepMinCostServiceName values.

cls DeliveryTariffZoneServiceInsuranceB2CCalculationMechanic(StrEnum): GAP_TO_PERCENT
  # DeliveryTariffZoneServiceInsuranceB2CCalculationMechanic values.

cls DeliveryTariffZoneServiceInsuranceB2CChargeableParameter(StrEnum): DECLARED_COST
  # DeliveryTariffZoneServiceInsuranceB2CChargeableParameter values.

cls DeliveryTariffZoneServiceInsuranceB2CServiceName(StrEnum): INSURANCE_B2C
  # DeliveryTariffZoneServiceInsuranceB2CServiceName values.

cls DeliveryTariffZoneServiceInsuranceC2CCalculationMechanic(StrEnum): GAP_TO_PERCENT
  # DeliveryTariffZoneServiceInsuranceC2CCalculationMechanic values.

cls DeliveryTariffZoneServiceInsuranceC2CChargeableParameter(StrEnum): DECLARED_COST
  # DeliveryTariffZoneServiceInsuranceC2CChargeableParameter values.

cls DeliveryTariffZoneServiceInsuranceC2CServiceName(StrEnum): INSURANCE
  # DeliveryTariffZoneServiceInsuranceC2CServiceName values.

cls GetChangeParcelInfoErrorCode(StrEnum): VALIDATION_ERROR, INTERNAL_ERROR, APPLICATION_NOT_FOUND
  # GetChangeParcelInfoErrorCode values.

cls GetInfoByOrderIdErrorReplyName(StrEnum): NOT_AUTHORIZED, BAD_PARAMETER, BAD_REQUEST
  # GetInfoByOrderIdErrorReplyName values.

cls GetRegisteredParcelIdErrorCode(StrEnum): NOT_FOUND, NOT_REGISTERED, VALIDATION_ERROR, INTERNAL_ERROR
  # GetRegisteredParcelIdErrorCode values.

cls GetSandboxParcelInfoErrorCode(StrEnum): VALIDATION_ERROR, INTERNAL_ERROR, UNKNOWN_PROVIDER, NOT_FOUND
  # GetSandboxParcelInfoErrorCode values.

cls GetTaskDataState(StrEnum): PROCESSING, SUCCESS, FAILED, PENDING_APPROVAL, DECLINED
  # GetTaskDataState values.

cls GetTerminalsTaskReplyDataState(StrEnum): PROCESSING, SUCCESS, FAILED, PENDING_APPROVAL, DECLINED
  # GetTerminalsTaskReplyDataState values.

cls SandboxCancelAnnouncementErrorCode(StrEnum): INTERNAL_ERROR, VALIDATION_ERROR, ANNOUNCEMENT_NOT_FOUND
  # SandboxCancelAnnouncementErrorCode values.

cls SandboxCancelAnnouncementReplyDataStatus(StrEnum): SUCCESS
  # SandboxCancelAnnouncementReplyDataStatus values.

cls SandboxCreateAnnouncementDeliveryPointAccuracy(StrEnum): EXACT, APPROXIMATE
  # SandboxCreateAnnouncementDeliveryPointAccuracy values.

cls SandboxCreateAnnouncementErrorCode(StrEnum): VALIDATION_ERROR, INTERNAL_ERROR, OBJECT_EXISTS
  # SandboxCreateAnnouncementErrorCode values.

cls SandboxCreateAnnouncementParticipantDeliveryType(StrEnum): TERMINAL, SORTING_CENTER
  # SandboxCreateAnnouncementParticipantDeliveryType values.

cls SandboxCreateAnnouncementParticipantType(StrEnum): V_3PL, ABD
  # SandboxCreateAnnouncementParticipantType values.

cls SandboxCreateAnnouncementReplyDataStatus(StrEnum): SUCCESS, FAILED
  # SandboxCreateAnnouncementReplyDataStatus values.

cls SandboxCreateAnnouncementRequestAnnouncementType(StrEnum): DELIVERY, PICKUP
  # SandboxCreateAnnouncementRequestAnnouncementType values.

cls SandboxGetAnnouncementEventErrorCode(StrEnum): INTERNAL_ERROR, VALIDATION_ERROR, ANNOUNCEMENT_NOT_FOUND
  # SandboxGetAnnouncementEventErrorCode values.

cls SetStatusErrorReplyName(StrEnum): NOT_AUTHORIZED, BAD_PARAMETER, BAD_REQUEST
  # SetStatusErrorReplyName values.

cls SetStatusRequestStatus(StrEnum): DELIVERY_RECEIVE, DELIVERY_SEND, RETURN_RECEIVE, RETURN_SEND
  # SetStatusRequestStatus values.

cls TerminalOptions(StrEnum): FITTING, ELECTRONICS_CHECKING, COD_BY_CARD, COD_BY_CASH, MULTI_DROP_OFF
  # TerminalOptions values.

cls TerminalServices(StrEnum): INTAKE, DELIVERY
  # TerminalServices values.

cls ZoneType(StrEnum): V_0, V_3, V_4, V_5, V_6, S_PUDO2S_PUDO, S_AREA2S_AREA, S_PUDO2S_AREA, S_PUDO_BTW_F_HUB, S_HUB_BTW_S_PUDO
  # ZoneType values.

cls CancelParcelReplyDataStatus(StrEnum): OK
  # CancelParcelReplyDataStatus values.

cls CancelParcelRequestActor(StrEnum): RECEIVER
  # CancelParcelRequestActor values.

cls CustomAreaScheduleRequestObjectServices(StrEnum): INTAKE, DELIVERY
  # CustomAreaScheduleRequestObjectServices values.

cls ProhibitOrderAcceptanceReplyDataStatus(StrEnum): OK
  # ProhibitOrderAcceptanceReplyDataStatus values.

cls CancelAnnouncement3PlReason(StrEnum): CANCELED_BY_DELIVERY_PROVIDER, CANCELED_BY_AVITO
  # CancelAnnouncement3PlReason values.

cls CreateAnnouncement3PlAnnouncementType(StrEnum): DELIVERY, PICKUP
  # CreateAnnouncement3PlAnnouncementType values.

cls CreateAnnouncementAnnouncementType(StrEnum): DELIVERY, PICKUP
  # CreateAnnouncementAnnouncementType values.

cls TrackAnnouncementEvent(StrEnum): ACCEPTANCE_DONE, CANCELLED, DELIVERED, RECEIVED
  # TrackAnnouncementEvent values.

cls CancelParcelActor(StrEnum): RECEIVER
  # CancelParcelActor values.

cls SetOrderRealAddressAddressAddressType(StrEnum): SENDER_SEND, SENDER_RECEIVE
  # SetOrderRealAddressAddressAddressType values.

cls AddTariffSandboxV2TariffType(StrEnum): MGT, KGT
  # AddTariffSandboxV2TariffType values.

cls V1changeParcelType(StrEnum): CHANGERECEIVER, PROHIBITPARCELRECEIVE, EXTENDPARCELSTORAGE, PROHIBITPARCELACCEPTANCE
  # V1changeParcelType values.

cls V1createAnnouncementAnnouncementType(StrEnum): DELIVERY, PICKUP
  # V1createAnnouncementAnnouncementType values.

cls ChangeParcelResultStatus(StrEnum): APPROVED, DECLINED
  # ChangeParcelResultStatus values.

cls ChangeParcelsType(StrEnum): CHANGERECEIVER, EXTENDPARCELSTORAGE, PROHIBITPARCELRECEIVE, PROHIBITPARCELACCEPTANCE, CHANGERECEIVERTERMINALONCONFIRMED
  # ChangeParcelsType values.

```

## items.py
```
# Объявления — domain enums (auto-generated from the Avito OpenAPI spec).


cls AnalyticsRequestSortOrder(StrEnum): ASC, DESC
  # AnalyticsRequestSortOrder values.

cls Groupings(StrEnum): DAY, WEEK, MONTH, ITEM, TOTALS
  # Groupings values.

cls InfoVasVasId(StrEnum): VIP, HIGHLIGHT, PUSHUP, PREMIUM, XL
  # InfoVasVasId values.

cls ItemInfoAvitoStatus(StrEnum): ACTIVE, REMOVED, OLD, BLOCKED, REJECTED, NOT_FOUND, ANOTHER_USER
  # ItemInfoAvitoStatus values.

cls ItemsInfoWithCategoryAvitoResourcesStatus(StrEnum): ACTIVE, REMOVED, OLD, BLOCKED, REJECTED
  # ItemsInfoWithCategoryAvitoResourcesStatus values.

cls SpendingsGroupings(StrEnum): DAY, WEEK, MONTH
  # SpendingsGroupings values.

cls StatisticsFieldsRoot(StrEnum): VIEWS, UNIQVIEWS, CONTACTS, UNIQCONTACTS, FAVORITES, UNIQFAVORITES
  # StatisticsFieldsRoot values.

cls StatisticsPeriodGrouping(StrEnum): DAY, WEEK, MONTH
  # StatisticsPeriodGrouping values.

cls StatisticsFieldsValue(StrEnum): VIEWS, UNIQVIEWS, CONTACTS, UNIQCONTACTS, FAVORITES, UNIQFAVORITES
  # StatisticsFieldsValue values.

cls PackageIdRequestBodyV2PackageId(StrEnum): X2_1, X2_7, X5_1, X5_7, X10_1, X10_7, X15_1, X15_7, X20_1, X20_7
  # PackageIdRequestBodyV2PackageId values.

cls VasIdRequestBodyVasId(StrEnum): HIGHLIGHT, XL
  # VasIdRequestBodyVasId values.

cls PutItemVasVasId(StrEnum): HIGHLIGHT, XL
  # PutItemVasVasId values.

cls GetItemsInfoStatus(StrEnum): ACTIVE, REMOVED, OLD, BLOCKED, REJECTED
  # GetItemsInfoStatus values.

cls PutItemVasPackageV2PackageId(StrEnum): X2_1, X2_7, X5_1, X5_7, X10_1, X10_7, X15_1, X15_7, X20_1, X20_7
  # PutItemVasPackageV2PackageId values.

cls ItemAnalyticsSortOrder(StrEnum): ASC, DESC
  # ItemAnalyticsSortOrder values.

```

## job.py
```
# Авито.Работа — domain enums (auto-generated from the Avito OpenAPI spec).


cls ActivationForbiddenErrorErrorType(StrEnum): VACANCIES
  # ActivationForbiddenErrorErrorType values.

cls ActivationForbiddenErrorErrorValue(StrEnum): CHOSEN_VACANCY_BELONGS_TO_ANOTHER_USER, UNAVAILABLE_FOR_BLOCKED, UNAVAILABLE_FOR_REMOVED, TOO_EARLY, UNAVAILABLE_TO_ACTIVATE, VACANCY_DOES_NOT_BELONG_TO_EMPLOYEE, EMPLOYEE_IS_NOT_ACTIVE
  # ActivationForbiddenErrorErrorValue values.

cls ApplyProcessingAdditionalQuestions(StrEnum): EXPERIENCE, CITIZENSHIP, AGE
  # ApplyProcessingAdditionalQuestions values.

cls ApplyProcessingApplyType(StrEnum): ONLY_WITH_RESUME, WITH_ASSISTANT
  # ApplyProcessingApplyType values.

cls BadRequestErrorReason(StrEnum): IS_EMPTY, WRONG_VALUE, CHOSEN_AREA_IS_NOT_A_LEAF_OR_NOT_EXIST, CHOSEN_PHONE_BELONGS_TO_ANOTHER_USER, NO_PHONE_FOR_AUTO_SUBSTITUTION
  # BadRequestErrorReason values.

cls BadRequestErrorType(StrEnum): BAD_JSON_DATA
  # BadRequestErrorType values.

cls BadRequestErrorValue(StrEnum): BILLING_TYPE
  # BadRequestErrorValue values.

cls BadRequestShortErrorReason(StrEnum): IS_EMPTY, WRONG_VALUE
  # BadRequestShortErrorReason values.

cls BadRequestShortErrorType(StrEnum): BAD_JSON_DATA
  # BadRequestShortErrorType values.

cls BonusesRoot(StrEnum): PROZIVANIE, PITANIE, MEDICINSKAIA_STRAXOVKA, UNIFORM, OPLATA_BENZINA, TRANSPORT_DO_RABOTY, SKIDKI_V_KOMPANII, PARKOVKA, ZONY_OTDYXA, PODARKI_DETIAM_NA_PRAZDNIKI, OPLATA_MOBILNOI_SVIAZI, OBUCHENIE, KOMPENSACIYA_PROEZDA_S_RABOTI, KASKO, SMARTPHONE, … (16)
  # BonusesRoot values.

cls CitizenshipCriteriaRoot(StrEnum): RUS, BLR, KAZ, KGZ, TJK, ARM, UZB, UKR
  # CitizenshipCriteriaRoot values.

cls ConstructionWorkTypeRoot(StrEnum): PAINTINGWORKS, WALLCOVERING, TILEWORK, MOUNTINGANDINSTALLATION, FINISHINGWORK, ROOFING, INSTALLATIONANDCONFIGURATIONOFEQUIPMENT, WELDINGWORK, CONSTRUCTIONOFFACADES, FORMINGMATERIALS, CONCRETEANDSTONEWORKS, REPAIRWORK, OTHER
  # ConstructionWorkTypeRoot values.

cls CreationForbiddenErrorErrorType(StrEnum): VACANCIES
  # CreationForbiddenErrorErrorType values.

cls CreationForbiddenErrorErrorValue(StrEnum): UNAVAILABLE_TO_CREATE, EMPLOYEE_DOES_NOT_BELONG_TO_COMPANY, EMPLOYEE_IS_NOT_ACTIVE
  # CreationForbiddenErrorErrorValue values.

cls CuisineRoot(StrEnum): RUSSIAN, EUROPEAN, CAUCASIAN, ITALIAN, JAPANESE, TURKISH, OTHER
  # CuisineRoot values.

cls DriverLicence(StrEnum): TRUE, FALSE
  # DriverLicence values.

cls DriverLicenceCategoryRoot(StrEnum): A, B, BE, C, CE, D, DE, M, TM, TB
  # DriverLicenceCategoryRoot values.

cls DrivingExperience(StrEnum): LESS_THAN_THREE_YEARS, MORE_THAN_THREE_YEARS
  # DrivingExperience values.

cls DrivingLicenseCategoryRoot(StrEnum): A, AI, AII, AIII, AIV, B, B1, BE, C, C1, C1E, CE, D, D1, D1E, … (21)
  # DrivingLicenseCategoryRoot values.

cls EateryTypeRoot(StrEnum): CAFE, BAR, FASTFOOD, RESTAURANT, CANTEEN, BAKERY, OTHER
  # EateryTypeRoot values.

cls EditingForbiddenErrorErrorType(StrEnum): VACANCIES
  # EditingForbiddenErrorErrorType values.

cls EditingForbiddenErrorErrorValue(StrEnum): CHOSEN_VACANCY_BELONGS_TO_ANOTHER_USER, UNAVAILABLE_FOR_BLOCKED, UNAVAILABLE_FOR_REMOVED, UNAVAILABLE_TO_CHANGE_LOCATION, UNAVAILABLE_TO_EDIT, VACANCY_DOES_NOT_BELONG_TO_EMPLOYEE, EMPLOYEE_IS_NOT_ACTIVE
  # EditingForbiddenErrorErrorValue values.

cls EducationLevel(StrEnum): HIGHER, UNFINISHED_HIGHER, SECONDARY, SPECIAL_SECONDARY, NONE
  # EducationLevel values.

cls EnrichedPropertiesStatus(StrEnum): IN_PROGRESS, NOT_COMPLETED, COMPLETED_NO_CRITERIA, COMPLETED_MATCHED, COMPLETED_MISMATCHED
  # EnrichedPropertiesStatus values.

cls EnrichedPropertyMatchingStatus(StrEnum): NO_CRITERIA, MATCHED, MISMATCHED
  # EnrichedPropertyMatchingStatus values.

cls FacilityTypeRoot(StrEnum): PRODUCTION, LOGISTICSCENTER, WAREHOUSE, OTHER
  # FacilityTypeRoot values.

cls FoodProductionShopTypeRoot(StrEnum): COLD, HOT, CONFECTIONERY, PREPARATION, OTHER
  # FoodProductionShopTypeRoot values.

cls Gender(StrEnum): FEMALE, MALE, NONE
  # Gender values.

cls GetApplicationsByIdsResultAppliesSource(StrEnum): SBC_COLD_FLOW
  # GetApplicationsByIdsResultAppliesSource values.

cls GetApplicationsByIdsResultAppliesType(StrEnum): BY_PHONE, BY_CHAT
  # GetApplicationsByIdsResultAppliesType values.

cls Grade(StrEnum): JUNIOR, MIDDLE, SENIOR, LEAD
  # Grade values.

cls ItemNotFoundErrorErrorType(StrEnum): VACANCIES
  # ItemNotFoundErrorErrorType values.

cls ItemNotFoundErrorErrorValue(StrEnum): CHOSEN_VACANCY_IS_NOT_FOUND
  # ItemNotFoundErrorErrorValue values.

cls MedicalBook(StrEnum): TRUE, FALSE
  # MedicalBook values.

cls MedicalBookVacancy(StrEnum): REGISTERBYCANDIDATE, HELPREGISTER, NOTNEEDED
  # MedicalBookVacancy values.

cls NotFoundErrorErrorType(StrEnum): VACANCIES
  # NotFoundErrorErrorType values.

cls NotFoundErrorErrorValue(StrEnum): EMPLOYEE_NOT_FOUND
  # NotFoundErrorErrorValue values.

cls OwnTransport(StrEnum): FALSE, CAR, CARGO_CAR, BIKE, SCOOTER
  # OwnTransport values.

cls PaidPeriod(StrEnum): MONTH, WEEK, SHIFT, HOUR, PIECEWORK
  # PaidPeriod values.

cls PaymentErrorErrorType(StrEnum): VACANCIES
  # PaymentErrorErrorType values.

cls PaymentErrorErrorValue(StrEnum): NOT_ENOUGH_PURCHASED_SERVICES, EMPLOYEE_DOES_NOT_HAVE_ENOUGH_PURCHASED_SERVICES, EMPLOYEE_CAN_PUBLISH_ONLY_FROM_BILLING_TYPE_PACKAGE
  # PaymentErrorErrorValue values.

cls PrevalidationAnswerVariable(StrEnum): JOB_FIO, JOB_PHONE, JOB_BIRTHDATE, JOB_CITY, JOB_GENDER, JOB_CITIZENSHIP, JOB_SCHEDULE, JOB_EDUCATIONAL_LEVEL, JOB_DISTRICT, JOB_EXPERIENCE, JOB_WORK_DURATION, JOB_LAST_EMPLOYMENT, JOB_LAST_POSITION, JOB_SALARY_EXPECTATIONS, JOB_RESPONSIBILITY, … (44)
  # PrevalidationAnswerVariable values.

cls RegistrationMethodRoot(StrEnum): CONTRACT, GPH_IP, GPH_SELF_EMPLOYED, GPH_INDIVIDUAL
  # RegistrationMethodRoot values.

cls Resume20ParamsAbilityToBusinessTrip(StrEnum): NE_GOTOV, GOTOV, INOGDA
  # Resume20ParamsAbilityToBusinessTrip values.

cls Resume20ParamsBusinessArea(StrEnum): IT_INTERNET_TELEKOM, AVTOMOBILNYI_BIZNES, ADMINISTRATIVNAYA_RABOTA, BANKI_INVESTITSII, BEZ_OPYTA_STUDENTY, BUHGALTERIYA_FINANSY, VYSSHII_MENEDZHMENT, GOSSLUZHBA_NKO, DOMASHNII_PERSONAL, ZHKH_EKSPLUATATSIYA, ISKUSSTVO_RAZVLECHENIYA, KONSULTIROVANIE, KURERSKAYA_DOSTAVKA, MARKETING_REKLAMA_PR, MEDITSINA_FARMATSEVTIKA, … (27)
  # Resume20ParamsBusinessArea values.

cls Resume20ParamsDriverLicence(StrEnum): TRUE, FALSE
  # Resume20ParamsDriverLicence values.

cls Resume20ParamsDriverLicenceCategory(StrEnum): A, B, BE, C, CE, D, DE, M, TM, TB
  # Resume20ParamsDriverLicenceCategory values.

cls Resume20ParamsEducation(StrEnum): VYSSHEE, NEZAKONCHENNOE_VYSSHEE, SREDNEE, SREDNEE_SPETSIALNOE
  # Resume20ParamsEducation values.

cls Resume20ParamsLanguageListLanguageLevel(StrEnum): NACHALNYI, SREDNII, VYSHE_SREDNEGO, SVOBODNOE_VLADENIE
  # Resume20ParamsLanguageListLanguageLevel values.

cls Resume20ParamsMoving(StrEnum): NEVOZMOZHEN, VOZMOZHEN
  # Resume20ParamsMoving values.

cls Resume20ParamsPol(StrEnum): MUZHSKOI, ZHENSKII
  # Resume20ParamsPol values.

cls Resume20ParamsRazreshenieNaRabotuVRossii(StrEnum): DA, NET
  # Resume20ParamsRazreshenieNaRabotuVRossii values.

cls Resume20ParamsSchedule(StrEnum): FLYINFLYOUT, PARTTIME, FULLDAY, FLEXIBLE, SHIFT, REMOTE, FIVEDAY, SIXDAY
  # Resume20ParamsSchedule values.

cls ResumeContactType(StrEnum): E_MAIL, PHONE, CHAT_ID
  # ResumeContactType values.

cls RetailEquipmentTypeRoot(StrEnum): CASHREGISTERANDPOSTERMINALS, ACCOUNTINGSOFTWARE
  # RetailEquipmentTypeRoot values.

cls RetailShopTypeRoot(StrEnum): HYPERMARKETORSUPERMARKET, GROCERY, ELECTRONICSANDHOUSEHOLDAPPLIANCES, CLOTHESANDSHOES, PERFUMESANDCOSMETICS, CONSTRUCTIONANDHOUSEHOLDGOODS, CHILDRENGOODS, SPORTINGGOODS, PETSHOP, PHARMACY, OTHER
  # RetailShopTypeRoot values.

cls DriverLicenceCategoryValue(StrEnum): A, B, BE, C, CE, D, DE, M, TM, TB
  # DriverLicenceCategoryValue values.

cls StoppingForbiddenErrorErrorType(StrEnum): VACANCIES
  # StoppingForbiddenErrorErrorType values.

cls StoppingForbiddenErrorErrorValue(StrEnum): CHOSEN_VACANCY_BELONGS_TO_ANOTHER_USER, UNAVAILABLE_FOR_BLOCKED, UNAVAILABLE_FOR_REMOVED, UNAVAILABLE_FOR_REJECTED, UNAVAILABLE_TO_STOP, VACANCY_DOES_NOT_BELONG_TO_EMPLOYEE, EMPLOYEE_IS_NOT_ACTIVE
  # StoppingForbiddenErrorErrorValue values.

cls Taxes(StrEnum): GROSS, NET
  # Taxes values.

cls ToolsAvailability(StrEnum): NEEDYOUROWN, WILLBEPROVIDED
  # ToolsAvailability values.

cls VacanciesGetByIdsBodyFields(StrEnum): TITLE, DESCRIPTION, URL, SALARY, START_TIME, UPDATE_TIME, IS_ACTIVE
  # VacanciesGetByIdsBodyFields values.

cls VacanciesGetByIdsBodyParams(StrEnum): ADDRESS, ADMINISTRATOR_ORGANIZATION_TYPE, AGE_PREFERENCES, APPLIES_FILTER, BONUSES, BUSINESS_AREA, CHANGE, CITIZENSHIP, CONSTRUCTION_WORK_TYPE, COORDINATES, CUISINE, DELIVERY_METHOD, DRIVING_EXPERIENCE, DRIVING_LICENSE_CATEGORY, EATERY_TYPE, … (51)
  # VacanciesGetByIdsBodyParams values.

cls Vacancy20ParamsAgePreferences(StrEnum): SOISKATELI_STARSHE_45_LET, SOISKATELI_OT_14_LET, SOISKATELI_OT_16_LET, S_NARUSHENIYAMI_ZDOROVYA, DLYA_STUDENTOV, DLYA_PENSIONEROV
  # Vacancy20ParamsAgePreferences values.

cls Vacancy20ParamsBonuses(StrEnum): UNIFORMA, PROZHIVANIE, MEDITSINSKAYA_STRAHOVKA, PITANIE, OPLATA_BENZINA, PARKOVKA, ZONY_OTDYHA, TRANSPORT_DO_RABOTY, SKIDKI_V_KOMPANII, PODARKI_DETYAM_NA_PRAZDNIKI, OPLATA_MOBILNOI_SVYAZI, OBUCHENIE, KOMPENSATSIYA_PROEZDA_S_RABOTY, KASKO, SMARTFON, … (16)
  # Vacancy20ParamsBonuses values.

cls Vacancy20ParamsChange(StrEnum): V_1_2, V_1_3, V_2_1, V_2_2, V_3_3, V_3_2, V_4_3, V_5_2, V_4_2, V_6_1, BEZ_VYHODNYH, UTRENNIE, DNEVNYE, VECHERNIE, NOCHNYE, … (17)
  # Vacancy20ParamsChange values.

cls Vacancy20ParamsConstructionWorkType(StrEnum): MALYARNYE_RABOTY, OBLITSOVKA_STEN, RABOTY_S_PLITKOI, MONTAZH_I_USTANOVKA, OTDELOCHNYE_RABOTY, KROVELNYE_RABOTY, MONTAZH_I_NASTROIKA_OBORUDOVANIYA, SVAROCHNYE_RABOTY, STROITELSTVO_FASADOV, FORMOVKA_MATERIALOV, BETONNYE_I_KAMENNYE_RABOTY, REMONTNYE_RABOTY, DRUGIE
  # Vacancy20ParamsConstructionWorkType values.

cls Vacancy20ParamsCuisine(StrEnum): RUSSKAYA, EVROPEISKAYA, KAVKAZSKAYA, ITALYANSKAYA, YAPONSKAYA, TURETSKAYA, DRUGAYA
  # Vacancy20ParamsCuisine values.

cls Vacancy20ParamsDeliveryMethod(StrEnum): NA_AVTOMOBILE, NA_VELOSIPEDE, NA_SAMOKATE, PESHKOM
  # Vacancy20ParamsDeliveryMethod values.

cls Vacancy20ParamsDrivingExperience(StrEnum): NET_OPYTA, MENSHE_GODA, V_1_2_GODA, V_3_5_LET, V_6_10_LET, BOLSHE_10_LET
  # Vacancy20ParamsDrivingExperience values.

cls DrivingLicenseCategoryValue(StrEnum): A, AI, AII, AIII, AIV, B, B1, BE, C, C1, C1E, CE, D, D1, D1E, … (21)
  # DrivingLicenseCategoryValue values.

cls Vacancy20ParamsEateryType(StrEnum): KAFE, BAR, FASTFUD, RESTORAN, STOLOVAYA, PEKARNYA, DRUGOI
  # Vacancy20ParamsEateryType values.

cls Vacancy20ParamsExperience(StrEnum): BEZ_OPYTA, BOLEE_1_GODA, BOLEE_3_LET, BOLEE_5_LET, BOLEE_10_LET
  # Vacancy20ParamsExperience values.

cls Vacancy20ParamsFacilityType(StrEnum): PROIZVODSTVO, LOGISTICHESKII_TSENTR, SKLAD, DRUGOE
  # Vacancy20ParamsFacilityType values.

cls Vacancy20ParamsFoodProductionShopType(StrEnum): HOLODNYI, GORYACHII, KONDITERSKII, ZAGOTOVOCHNYI, DRUGOI
  # Vacancy20ParamsFoodProductionShopType values.

cls Vacancy20ParamsIsCompanyCar(StrEnum): DA, NET
  # Vacancy20ParamsIsCompanyCar values.

cls Vacancy20ParamsIsRemote(StrEnum): DA, NET
  # Vacancy20ParamsIsRemote values.

cls Vacancy20ParamsIsSideJob(StrEnum): DA, NET
  # Vacancy20ParamsIsSideJob values.

cls Vacancy20ParamsMedicalBook(StrEnum): DOLZHEN_OFORMIT_KANDIDAT, POMOZHEM_OFORMIT, NE_NUZHNA
  # Vacancy20ParamsMedicalBook values.

cls Vacancy20ParamsPaidPeriod(StrEnum): V_MESYATS, V_NEDELYU, ZA_SMENU, ZA_CHAS, SDELNAYA_OPLATA
  # Vacancy20ParamsPaidPeriod values.

cls Vacancy20ParamsPayoutFrequency(StrEnum): POCHASOVAYA_OPLATA, KAZHDYI_DEN, DVAZHDY_V_MESYATS, RAZ_V_NEDELYU, TRI_RAZA_V_MESYATS, RAZ_V_MESYATS
  # Vacancy20ParamsPayoutFrequency values.

cls Vacancy20ParamsRegistrationMethod(StrEnum): TRUDOVOI_DOGOVOR, GPH_S_IP, GPH_S_SAMOZANYATYM, GPH_S_FIZICHESKIM_LITSOM
  # Vacancy20ParamsRegistrationMethod values.

cls Vacancy20ParamsRetailEquipmentType(StrEnum): KASSA_I_POS_TERMINALY, PROGRAMMY_UCHETA_TOVAROV
  # Vacancy20ParamsRetailEquipmentType values.

cls Vacancy20ParamsRetailShopType(StrEnum): GIPERMARKET_ILI_SUPERMARKET, PRODUKTOVYI, ELEKTRONIKA_I_BYTOVAYA_TEHNIKA, ODEZHDA_I_OBUV, PARFYUMERIYA_I_KOSMETIKA, STROITELSTVO_I_HOZTOVARY, DETSKIE_TOVARY, SPORTIVNYE_TOVARY, ZOOMAGAZIN, APTEKA, DRUGOE
  # Vacancy20ParamsRetailShopType values.

cls Vacancy20ParamsSchedule(StrEnum): V_5_2, V_6_1, VAHTA, GIBKII, SMENNYI, POLNYI_DEN, NEPOLNYI_DEN, FIKSIROVANNYI, UDALENNAYA_RABOTA
  # Vacancy20ParamsSchedule values.

cls Vacancy20ParamsTaxes(StrEnum): DO_VYCHETA_NALOGOV, NA_RUKI
  # Vacancy20ParamsTaxes values.

cls Vacancy20ParamsToolsAvailability(StrEnum): NUZHNY_SVOI, PREDOSTAVLYAET_RABOTODATEL
  # Vacancy20ParamsToolsAvailability values.

cls Vacancy20ParamsWorkerClass(StrEnum): V_1, V_2, V_3, V_4, V_5_I_VYSHE, NE_TREBUETSYA
  # Vacancy20ParamsWorkerClass values.

cls VacancyCreateAgePreferences(StrEnum): OLDERTHAN45, OLDERTHAN14, OLDERTHAN16, WITHHEALTHPROBLEMS, STUDENTS, PENSIONERS
  # VacancyCreateAgePreferences values.

cls VacancyCreateBillingType(StrEnum): PACKAGE, SINGLE, PACKAGEORSINGLE
  # VacancyCreateBillingType values.

cls BonusesValue(StrEnum): PROZIVANIE, PITANIE, MEDICINSKAIA_STRAXOVKA, UNIFORM, OPLATA_BENZINA, TRANSPORT_DO_RABOTY, SKIDKI_V_KOMPANII, PARKOVKA, ZONY_OTDYXA, PODARKI_DETIAM_NA_PRAZDNIKI, OPLATA_MOBILNOI_SVIAZI, OBUCHENIE, KOMPENSACIYA_PROEZDA_S_RABOTI, KASKO, SMARTPHONE, … (16)
  # BonusesValue values.

cls CitizenshipCriteriaValue(StrEnum): RUS, BLR, KAZ, KGZ, TJK, ARM, UZB, UKR
  # CitizenshipCriteriaValue values.

cls ConstructionWorkTypeValue(StrEnum): PAINTINGWORKS, WALLCOVERING, TILEWORK, MOUNTINGANDINSTALLATION, FINISHINGWORK, ROOFING, INSTALLATIONANDCONFIGURATIONOFEQUIPMENT, WELDINGWORK, CONSTRUCTIONOFFACADES, FORMINGMATERIALS, CONCRETEANDSTONEWORKS, REPAIRWORK, OTHER
  # ConstructionWorkTypeValue values.

cls CuisineValue(StrEnum): RUSSIAN, EUROPEAN, CAUCASIAN, ITALIAN, JAPANESE, TURKISH, OTHER
  # CuisineValue values.

cls VacancyCreateDeliveryMethod(StrEnum): CAR, BIKE, SCOOTER, FOOT
  # VacancyCreateDeliveryMethod values.

cls VacancyCreateDescription(StrEnum): P, UL, OL, LI, BR, STRONG, EM
  # VacancyCreateDescription values.

cls VacancyCreateDrivingExperienceId(StrEnum): NOEXPERIENCE, LESSTHAN1, V_1_2, V_3_5, V_6_10, MORETHAN10
  # VacancyCreateDrivingExperienceId values.

cls EateryTypeValue(StrEnum): CAFE, BAR, FASTFOOD, RESTAURANT, CANTEEN, BAKERY, OTHER
  # EateryTypeValue values.

cls VacancyCreateExperienceId(StrEnum): NOMATTER, MORETHAN1, MORETHAN3, MORETHAN5, MORETHAN10
  # VacancyCreateExperienceId values.

cls FacilityTypeValue(StrEnum): PRODUCTION, LOGISTICSCENTER, WAREHOUSE, OTHER
  # FacilityTypeValue values.

cls FoodProductionShopTypeValue(StrEnum): COLD, HOT, CONFECTIONERY, PREPARATION, OTHER
  # FoodProductionShopTypeValue values.

cls VacancyCreatePayoutFrequencyId(StrEnum): DAILYPAY, WEEKLYPAY, BIWEEKLYPAY, THRICEMONTHLYPAY, MONTHLYPAY
  # VacancyCreatePayoutFrequencyId values.

cls RegistrationMethodValue(StrEnum): CONTRACT, GPH_IP, GPH_SELF_EMPLOYED, GPH_INDIVIDUAL
  # RegistrationMethodValue values.

cls RetailEquipmentTypeValue(StrEnum): CASHREGISTERANDPOSTERMINALS, ACCOUNTINGSOFTWARE
  # RetailEquipmentTypeValue values.

cls RetailShopTypeValue(StrEnum): HYPERMARKETORSUPERMARKET, GROCERY, ELECTRONICSANDHOUSEHOLDAPPLIANCES, CLOTHESANDSHOES, PERFUMESANDCOSMETICS, CONSTRUCTIONANDHOUSEHOLDGOODS, CHILDRENGOODS, SPORTINGGOODS, PETSHOP, PHARMACY, OTHER
  # RetailShopTypeValue values.

cls VacancyCreateScheduleId(StrEnum): FLYINFLYOUT, FIXED, FLEXIBLE, SHIFT
  # VacancyCreateScheduleId values.

cls VacancyCreateWorkFormat(StrEnum): OFFICE, REMOTE, GIBRID
  # VacancyCreateWorkFormat values.

cls WorkerClassValue(StrEnum): V_1, V_2, V_3, V_4, V_5ANDHIGHER, NOTNEEDED
  # WorkerClassValue values.

cls VacancyEducationLevel(StrEnum): NOTMATTER, SECONDARY, HIGHER
  # VacancyEducationLevel values.

cls VacancyProlongateBillingType(StrEnum): PACKAGE, SINGLE, PACKAGEORSINGLE
  # VacancyProlongateBillingType values.

cls VacancyStatusesResultRootVacancyModerationStatus(StrEnum): IN_PROGRESS, ALLOWED, BLOCKED, REJECTED
  # VacancyStatusesResultRootVacancyModerationStatus values.

cls VacancyStatusesResultRootVacancyStatus(StrEnum): CREATED, ACTIVATED, ARCHIVED, BLOCKED, CLOSED, EXPIRED, REJECTED, UNBLOCKED
  # VacancyStatusesResultRootVacancyStatus values.

cls VacancyUpdateAgePreferences(StrEnum): OLDERTHAN45, OLDERTHAN14, OLDERTHAN16, WITHHEALTHPROBLEMS, STUDENTS, PENSIONERS
  # VacancyUpdateAgePreferences values.

cls VacancyUpdateBillingType(StrEnum): PACKAGE, SINGLE, PACKAGEORSINGLE
  # VacancyUpdateBillingType values.

cls VacancyUpdateDeliveryMethod(StrEnum): CAR, BIKE, SCOOTER, FOOT
  # VacancyUpdateDeliveryMethod values.

cls VacancyUpdateDescription(StrEnum): P, UL, OL, LI, BR, STRONG, EM
  # VacancyUpdateDescription values.

cls VacancyUpdateDrivingExperienceId(StrEnum): NOEXPERIENCE, LESSTHAN1, V_1_2, V_3_5, V_6_10, MORETHAN10
  # VacancyUpdateDrivingExperienceId values.

cls VacancyUpdateExperienceId(StrEnum): NOMATTER, MORETHAN1, MORETHAN3, MORETHAN5, MORETHAN10
  # VacancyUpdateExperienceId values.

cls VacancyUpdatePayoutFrequencyId(StrEnum): DAILYPAY, WEEKLYPAY, BIWEEKLYPAY, THRICEMONTHLYPAY, MONTHLYPAY
  # VacancyUpdatePayoutFrequencyId values.

cls VacancyUpdateWorkFormat(StrEnum): OFFICE, REMOTE, GIBRID
  # VacancyUpdateWorkFormat values.

cls VacancyV2CreateAgePreferences(StrEnum): OLDERTHAN45, OLDERTHAN14, OLDERTHAN16, WITHHEALTHPROBLEMS, STUDENTS, PENSIONERS
  # VacancyV2CreateAgePreferences values.

cls VacancyV2CreateBillingType(StrEnum): PACKAGE, PACKAGEORSINGLE
  # VacancyV2CreateBillingType values.

cls VacancyV2CreateDeliveryMethod(StrEnum): CAR, BIKE, SCOOTER, FOOT
  # VacancyV2CreateDeliveryMethod values.

cls VacancyV2CreateDescription(StrEnum): P, UL, OL, LI, BR, STRONG, EM
  # VacancyV2CreateDescription values.

cls VacancyV2CreateDrivingExperience(StrEnum): NOEXPERIENCE, LESSTHAN1, V_1_2, V_3_5, V_6_10, MORETHAN10
  # VacancyV2CreateDrivingExperience values.

cls VacancyV2CreateExperience(StrEnum): NOMATTER, MORETHAN1, MORETHAN3, MORETHAN5, MORETHAN10
  # VacancyV2CreateExperience values.

cls VacancyV2CreatePayoutFrequency(StrEnum): DAILYPAY, WEEKLYPAY, BIWEEKLYPAY, THRICEMONTHLYPAY, MONTHLYPAY
  # VacancyV2CreatePayoutFrequency values.

cls VacancyV2CreatePrograms(StrEnum): CHASTYEVYPLATY
  # VacancyV2CreatePrograms values.

cls VacancyV2CreateSchedule(StrEnum): FLYINFLYOUT, FIXED, FLEXIBLE, SHIFT
  # VacancyV2CreateSchedule values.

cls VacancyV2CreateWorkFormat(StrEnum): OFFICE, REMOTE, GIBRID
  # VacancyV2CreateWorkFormat values.

cls WorkerClassRoot(StrEnum): V_1, V_2, V_3, V_4, V_5ANDHIGHER, NOTNEEDED
  # WorkerClassRoot values.

cls ResumesGetFields(StrEnum): TITLE, LOCATION, SPECIALIZATION, EDUCATION_LEVEL, TOTAL_EXPERIENCE, GENDER, AGE, SALARY, ADDRESS_DETAILS, IS_PURCHASED, CREATED_AT, UPDATED_AT, NATIONALITY, DRIVER_LICENCE, DRIVER_LICENCE_CATEGORY, … (18)
  # ResumesGetFields values.

cls ResumesGetSchedule(StrEnum): PARTIAL_DAY, FULL_DAY, FLY_IN_FLY_OUT, FLEXIBLE, SHIFT, REMOTE
  # ResumesGetSchedule values.

cls ResumesGetBusinessTripReadiness(StrEnum): READY, NEVER, SOMETIMES
  # ResumesGetBusinessTripReadiness values.

cls ResumesGetRelocationReadiness(StrEnum): POSSIBLE, NEVER
  # ResumesGetRelocationReadiness values.

cls ResumesGetGender(StrEnum): FEMALE, MALE
  # ResumesGetGender values.

cls ResumesGetEducationLevel(StrEnum): HIGHER, UNFINISHED_HIGHER, SECONDARY, SPECIAL_SECONDARY
  # ResumesGetEducationLevel values.

cls ResumesGetDriverLicence(StrEnum): TRUE, FALSE
  # ResumesGetDriverLicence values.

cls ResumesGetDriverLicenceCategory(StrEnum): A, B, BE, C, CE, D, DE, M, TM, TB
  # ResumesGetDriverLicenceCategory values.

cls ResumesGetDrivingExperience(StrEnum): LESS_THAN_THREE_YEARS, MORE_THAN_THREE_YEARS
  # ResumesGetDrivingExperience values.

cls ResumesGetOwnTransport(StrEnum): FALSE, CAR, CARGO_CAR, BIKE, SCOOTER
  # ResumesGetOwnTransport values.

cls ResumesGetMedicalBook(StrEnum): TRUE, FALSE
  # ResumesGetMedicalBook values.

cls VacancyCreate2AgePreferences(StrEnum): OLDERTHAN45, OLDERTHAN14, OLDERTHAN16, WITHHEALTHPROBLEMS, STUDENTS, PENSIONERS
  # VacancyCreate2AgePreferences values.

cls VacancyCreate2BillingType(StrEnum): PACKAGE, SINGLE, PACKAGEORSINGLE
  # VacancyCreate2BillingType values.

cls VacancyCreate2DeliveryMethod(StrEnum): CAR, BIKE, SCOOTER, FOOT
  # VacancyCreate2DeliveryMethod values.

cls VacancyCreate2Description(StrEnum): P, UL, OL, LI, BR, STRONG, EM
  # VacancyCreate2Description values.

cls VacancyCreate2DrivingExperienceId(StrEnum): NOEXPERIENCE, LESSTHAN1, V_1_2, V_3_5, V_6_10, MORETHAN10
  # VacancyCreate2DrivingExperienceId values.

cls VacancyCreate2ExperienceId(StrEnum): NOMATTER, MORETHAN1, MORETHAN3, MORETHAN5, MORETHAN10
  # VacancyCreate2ExperienceId values.

cls VacancyCreate2PayoutFrequencyId(StrEnum): DAILYPAY, WEEKLYPAY, BIWEEKLYPAY, THRICEMONTHLYPAY, MONTHLYPAY
  # VacancyCreate2PayoutFrequencyId values.

cls VacancyCreate2ScheduleId(StrEnum): FLYINFLYOUT, FIXED, FLEXIBLE, SHIFT
  # VacancyCreate2ScheduleId values.

cls VacancyCreate2WorkFormat(StrEnum): OFFICE, REMOTE, GIBRID
  # VacancyCreate2WorkFormat values.

cls VacancyUpdate2AgePreferences(StrEnum): OLDERTHAN45, OLDERTHAN14, OLDERTHAN16, WITHHEALTHPROBLEMS, STUDENTS, PENSIONERS
  # VacancyUpdate2AgePreferences values.

cls VacancyUpdate2BillingType(StrEnum): PACKAGE, SINGLE, PACKAGEORSINGLE
  # VacancyUpdate2BillingType values.

cls VacancyUpdate2DeliveryMethod(StrEnum): CAR, BIKE, SCOOTER, FOOT
  # VacancyUpdate2DeliveryMethod values.

cls VacancyUpdate2Description(StrEnum): P, UL, OL, LI, BR, STRONG, EM
  # VacancyUpdate2Description values.

cls VacancyUpdate2DrivingExperienceId(StrEnum): NOEXPERIENCE, LESSTHAN1, V_1_2, V_3_5, V_6_10, MORETHAN10
  # VacancyUpdate2DrivingExperienceId values.

cls VacancyUpdate2ExperienceId(StrEnum): NOMATTER, MORETHAN1, MORETHAN3, MORETHAN5, MORETHAN10
  # VacancyUpdate2ExperienceId values.

cls VacancyUpdate2PayoutFrequencyId(StrEnum): DAILYPAY, WEEKLYPAY, BIWEEKLYPAY, THRICEMONTHLYPAY, MONTHLYPAY
  # VacancyUpdate2PayoutFrequencyId values.

cls VacancyUpdate2WorkFormat(StrEnum): OFFICE, REMOTE, GIBRID
  # VacancyUpdate2WorkFormat values.

cls VacancyProlongate2BillingType(StrEnum): PACKAGE, SINGLE, PACKAGEORSINGLE
  # VacancyProlongate2BillingType values.

cls ResumeGetItemFields(StrEnum): ADDRESS_DETAILS, DESCRIPTION, IS_ACTIVE, IS_PURCHASED, SALARY, START_TIME, TITLE, UPDATE_TIME, URL
  # ResumeGetItemFields values.

cls ResumeGetItemParams(StrEnum): ABILITY_TO_BUSINESS_TRIP, ADDRESS, AGE, BUSINESS_AREA, DRIVER_LICENCE, DRIVER_LICENCE_CATEGORY, EDUCATION, EDUCATION_LIST, EXPERIENCE, EXPERIENCE_LIST, LANGUAGE_LIST, MOVING, NATIONALITY, POL, RAZRESHENIE_NA_RABOTU_V_ROSSII, … (16)
  # ResumeGetItemParams values.

cls VacancyCreateV2AgePreferences(StrEnum): OLDERTHAN45, OLDERTHAN14, OLDERTHAN16, WITHHEALTHPROBLEMS, STUDENTS, PENSIONERS
  # VacancyCreateV2AgePreferences values.

cls VacancyCreateV2BillingType(StrEnum): PACKAGE, PACKAGEORSINGLE
  # VacancyCreateV2BillingType values.

cls VacancyCreateV2DeliveryMethod(StrEnum): CAR, BIKE, SCOOTER, FOOT
  # VacancyCreateV2DeliveryMethod values.

cls VacancyCreateV2Description(StrEnum): P, UL, OL, LI, BR, STRONG, EM
  # VacancyCreateV2Description values.

cls VacancyCreateV2DrivingExperience(StrEnum): NOEXPERIENCE, LESSTHAN1, V_1_2, V_3_5, V_6_10, MORETHAN10
  # VacancyCreateV2DrivingExperience values.

cls VacancyCreateV2Experience(StrEnum): NOMATTER, MORETHAN1, MORETHAN3, MORETHAN5, MORETHAN10
  # VacancyCreateV2Experience values.

cls VacancyCreateV2PayoutFrequency(StrEnum): DAILYPAY, WEEKLYPAY, BIWEEKLYPAY, THRICEMONTHLYPAY, MONTHLYPAY
  # VacancyCreateV2PayoutFrequency values.

cls VacancyCreateV2Programs(StrEnum): CHASTYEVYPLATY
  # VacancyCreateV2Programs values.

cls VacancyCreateV2Schedule(StrEnum): FLYINFLYOUT, FIXED, FLEXIBLE, SHIFT
  # VacancyCreateV2Schedule values.

cls VacancyCreateV2WorkFormat(StrEnum): OFFICE, REMOTE, GIBRID
  # VacancyCreateV2WorkFormat values.

cls VacanciesGetByIdsFields(StrEnum): TITLE, DESCRIPTION, URL, SALARY, START_TIME, UPDATE_TIME, IS_ACTIVE
  # VacanciesGetByIdsFields values.

cls VacanciesGetByIdsParams(StrEnum): ADDRESS, ADMINISTRATOR_ORGANIZATION_TYPE, AGE_PREFERENCES, APPLIES_FILTER, BONUSES, BUSINESS_AREA, CHANGE, CITIZENSHIP, CONSTRUCTION_WORK_TYPE, COORDINATES, CUISINE, DELIVERY_METHOD, DRIVING_EXPERIENCE, DRIVING_LICENSE_CATEGORY, EATERY_TYPE, … (51)
  # VacanciesGetByIdsParams values.

cls VacancyUpdateV2AgePreferences(StrEnum): OLDERTHAN45, OLDERTHAN14, OLDERTHAN16, WITHHEALTHPROBLEMS, STUDENTS, PENSIONERS
  # VacancyUpdateV2AgePreferences values.

cls VacancyUpdateV2BillingType(StrEnum): PACKAGE, PACKAGEORSINGLE
  # VacancyUpdateV2BillingType values.

cls VacancyUpdateV2DeliveryMethod(StrEnum): CAR, BIKE, SCOOTER, FOOT
  # VacancyUpdateV2DeliveryMethod values.

cls VacancyUpdateV2Description(StrEnum): P, UL, OL, LI, BR, STRONG, EM
  # VacancyUpdateV2Description values.

cls VacancyUpdateV2DrivingExperience(StrEnum): NOEXPERIENCE, LESSTHAN1, V_1_2, V_3_5, V_6_10, MORETHAN10
  # VacancyUpdateV2DrivingExperience values.

cls VacancyUpdateV2Experience(StrEnum): NOMATTER, MORETHAN1, MORETHAN3, MORETHAN5, MORETHAN10
  # VacancyUpdateV2Experience values.

cls VacancyUpdateV2PayoutFrequency(StrEnum): DAILYPAY, WEEKLYPAY, BIWEEKLYPAY, THRICEMONTHLYPAY, MONTHLYPAY
  # VacancyUpdateV2PayoutFrequency values.

cls VacancyUpdateV2Programs(StrEnum): CHASTYEVYPLATY
  # VacancyUpdateV2Programs values.

cls VacancyUpdateV2Schedule(StrEnum): FLYINFLYOUT, FIXED, FLEXIBLE, SHIFT
  # VacancyUpdateV2Schedule values.

cls VacancyUpdateV2WorkFormat(StrEnum): OFFICE, REMOTE, GIBRID
  # VacancyUpdateV2WorkFormat values.

cls VacancyGetItemFields(StrEnum): DESCRIPTION, IS_ACTIVE, SALARY, START_TIME, TITLE, UPDATE_TIME, URL
  # VacancyGetItemFields values.

cls VacancyGetItemParams(StrEnum): ADDRESS, ADMINISTRATOR_ORGANIZATION_TYPE, AGE_PREFERENCES, APPLIES_FILTER, BONUSES, BUSINESS_AREA, CHANGE, CITIZENSHIP, CONSTRUCTION_WORK_TYPE, COORDINATES, CUISINE, DELIVERY_METHOD, DRIVING_EXPERIENCE, DRIVING_LICENSE_CATEGORY, EATERY_TYPE, … (51)
  # VacancyGetItemParams values.

```

## messenger.py
```
# Мессенджер — domain enums (auto-generated from the Avito OpenAPI spec).


cls MessageContentCallStatus(StrEnum): MISSED
  # MessageContentCallStatus values.

cls MessageContentLocationKind(StrEnum): HOUSE, STREET, AREA, EMPTY
  # MessageContentLocationKind values.

cls MessageQuoteType(StrEnum): TEXT, IMAGE, LINK, ITEM, LOCATION, CALL, DELETED, VOICE, SYSTEM
  # MessageQuoteType values.

cls MessagesRootDirection(StrEnum): IN, OUT
  # MessagesRootDirection values.

cls MessagesRootType(StrEnum): TEXT, IMAGE, LINK, ITEM, LOCATION, CALL, DELETED, VOICE, SYSTEM
  # MessagesRootType values.

cls WebhookMessageChatType(StrEnum): U2I, U2U, A2U
  # WebhookMessageChatType values.

cls WebhookMessageType(StrEnum): TEXT, IMAGE, SYSTEM, ITEM, CALL, LINK, LOCATION, DELETED, APPCALL, FILE, VIDEO, VOICE
  # WebhookMessageType values.

cls SendMessageRequestBodyType(StrEnum): TEXT
  # SendMessageRequestBodyType values.

cls PostSendMessageType(StrEnum): TEXT
  # PostSendMessageType values.

cls GetChatsV2ChatTypes(StrEnum): U2I, U2U, A2U
  # GetChatsV2ChatTypes values.

```

## order_management.py
```
# Управление заказами — domain enums (auto-generated from the Avito OpenAPI spec).


cls ActionName(StrEnum): SETMARKINGS, SETCNCDETAILS, SETTRACKNUMBER, FIXTRACKNUMBER, ACCEPTRETURNORDER, CONFIRM, REJECT, PERFORM, RECEIVE
  # ActionName values.

cls DeliveryServiceType(StrEnum): PVZ, DBS, RDBS
  # DeliveryServiceType values.

cls DiscountType(StrEnum): PROMOCODE
  # DiscountType values.

cls OrderApplyTransitionRequestTransition(StrEnum): CONFIRM, REJECT, PERFORM, RECEIVE
  # OrderApplyTransitionRequestTransition values.

cls OrderCheckConfirmationCodeResponseDataStatus(StrEnum): SUCCESS, FAIL, EXPIRED, ATTEMPTS
  # OrderCheckConfirmationCodeResponseDataStatus values.

cls OrderSetTrackingNumberResponseErrorCode(StrEnum): INCORRECT_NUMBER, ALREADY_SET
  # OrderSetTrackingNumberResponseErrorCode values.

cls ReturnPolicyReturnStatus(StrEnum): IN_TRANSIT, READY_TO_PICKUP, SELF_RETURN
  # ReturnPolicyReturnStatus values.

cls SetCourierDeliveryRangeRequestIntervalType(StrEnum): FIXED, ASAP
  # SetCourierDeliveryRangeRequestIntervalType values.

cls Status(StrEnum): ON_CONFIRMATION, READY_TO_SHIP, IN_TRANSIT, CANCELED, DELIVERED, ON_RETURN, IN_DISPUTE, CLOSED
  # Status values.

cls ApplyTransitionTransition(StrEnum): CONFIRM, REJECT, PERFORM, RECEIVE
  # ApplyTransitionTransition values.

cls SetCourierDeliveryRangeIntervalType(StrEnum): FIXED, ASAP
  # SetCourierDeliveryRangeIntervalType values.

```

## promotion.py
```
# Продвижение — domain enums (auto-generated from the Avito OpenAPI spec).


cls CommonErrorDetailsSource(StrEnum): HEADER, URL, QUERY, BODY
  # CommonErrorDetailsSource values.

cls OrderServiceStatus(StrEnum): UNKNOWN, ACTIVE, ERROR, CANCELED, PROCESSED
  # OrderServiceStatus values.

cls OrderStatus(StrEnum): UNKNOWN, INITIALIZED, WAITING, IN_PROCESS, PROCESSED
  # OrderStatus values.

```

## realty_reports.py
```
# Аналитика по недвижимости — domain enums (auto-generated from the Avito OpenAPI spec).


cls MarketPriceCorrespondenceV1ResponseCorrespondence(StrEnum): BELOW, NORMAL, ABOVE
  # MarketPriceCorrespondenceV1ResponseCorrespondence values.

```

## reviews.py
```
# Рейтинги и отзывы — domain enums (auto-generated from the Avito OpenAPI spec).


cls ReviewStage(StrEnum): DONE, FELL_THROUGH, NOT_AGREE, NOT_COMMUNICATE
  # ReviewStage values.

cls ReviewAnswerStatus(StrEnum): MODERATION, PUBLISHED, REJECTED
  # ReviewAnswerStatus values.

```

## short_term_rental.py
```
# Краткосрочная аренда — domain enums (auto-generated from the Avito OpenAPI spec).


cls BaseParamsFeesPetsApplication(StrEnum): BY_BOOKING, BY_NIGHT
  # BaseParamsFeesPetsApplication values.

cls PostCalendarDataBookingsType(StrEnum): MANUAL, BOOKING
  # PostCalendarDataBookingsType values.

cls RealtyBookingStatus(StrEnum): ACTIVE, CANCELED, PENDING
  # RealtyBookingStatus values.

cls PutBookingsInfoResponseResult(StrEnum): SUCCESS
  # PutBookingsInfoResponseResult values.

cls PutBookingsInfoBookingsType(StrEnum): MANUAL, BOOKING
  # PutBookingsInfoBookingsType values.

cls PostRealtyPricesResponseResult(StrEnum): SUCCESS
  # PostRealtyPricesResponseResult values.

cls PutIntervalsResponseResult(StrEnum): SUCCESS
  # PutIntervalsResponseResult values.

cls PostBaseParamsFeesPetsApplication(StrEnum): BY_BOOKING, BY_NIGHT
  # PostBaseParamsFeesPetsApplication values.

```

## special_offers.py
```
# Рассылка скидок и спецпредложений в мессенджере (beta-version) — domain enums (auto-generated from the Avito OpenAPI spec).


cls OpenApiMultiCreateResponseBodyCommonOffersType(StrEnum): DISCOUNT, TEXT
  # OpenApiMultiCreateResponseBodyCommonOffersType values.

cls OpenApiMultiCreateResponseBodyDispatchesStatus(StrEnum): NOTCREATED, CREATED
  # OpenApiMultiCreateResponseBodyDispatchesStatus values.

```

## stock_management.py
```
# Управление остатками — domain enums (auto-generated from the Avito OpenAPI spec).


```

## tariff.py
```
# Тарифы — domain enums (auto-generated from the Avito OpenAPI spec).


```

## trxpromo.py
```
# TrxPromo — domain enums (auto-generated from the Avito OpenAPI spec).


```

## user.py
```
# Информация о пользователе — domain enums (auto-generated from the Avito OpenAPI spec).


cls ResponseOperationsHistoryItemOperationType(StrEnum): SPISANIE_V_SCHET_KREDITA, POSTOPLATA, VNESENIE_CPA_AVANSA, VOZVRAT_CPA_AVANSA, AVANS, VOZVRAT_AVANSA, SPISANIE_SREDSTV_S_KOSHELKA_V_DOHOD_NE_ZA_OKAZANNYE_USLUGI, SZHIGANIE_BONUSOV, REZERVIROVANIE_POD_AVTOSTRATEGIYU, VOZVRAT_ZAREZERVIROVANNYH_SREDSTV_POD_AVTOSTATEGIYU_NA_KOSHELEK, REZERVIROVANIE_SREDSTV_POD_USLUGU, VOZVRAT_ZARZERVIROVANNYH_SREDSTV_NA_BALANS_KOSHELKA, PRIZNANIE_VYRUCHKI, SPISANIE_OSTATKA, STORNO, … (17)
  # ResponseOperationsHistoryItemOperationType values.

cls ResponseOperationsHistoryItemServiceType(StrEnum): VAS, PERF_VAS, LF, CV, TARIFF, SUBSCRIPTION, CPA, BUNDLE
  # ResponseOperationsHistoryItemServiceType values.

```

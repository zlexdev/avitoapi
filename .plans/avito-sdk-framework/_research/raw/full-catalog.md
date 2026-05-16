# Avito Partner API — Full Domain Catalog (scraped from developers.avito.ru)

Date: 2026-05-17. Source: every domain's `/documentation` page on `developers.avito.ru`, captured live via Playwright. The earlier dossier had to infer from third-party clients; this one is authoritative.

## 24 domains in the public catalog

| Slug | RU title | Endpoints | Status in SDK |
|---|---|---|---|
| accounts-hierarchy | Иерархия Аккаунтов | 5 | **missing** |
| auction | CPA-аукцион | 2 | **missing** |
| auth | Авторизация | (OAuth, in W1) | covered |
| autoload | Автозагрузка | ~10 | covered (W6) |
| autostrategy | Автостратегия | 7 | **missing** |
| autoteka | Автотека | 3 | covered (W6) |
| calltracking | CallTracking[КТ] | 3 | covered (W6) |
| cpa | CPA Авито | 7 | covered (W5) |
| cpxpromo | Настройка цены целевого действия | 5 | **missing** |
| delivery-sandbox | Доставка | 31 | **missing** |
| item | Объявления | 9 | covered (W2) |
| job | Авито.Работа | 3 | covered (W6) |
| messenger | Мессенджер | 13 | covered (W3) — 3 webhook lifecycle missing |
| order-management | Управление заказами | 12 | **missing** (distinct from cpa/orders!) |
| promotion | Продвижение | 5 | covered (W5) |
| ratings | Рейтинги и отзывы | 4 | covered (W5) |
| realty-reports | Аналитика по недвижимости | 2 | **missing** |
| sbc-gateway | Рассылка скидок (special-offers) | 5 | **missing** |
| stock-management | Управление остатками | 2 | **missing** |
| str | Краткосрочная аренда | ~5 | covered (W6 realty) |
| tariff | Тарифы | 1 | **missing** |
| trxpromo | TrxPromo | 3 | **missing** |
| user | Информация о пользователе | 3 | covered (W2 balance/accounts) |

## New endpoints (Wave 7)

### accounts-hierarchy (5)
- `GET  /checkAhUserV1`
- `GET  /getEmployeesV1`
- `POST /linkItemsV1`
- `GET  /listCompanyPhonesV1`
- `POST /listItemsByEmployeeIdV1`

### auction (2)
- `GET  /auction/1/bids`
- `POST /auction/1/bids`

### autostrategy (7)
- `POST /autostrategy/v1/budget`
- `POST /autostrategy/v1/campaign/create`
- `POST /autostrategy/v1/campaign/edit`
- `POST /autostrategy/v1/campaign/info`
- `POST /autostrategy/v1/campaign/stop`
- `POST /autostrategy/v1/campaigns`
- `POST /autostrategy/v1/stat`

### cpxpromo (5)
- `GET  /cpxpromo/1/getBids/{itemId}`
- `POST /cpxpromo/1/getPromotionsByItemIds`
- `POST /cpxpromo/1/remove`
- `POST /cpxpromo/1/setAuto`
- `POST /cpxpromo/1/setManual`

### delivery-sandbox (31 — Avito Доставка integration)
- `POST /createParcel`
- `POST /delivery-sandbox/tariffs/{tariff_id}/areas`
- `POST /delivery-sandbox/tariffs/{tariff_id}/terms`
- `POST /delivery-sandbox/tariffsV2`
- `POST /delivery-sandbox/areas/custom-schedule`
- `POST /delivery-sandbox/tariffs/{tariff_id}/terminals`
- `GET  /delivery-sandbox/tasks/{task_id}`
- `POST /delivery-sandbox/cancelParcel`
- `POST /delivery-sandbox/order/checkConfirmationCode`
- `POST /delivery-sandbox/order/properties`
- `POST /delivery-sandbox/order/realAddress`
- `POST /delivery-sandbox/order/tracking`
- `POST /delivery-sandbox/prohibitOrderAcceptance`
- `POST /delivery/order/changeParcelResult`
- `POST /sandbox/changeParcels`
- `POST /cancelAnnouncement`
- `POST /createAnnouncement`
- `POST /delivery-sandbox/announcements/create`
- `POST /delivery-sandbox/announcements/track`
- `GET  /delivery-sandbox/sorting-center`
- `POST /delivery-sandbox/tariffs/sorting-center`
- `POST /delivery-sandbox/tariffs/{tariff_id}/tagged-sorting-centers`
- `POST /delivery-sandbox/v1/cancelAnnouncement`
- `POST /delivery-sandbox/v1/cancelParcel`
- `POST /delivery-sandbox/v1/changeParcel`
- `POST /delivery-sandbox/v1/createAnnouncement`
- `POST /delivery-sandbox/v1/getAnnouncementEvent`
- `POST /delivery-sandbox/v1/getChangeParcelInfo`
- `POST /delivery-sandbox/v1/getParcelInfo`
- `POST /delivery-sandbox/v1/getRegisteredParcelID`
- `POST /delivery-sandbox/v2/createParcel`

### order-management (12) — distinct from CPA orders
- `POST /order-management/1/markings`
- `POST /order-management/1/order/acceptReturnOrder`
- `POST /order-management/1/order/applyTransition`
- `POST /order-management/1/order/checkConfirmationCode`
- `POST /order-management/1/order/cncSetDetails`
- `GET  /order-management/1/order/getCourierDeliveryRange`
- `POST /order-management/1/order/setCourierDeliveryRange`
- `POST /order-management/1/order/setTrackingNumber`
- `GET  /order-management/1/orders`
- `POST /order-management/1/orders/labels`
- `POST /order-management/1/orders/labels/extended`
- `GET  /order-management/1/orders/labels/{taskID}/download`

### realty-reports (2)
- `GET  /realty/v1/marketPriceCorrespondence/{itemId}/{price}`
- `POST /realty/v1/report/create/{itemId}`

### sbc-gateway / special-offers (5)
- `POST /special-offers/v1/available`
- `POST /special-offers/v1/multiConfirm`
- `POST /special-offers/v1/multiCreate`
- `POST /special-offers/v1/stats`
- `POST /special-offers/v1/tariffInfo`

### stock-management (2)
- `POST /stock-management/1/info`
- `PUT  /stock-management/1/stocks`

### tariff (1)
- `GET  /tariff/info/1`

### trxpromo (3)
- `POST /trx-promo/1/apply`
- `POST /trx-promo/1/cancel`
- `GET  /trx-promo/1/commissions`

## Messenger webhook lifecycle (missing in W3)
- `POST /messenger/v3/webhook` — register webhook URL (v3)
- `POST /messenger/v1/webhook/unsubscribe` — unsubscribe
- `POST /messenger/v1/subscriptions` — list active subscriptions

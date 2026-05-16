# Avito Partner API — SDK Surface Inventory

Every method-class shipped through Waves 1–6 of the `avitoapi` SDK.
Generated from `avitoapi/methods/*.py` on 2026-05-17.

Wave key:

- W1 — bootstrap (oauth + accounts).
- W2 — items, balance, stats.
- W3 — messenger (chats, messages, blacklist, voice, image upload).
- W5 — orders, reviews, promotion, CPA.
- W6 — autoload, calltracking, job, realty, autoteka (closes the
  documented Avito Partner API surface).

| Method-class | Verb | Endpoint | Returns | Wave |
|---|---|---|---|---|
| `GetSelf` | GET | `/core/v1/accounts/self` | `Account` | W1 |
| `GetBalance` | GET | `/core/v1/accounts/{user_id}/balance/` | `Balance` | W2 |
| `GetBalanceBonus` | GET | `/core/v1/accounts/{user_id}/balance/bonus` | `BalanceBonus` | W2 |
| `OperationsHistory` | POST | `/core/v1/accounts/operations_history/` | `Page[Operation]` | W2 |
| `ListItems` | GET | `/core/v1/items` | `Page[Item]` | W2 |
| `GetItem` | GET | `/core/v1/accounts/{user_id}/items/{item_id}/` | `Item` | W2 |
| `UpdateItemPrice` | PUT | `/core/v1/accounts/{user_id}/items/{item_id}/price` | `Item` | W2 |
| `ApplyVas` | POST | `/core/v1/accounts/{user_id}/price/vas` | `VasOrderResult` | W2 |
| `ApplyVasPackage` | POST | `/core/v1/accounts/{user_id}/price/vas_packages` | `VasOrderResult` | W2 |
| `ApplyVasV2` | PUT | `/core/v2/accounts/{user_id}/items/{item_id}/vas_packages` | `VasOrderResult` | W2 |
| `ArchiveItem` | DELETE | `/core/v1/accounts/{user_id}/items/{item_id}/` | `None` | W2 |
| `ItemStatsShallow` | GET | `/stats/v1/accounts/{user_id}/items/shallow` | `ItemViewStatsList` | W2 |
| `ItemStatsDeep` | POST | `/stats/v1/accounts/{user_id}/items` | `ItemViewStatsList` | W2 |
| `CallStats` | GET | `/stats/v1/accounts/{user_id}/items/{item_id}/calls` | `CallStatList` | W2 |
| `Spendings` | POST | `/stats/v2/accounts/{user_id}/spendings` | `OperationList` | W2 |
| `ListChats` | GET | `/messenger/v2/accounts/{user_id}/chats` | `ChatList` | W3 |
| `GetChat` | GET | `/messenger/v2/accounts/{user_id}/chats/{chat_id}` | `Chat` | W3 |
| `ListMessages` | GET | `/messenger/v3/accounts/{user_id}/chats/{chat_id}/messages/` | `MessageList` | W3 |
| `SendTextMessage` | POST | `/messenger/v1/accounts/{user_id}/chats/{chat_id}/messages` | `MessageEnvelope` | W3 |
| `SendImageMessage` | POST | `/messenger/v1/accounts/{user_id}/chats/{chat_id}/messages/image` | `MessageEnvelope` | W3 |
| `MarkChatRead` | POST | `/messenger/v1/accounts/{user_id}/chats/{chat_id}/read` | `DeleteResult` | W3 |
| `DeleteMessage` | DELETE | `/messenger/v1/accounts/{user_id}/chats/{chat_id}/messages/{message_id}` | `DeleteResult` | W3 |
| `UploadImage` | POST | `/messenger/v1/accounts/{user_id}/uploadImages` | `UploadImageResult` | W3 |
| `ListBlacklist` | GET | `/messenger/v1/accounts/{user_id}/blacklist` | `Blacklist` | W3 |
| `AddBlacklist` | POST | `/messenger/v2/accounts/{user_id}/blacklist` | `DeleteResult` | W3 |
| `RemoveBlacklist` | DELETE | `/messenger/v2/accounts/{user_id}/blacklist/{target_user_id}` | `DeleteResult` | W3 |
| `GetVoiceFiles` | GET | `/messenger/v1/accounts/{user_id}/voice/files` | `VoiceFiles` | W3 |
| `ListOrders` | GET | `/orders/list` | `OrderList` | W5 |
| `GetOrder` | GET | `/orders/{order_id}` | `Order` | W5 |
| `ChangeOrderStatus` | POST | `/orders/{order_id}/status` | `Order` | W5 |
| `TransferDeliveryTerms` | POST | `/orders/{order_id}/delivery_terms` | `Order` | W5 |
| `TransferTrackNumber` | POST | `/orders/{order_id}/track` | `Order` | W5 |
| `RefundOrder` | POST | `/orders/{order_id}/refund` | `Order` | W5 |
| `ListReviews` | GET | `/ratings/v1/reviews` | `ReviewList` | W5 |
| `GetReviewInfo` | GET | `/ratings/v1/info` | `RatingInfo` | W5 |
| `ReplyToReview` | POST | `/ratings/v1/answers` | `ReviewReply` | W5 |
| `DeleteReviewReply` | DELETE | `/ratings/v1/answers/{answer_id}` | `None` | W5 |
| `ListActivePromotions` | GET | `/promotion/v1/items` | `PromotionList` | W5 |
| `DropPromotion` | DELETE | `/promotion/v1/items` | `None` | W5 |
| `ListBids` | GET | `/promotion/v1/items/bids` | `BidList` | W5 |
| `CreateBbipOrder` | PUT | `/promotion/v1/items/services/bbip/orders/create` | `BbipOrder` | W5 |
| `BbipForecast` | GET | `/promotion/v1/items/services/bbip/budget/forecast` | `BbipForecast` | W5 |
| `CpaBalance` | POST | `/cpa/v3/balanceInfo` | `CpaBalanceInfo` | W5 |
| `CallsByTime` | POST | `/cpa/v3/callsByTime` | `CallList` | W5 |
| `ChatsByTime` | POST | `/cpa/v3/chatsByTime` | `ChatList` | W5 |
| `ChatByActionId` | POST | `/cpa/v3/chatByActionId` | `ChatByTime` | W5 |
| `ListComplaints` | GET | `/cpa/v3/complaints` | `ComplaintList` | W5 |
| `CreateComplaint` | POST | `/cpa/v3/complaints` | `Complaint` | W5 |
| `CancelComplaint` | POST | `/cpa/v3/complaints/{complaint_id}/cancel` | `None` | W5 |
| `AutoloadItemStatus` | GET | `/autoload/v1/accounts/{user_id}/items/{ad_id}/` | `AutoloadItemReport` | W6 |
| `ListAutoloadReports` | GET | `/autoload/v1/accounts/{user_id}/reports/` | `Page[AutoloadReport]` | W6 |
| `GetLastAutoloadReport` | GET | `/autoload/v1/accounts/{user_id}/reports/last_report/` | `AutoloadReport` | W6 |
| `GetAutoloadReport` | GET | `/autoload/v1/accounts/{user_id}/reports/{report_id}/` | `AutoloadReport` | W6 |
| `GetAutoloadCategoryFields` | GET | `/autoload/v2/items/category/{category_id}/fields` | `AutoloadCategoryFields` | W6 |
| `GetAutoloadProfile` | GET | `/autoload/v1/profile` | `AutoloadProfile` | W6 |
| `UpdateAutoloadProfile` | PUT | `/autoload/v1/profile` | `AutoloadProfile` | W6 |
| `UploadAutoloadFile` | POST | `/autoload/v1/upload` | `AutoloadUploadResult` | W6 |
| `ConvertAutoloadId` | GET | `/autoload/v1/convert` | `AutoloadIdConversion` | W6 |
| `GetCall` | GET | `/calltracking/v2/calls/{call_id}` | `Call` | W6 |
| `ListCalls` | GET | `/calltracking/v2/calls` | `CallList` | W6 |
| `GetCallRecording` | GET | `/calltracking/v2/calls/{call_id}/recording` | `bytes` (binary) | W6 |
| `SearchResumes` | POST | `/job/v1/resumes/search` | `Page[Resume]` | W6 |
| `GetResume` | GET | `/job/v1/resumes/{resume_id}` | `Resume` | W6 |
| `GetResumeContacts` | POST | `/job/v1/resumes/{resume_id}/contacts` | `ResumeContact` | W6 |
| `ListBookings` | GET | `/realty/v1/bookings` | `BookingList` | W6 |
| `GetCalendar` | GET | `/realty/v1/items/{item_id}/calendar` | `Calendar` | W6 |
| `GetPeriodPrices` | GET | `/realty/v1/items/{item_id}/period_prices` | `PeriodPriceList` | W6 |
| `UpdatePeriodPrices` | PUT | `/realty/v1/items/{item_id}/period_prices` | `None` | W6 |
| `ItemBookings` | GET | `/core/v1/accounts/{user_id}/items/{item_id}/bookings` | `BookingList` | W6 |
| `AutotekaPreviewByVin` | GET | `/autoteka/v1/preview` | `AutotekaPreview` | W6 |
| `AutotekaPreviewByRegnum` | GET | `/autoteka/v1/preview` | `AutotekaPreview` | W6 |
| `AutotekaFullReport` | POST | `/autoteka/v1/report` | `AutotekaFullReport` (model) | W6 |

## Notes

- `GetCallRecording` sets `__binary_response__ = True`; the awaited result is
  raw `bytes` (`audio/mpeg`), not a Pydantic model. The internal returning
  type `_BytesEnvelope` is a sentinel that satisfies the framework's "returning
  must be a `BaseModel`" import-time check.
- `AutotekaFullReport` exists in both `models/autoteka.py` (DTO) and
  `methods/autoteka.py` (method-class). The DTO is imported as
  `AutotekaFullReportDoc` inside the method module to keep the spec naming.
- `Page[T]` is the page envelope from `models/common.py`; `*List` types are
  Pydantic `RootModel` envelopes around bare JSON arrays Avito returns.
- OAuth endpoints (`GET /token/`, `POST /token/refresh`) are not modelled as
  method-classes — they live in `avitoapi/auth/oauth.py` as part of the
  request middleware that injects bearer tokens transparently.

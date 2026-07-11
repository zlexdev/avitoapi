# unit/
<!-- AUTO-GENERATED. Do not edit. Run gen_module_auto.py to update. -->

## test_accounts_hierarchy.py
```
# Unit tests for the accounts-hierarchy domain.

FIXTURES = …

_load(name: str) -> dict[str, Any] | list[Any]

ah_config() -> ClientConfig

async ah_client(ah_config: ClientConfig) -> Any

async test_check_ah_user_decodes_status(ah_client: tuple[Client, FakeSession) -> None

async test_get_employees_returns_envelope(ah_client: tuple[Client, FakeSession) -> None

async test_link_items_posts_body(ah_client: tuple[Client, FakeSession) -> None

async test_list_company_phones_decodes_envelope(ah_client: tuple[Client, FakeSession) -> None

async test_list_items_by_employee_posts_body(ah_client: tuple[Client, FakeSession) -> None

```

## test_assets.py
```
# Unit tests for the :mod:`avitoapi.assets` subsystem.


cls _FakeHttp
  # Minimal ducktype: one ``get`` returning an object with ``status_code`` + ``content``.
  __init__(payloads: dict[str, bytes) -> None
  async get(url: str) -> Any

async test_memory_file_storage_put_get_round_trip() -> None

async test_memory_file_storage_get_missing_returns_none() -> None

async test_memory_file_storage_delete() -> None

async test_memory_file_storage_ttl_expiry() -> None

async test_memory_file_storage_namespaced_isolates() -> None

async test_local_file_storage_put_get_round_trip(tmp_path: Path) -> None

async test_local_file_storage_delete(tmp_path: Path) -> None

async test_local_file_storage_ttl_expiry(tmp_path: Path) -> None

async test_local_file_storage_filenames_are_sha256_hashed(tmp_path: Path) -> None

async test_file_cache_enforces_uniform_ttl() -> None

async test_file_cache_delegates_delete_to_storage() -> None

async test_asset_downloader_caches_after_first_fetch() -> None

async test_asset_downloader_download_many_returns_dict() -> None

async test_asset_downloader_download_many_empty_returns_empty() -> None

async test_asset_downloader_propagates_non_2xx_status() -> None

```

## test_auction.py
```
# Unit tests for the auction (CPA bids) domain.

FIXTURES = …

_load(name: str) -> dict[str, Any] | list[Any]

auc_config() -> ClientConfig

async auc_client(auc_config: ClientConfig) -> Any

async test_get_auction_bids_returns_envelope(auc_client: tuple[Client, FakeSession) -> None

async test_set_auction_bids_posts_and_is_idempotent(auc_client: tuple[Client, FakeSession) -> None

```

## test_autoload.py
```
# Autoload domain — method-class fixture round-trips + binary upload routing.


async test_autoload_item_status_returns_typed_report(client: Client, fake_session: FakeSession) -> None

async test_autoload_item_status_uses_path_template(client: Client, fake_session: FakeSession) -> None

async test_list_autoload_reports_returns_page_envelope(client: Client, fake_session: FakeSession) -> None

async test_get_last_autoload_report_round_trip(client: Client, fake_session: FakeSession) -> None

async test_get_autoload_report_uses_report_id_in_path(client: Client, fake_session: FakeSession) -> None

async test_get_autoload_category_fields_returns_typed_schema(client: Client, fake_session: FakeSession) -> None

async test_get_autoload_profile_returns_dto(client: Client, fake_session: FakeSession) -> None

async test_update_autoload_profile_emits_put_with_idempotency_key(client: Client, fake_session: FakeSession) -> None

async test_upload_autoload_file_carries_bytes_in_body(client: Client, fake_session: FakeSession) -> None

async test_convert_autoload_id_unpacks_top_level_mapping(client: Client, fake_session: FakeSession) -> None

```

## test_autostrategy.py
```
# Autostrategy v1 — budget, campaign CRUD, info, stats round-trips.


async test_set_autostrategy_budget_idempotent(client: Client, fake_session: FakeSession) -> None

async test_create_autostrategy_campaign_idempotent(client: Client, fake_session: FakeSession) -> None

async test_edit_autostrategy_campaign_idempotent(client: Client, fake_session: FakeSession) -> None

async test_get_autostrategy_campaign_info_decodes_extended(client: Client, fake_session: FakeSession) -> None

async test_stop_autostrategy_campaign_idempotent(client: Client, fake_session: FakeSession) -> None

async test_list_autostrategy_campaigns_decodes_list(client: Client, fake_session: FakeSession) -> None

async test_get_autostrategy_stats_decodes_rows(client: Client, fake_session: FakeSession) -> None

async test_campaign_bound_methods_target_correct_endpoints(client: Client, fake_session: FakeSession) -> None

```

## test_autoteka.py
```
# Autoteka — VIN/regnum previews + paid full report (offline fixtures only).


async test_autoteka_preview_by_vin_returns_typed_preview(client: Client, fake_session: FakeSession) -> None

async test_autoteka_preview_by_vin_carries_vin_in_query(client: Client, fake_session: FakeSession) -> None

async test_autoteka_preview_by_regnum_returns_typed_preview(client: Client, fake_session: FakeSession) -> None

async test_autoteka_full_report_round_trip_with_vin(client: Client, fake_session: FakeSession) -> None

async test_autoteka_full_report_emits_post_with_idempotency_key(client: Client, fake_session: FakeSession) -> None

test_autoteka_full_report_rejects_both_identifiers() -> None

test_autoteka_full_report_rejects_neither_identifier() -> None

```

## test_avito_webhook_handler.py
```
# Unit tests for :class:`AvitoWebhookHandler`.


cls _DispatcherStub
  __init__() -> None
  async feed_event(event) -> None

_envelope(kind: str, value: dict) -> dict

async test_parse_new_message()

async test_parse_message_read()

async test_parse_chat_archived()

async test_parse_missing_ids_raises()

async test_parse_unknown_kind_raises()

async test_handle_bad_json_returns_400()

async test_handle_unknown_kind_returns_200_skipped()

async test_handle_dispatches_to_feed_event()

async test_handle_falls_back_to_router_when_no_feed_event()

async test_handle_accepts_dict_directly()

```

## test_breaker.py
```
# Unit tests for the in-package CircuitBreaker + BreakerRegistry.


_cfg(**overrides) -> ClientConfig

async test_breaker_opens_after_threshold()

async test_breaker_half_opens_after_timeout()

async test_breaker_reset_on_success()

async test_breaker_half_open_failure_reopens()

async test_breaker_reset_method()

async test_registry_caches_by_key()

async test_registry_per_account_keying()

async test_threshold_parametrized(threshold: int)

```

## test_calltracking.py
```
# Calltracking — call metadata + binary audio recording streaming.


async test_get_call_returns_typed_call(client: Client, fake_session: FakeSession) -> None

async test_get_call_uses_path_template(client: Client, fake_session: FakeSession) -> None

async test_list_calls_returns_envelope_with_two_rows(client: Client, fake_session: FakeSession) -> None

async test_get_call_recording_returns_raw_bytes(client: Client, fake_session: FakeSession) -> None
  # Validates ``__binary_response__ = True`` short-circuits the JSON decode path.

async test_get_call_recording_path_includes_call_id(client: Client, fake_session: FakeSession) -> None

```

## test_channels.py
```
# Push-channel overflow policies + drain into the dispatcher.


_order(order_id: str) -> OrderCreated

async test_drop_new_rejects_when_full() -> None

async test_drop_oldest_evicts_head() -> None

async test_raise_policy_raises_when_full() -> None

async test_channel_drains_into_dispatcher() -> None

async test_block_policy_backpressures_then_accepts() -> None

```

## test_client.py
```
# Unit tests for ``avitoapi.Client`` — facade, lifecycle, ``__call__``, ``get_user_info_self``.


async test_client_call_returns_account_when_invoked_with_get_self(client: Client) -> None

async test_client_call_binds_returned_model_to_self(client: Client) -> None

async test_get_self_returns_account_with_expected_fields(client: Client, accounts_self_payload: dict[str, Any) -> None

async test_get_self_returns_account_bound_to_client(client: Client) -> None

async test_client_async_with_opens_and_closes_session(client_config: ClientConfig, fake_session: FakeSession, accounts_self_payload: dict[str, Any) -> None

async test_client_reauths_and_retries_when_call_returns_token_expired_403(client_config: ClientConfig, accounts_self_payload: dict[str, Any, oauth_token_payload: dict[str, Any, oauth_token_expired_payload: dict[str, Any) -> None

```

## test_cpa.py
```
# CPA v3 — balance, calls/chats by time, complaints lifecycle round-trips.


async test_cpa_balance_round_trip(client: Client, fake_session: FakeSession) -> None

async test_calls_by_time_round_trip(client: Client, fake_session: FakeSession) -> None

async test_chats_by_time_round_trip(client: Client, fake_session: FakeSession) -> None

async test_chat_by_action_id_round_trip(client: Client, fake_session: FakeSession) -> None

async test_list_complaints_round_trip(client: Client, fake_session: FakeSession) -> None

async test_create_complaint_idempotent(client: Client, fake_session: FakeSession) -> None

async test_cancel_complaint_idempotent(client: Client, fake_session: FakeSession) -> None

async test_complaint_bound_cancel_without_client_raises() -> None

```

## test_cpxpromo.py
```
# CpxPromo v1 — getBids / getPromotionsByItemIds / remove / setAuto / setManual.


async test_get_cpx_bids_uses_path_template(client: Client, fake_session: FakeSession) -> None

async test_get_cpx_promotions_by_items_decodes_modes(client: Client, fake_session: FakeSession) -> None

async test_remove_cpx_promotion_idempotent(client: Client, fake_session: FakeSession) -> None

async test_set_cpx_auto_promotion_idempotent(client: Client, fake_session: FakeSession) -> None

async test_set_cpx_manual_promotion_idempotent_carries_bid(client: Client, fake_session: FakeSession) -> None

async test_cpx_promotion_bound_methods_target_correct_endpoints(client: Client, fake_session: FakeSession) -> None

```

## test_delivery.py
```
# Delivery-sandbox domain — representative method-class round-trips.


async test_create_parcel_returns_parcel(client: Client, fake_session: FakeSession) -> None

async test_create_parcel_injects_idempotency_key(client: Client, fake_session: FakeSession) -> None

async test_cancel_parcel_returns_change_result(client: Client, fake_session: FakeSession) -> None

async test_list_tariffs_v2_returns_root_envelope(client: Client, fake_session: FakeSession) -> None

async test_list_tariff_areas_renders_tariff_id_in_path(client: Client, fake_session: FakeSession) -> None

async test_list_tariff_terminals_path_templating(client: Client, fake_session: FakeSession) -> None

async test_get_delivery_task_returns_task(client: Client, fake_session: FakeSession) -> None

async test_set_area_custom_schedule_returns_generic_result(client: Client, fake_session: FakeSession) -> None

async test_track_announcement_v1_routes_to_v1_endpoint(client: Client, fake_session: FakeSession) -> None

async test_get_parcel_info_v1_round_trip(client: Client, fake_session: FakeSession) -> None

```

## test_dispatch_dedup.py
```
# Dispatch-boundary accept-once: dedup, auto-ack, failure → DLQ + release.


_order(order_id: str = 'o1') -> OrderCreated

async test_redelivered_event_dispatched_once() -> None

async test_distinct_events_both_dispatched() -> None

async test_handler_failure_dlqs_releases_and_acks() -> None

```

## test_dispatcher.py
```
# Unit tests for ``avitoapi.dispatcher``.

_EVENTED_INSTALLED = find_spec('evented') is not None

test_dispatcher_class_exists() -> None
  # Importing Dispatcher succeeds when evented is installed.

test_make_dispatcher_constructs_with_empty_accounts() -> None
  # make_dispatcher() returns a Dispatcher with an empty account registry.

```

## test_fanout.py
```
# SourceHub: merge sources into the dispatcher + supervised restart on failure.


cls _ListSource(BaseEventSource)
  __init__(name: str, order_ids: list[str) -> None
  async stream() -> AsyncIterator[OrderCreated]

cls _FlakySource(BaseEventSource)
  # Fails once (after emitting one event), then succeeds on restart.
  __init__(name: str) -> None
  async stream() -> AsyncIterator[OrderCreated]

_order(order_id: str) -> OrderCreated

async test_hub_merges_sources_into_dispatcher() -> None

async test_failed_source_is_restarted() -> None

```

## test_fast_return.py
```
# Unit tests for :class:`WebhookFastReturnMiddleware`.


async test_schedule_returns_immediately()
  # ``schedule(coro)`` must return without awaiting the coroutine.

async test_schedule_keeps_strong_ref()
  # Tasks must not be GC'd mid-flight even if caller drops the ref.

async test_fallback_tracker_shutdown_waits()

async test_external_tracker_used_when_supplied()

```

## test_fsm_round_trip.py
```
# FSM round-trip — :class:`MemoryFSMStorage` + :class:`FSMContext` + key builder.


cls _ChatStates(StatesGroup)

test_storage_key_render_format() -> None

test_storage_key_builder_stringifies_int_account_id() -> None

test_storage_key_disambiguates_account_chat_pairs() -> None

async test_fsm_context_state_round_trip() -> None

async test_fsm_context_data_round_trip() -> None

async test_fsm_context_isolation_between_keys() -> None

test_state_auto_prefixes_with_group_name() -> None

async test_state_filter_matches_current_state() -> None

async test_state_filter_matches_cleared_context() -> None

async test_state_filter_membership(states: tuple, current: State, expected: bool) -> None

```

## test_hmac_signature.py
```
# Unit tests for :class:`HMACSignatureMiddleware`.


_sign(body: bytes, secret: str) -> str

async test_correct_signature_accepts()

async test_wrong_signature_rejects()

async test_unknown_webhook_id_rejects()

async test_missing_signature_required_raises()

async test_missing_signature_optional_returns_false()

async test_constant_time_compare_used()

```

## test_job.py
```
# Job domain — résumé search, detail, contacts (PII).


async test_search_resumes_emits_post_with_body_fields(client: Client, fake_session: FakeSession) -> None

async test_search_resumes_from_query_dto_round_trips_fields() -> None

async test_get_resume_returns_typed_resume(client: Client, fake_session: FakeSession) -> None

async test_get_resume_contacts_emits_post_with_idempotency_key(client: Client, fake_session: FakeSession) -> None

async test_resume_bound_get_contacts_builds_method_class(client: Client, fake_session: FakeSession) -> None

```

## test_message_variants.py
```
# Discriminated-union decoding for all 11 Message variants + Unknown fallback.

FIXTURES = …

_load(name: str) -> dict

_reset_warning_cache() -> None

test_text_message_decodes_into_text_variant() -> None

test_image_message_decodes_into_image_variant() -> None

test_link_message_decodes_into_link_variant() -> None

test_item_message_decodes_into_item_variant() -> None

test_location_message_decodes_with_lat_lng() -> None

test_voice_message_carries_voice_id() -> None

test_call_message_decodes_status() -> None

test_file_message_decodes_size_and_url() -> None

test_system_message_decodes_kind() -> None

test_app_call_message_decodes_into_app_call_variant() -> None

test_deleted_message_decodes_into_deleted_variant() -> None

test_unknown_message_decodes_into_unknown_fallback_with_raw_type() -> None

test_unknown_message_emits_exactly_one_warning_per_type(caplog: pytest.LogCaptureFixture) -> None

test_unknown_warning_is_deduplicated_across_calls(caplog: pytest.LogCaptureFixture) -> None

```

## test_messenger.py
```
# Unit tests for the messenger method-classes.

FIXTURES = …

_load(name: str) -> dict[str, Any]

msgr_config() -> ClientConfig

async msgr_client(msgr_config: ClientConfig) -> Any

async test_list_chats_decodes_chat_list_and_renders_path(msgr_client: tuple[Client, FakeSession) -> None

async test_get_chat_renders_path_and_decodes_chat(msgr_client: tuple[Client, FakeSession) -> None

async test_list_messages_renders_v3_path_and_decodes(msgr_client: tuple[Client, FakeSession) -> None

async test_send_text_message_posts_body_and_idempotency_header(msgr_client: tuple[Client, FakeSession) -> None

async test_send_image_posts_image_id_in_body(msgr_client: tuple[Client, FakeSession) -> None

async test_mark_chat_read_posts_to_read_endpoint(msgr_client: tuple[Client, FakeSession) -> None

async test_delete_message_renders_three_path_fields(msgr_client: tuple[Client, FakeSession) -> None

async test_upload_image_collapses_random_key_response(msgr_client: tuple[Client, FakeSession) -> None

async test_list_blacklist_decodes_blacklist_envelope(msgr_client: tuple[Client, FakeSession) -> None

async test_add_blacklist_posts_user_ids(msgr_client: tuple[Client, FakeSession) -> None

async test_remove_blacklist_uses_delete_verb_with_target(msgr_client: tuple[Client, FakeSession) -> None

async test_get_voice_files_renders_query_and_decodes(msgr_client: tuple[Client, FakeSession) -> None

async test_chat_send_text_builds_bound_send_text_message(msgr_client: tuple[Client, FakeSession) -> None

async test_message_reply_uses_send_text_regardless_of_source(msgr_client: tuple[Client, FakeSession) -> None
  # Reply is always a SendTextMessage even when source variant is image / voice.

async test_subscribe_webhook_posts_url_and_secret(msgr_client: tuple[Client, FakeSession) -> None

async test_unsubscribe_webhook_posts_url(msgr_client: tuple[Client, FakeSession) -> None

async test_list_subscriptions_decodes_envelope(msgr_client: tuple[Client, FakeSession) -> None

```

## test_methods_base.py
```
# Unit tests for ``avitoapi.methods._base.BaseMethod``.


cls _Stub(BaseModel)

test_subclass_with_path_attribute_raises_method_declaration_error() -> None

test_subclass_with_generic_only_auto_binds_returning() -> None

test_subclass_with_matching_generic_and_returning_keeps_returning() -> None

test_subclass_with_contradictory_generic_and_returning_raises() -> None

async test_bare_method_await_raises_method_not_bound_error() -> None

async test_as_attaches_client_and_returns_self() -> None

async test_as_with_different_client_overrides_previous() -> None

async test_emit_routes_through_session_make_request(client: Any, accounts_self_payload: dict[str, Any) -> None
  # as_(client) + emit(client) must produce the same result as ``await client(method)``.

async test_await_after_bind_works(client: Any, accounts_self_payload: dict[str, Any) -> None

```

## test_models_base.py
```
# Unit tests for ``avitoapi.models._base.AvitoObject``.


cls _Child(AvitoObject)

cls _Parent(AvitoObject)

cls _ListParent(AvitoObject)

cls _DictParent(AvitoObject)

cls _Grandchild(AvitoObject)

cls _Middle(AvitoObject)

cls _Root(AvitoObject)

test_require_client_raises_when_client_is_none() -> None

test_require_client_returns_client_when_bound() -> None

test_as_returns_self_for_fluent_chaining() -> None

test_as_sets_client_attribute() -> None

test_as_recursively_binds_nested_bound_model_child() -> None

test_as_with_none_child_does_not_raise() -> None

test_as_recursively_binds_list_of_bound_models() -> None

test_as_with_empty_list_does_not_raise() -> None

test_as_recursively_binds_dict_value_bound_models() -> None

test_as_with_empty_dict_does_not_raise() -> None

test_as_propagates_through_multiple_levels_of_nesting() -> None

```

## test_oauth.py
```
# Unit tests for ``avitoapi.auth.oauth``.


async test_issue_client_credentials_returns_token_when_endpoint_responds_200(oauth_client: OAuthClient, fake_session: FakeSession, oauth_token_payload: dict[str, Any) -> None

async test_issue_client_credentials_caches_token_when_called(oauth_client: OAuthClient, token_cache: TokenCache, fake_session: FakeSession, oauth_token_payload: dict[str, Any, client_config: ClientConfig) -> None

async test_refresh_if_needed_returns_same_token_when_far_from_expiry(oauth_client: OAuthClient, sample_token: Token, fake_session: FakeSession) -> None

async test_refresh_if_needed_issues_new_token_when_close_to_expiry(oauth_client: OAuthClient, fake_session: FakeSession, oauth_token_payload: dict[str, Any) -> None

async test_refresh_if_needed_issues_new_token_when_already_expired(oauth_client: OAuthClient, fake_session: FakeSession, oauth_token_payload: dict[str, Any) -> None

async test_token_cache_put_then_get_round_trips(token_cache: TokenCache, sample_token: Token) -> None

async test_token_cache_get_returns_none_when_key_absent(token_cache: TokenCache) -> None

async test_token_cache_invalidate_removes_key(token_cache: TokenCache, sample_token: Token) -> None

test_is_token_expired_403_accepts_body_with_token_expired_message() -> None

test_is_token_expired_403_accepts_top_level_token_expired_key() -> None

test_is_token_expired_403_accepts_str_body() -> None

test_is_token_expired_403_rejects_unrelated_forbidden_body() -> None

test_is_token_expired_403_rejects_empty_body() -> None

test_is_token_expired_403_rejects_non_json_body() -> None

async test_oauth_injector_reauths_when_first_call_returns_token_expired_403(oauth_client: OAuthClient, oauth_injector: Any, fake_session: FakeSession, client_config: ClientConfig, oauth_token_payload: dict[str, Any, oauth_token_expired_payload: dict[str, Any) -> None

```

## test_order_management.py
```
# Order-management domain — representative round-trips + bound actions + binary download.


async test_list_managed_orders_returns_root_envelope(client: Client, fake_session: FakeSession) -> None

async test_apply_order_transition_idempotency_key_injected(client: Client, fake_session: FakeSession) -> None

async test_apply_transition_serializes_each_verb(client: Client, fake_session: FakeSession) -> None

async test_accept_return_order_round_trip(client: Client, fake_session: FakeSession) -> None

async test_set_order_markings_routes_post_with_body(client: Client, fake_session: FakeSession) -> None

async test_get_courier_delivery_range_routes_get(client: Client, fake_session: FakeSession) -> None

async test_check_order_confirmation_code_returns_check(client: Client, fake_session: FakeSession) -> None

async test_create_order_labels_returns_task(client: Client, fake_session: FakeSession) -> None

async test_download_order_labels_returns_raw_bytes(client: Client, fake_session: FakeSession) -> None

test_download_order_labels_declares_binary_response() -> None

async test_managed_order_bound_apply_transition_builds_method(client: Client, fake_session: FakeSession) -> None

async test_managed_order_bound_accept_return(client: Client, fake_session: FakeSession) -> None

test_managed_order_bound_method_without_client_raises() -> None

```

## test_order_state_machine.py
```
# Order state-machine — exhaustive transition table coverage.


test_transitions_table_covers_every_status() -> None

test_terminal_states_have_no_outgoing_transitions() -> None

test_declared_transitions_match_spec() -> None
  # Mirror the spec exactly so any silent edit to the table fails this test.

test_every_pair_matches_table(src: OrderStatus, dst: OrderStatus) -> None

test_full_happy_path_new_to_completed() -> None

test_refund_branch_from_completed() -> None

test_cancel_branches_from_each_pre_delivery_state() -> None

test_cannot_skip_states() -> None

test_cannot_resurrect_from_terminal() -> None

test_cannot_cancel_after_delivery() -> None

test_non_strict_logs_warning_instead_of_raising(caplog: pytest.LogCaptureFixture) -> None

```

## test_orders.py
```
# Orders domain — method-class fixture round-trips + bound action wiring.


async test_get_order_returns_typed_order(client: Client, fake_session: FakeSession) -> None

async test_list_orders_returns_envelope_with_two_rows(client: Client, fake_session: FakeSession) -> None

async test_change_order_status_round_trip(client: Client, fake_session: FakeSession) -> None

async test_change_order_status_emits_post_with_idempotency_key(client: Client, fake_session: FakeSession) -> None

async test_transfer_delivery_terms_carries_body_fields(client: Client, fake_session: FakeSession) -> None

async test_transfer_track_number_routes_correctly(client: Client, fake_session: FakeSession) -> None

async test_refund_order_round_trip(client: Client, fake_session: FakeSession) -> None

async test_order_bound_change_status_builds_method_with_client(client: Client, fake_session: FakeSession) -> None

async test_order_bound_refund_builds_method(client: Client, fake_session: FakeSession) -> None

async test_order_bound_method_without_client_raises(accounts_self_payload: dict[str, Any) -> None

```

## test_persistent_queue.py
```
# Unit tests for :class:`EventQueue` and the dispatcher ack/replay loop.


cls _Pinged(BaseEvent)
  __init__() -> None

async test_enqueue_persists_under_storage()

async test_ack_atomically_removes()

async test_replay_yields_unacked_events_in_order()

async test_dispatcher_calls_atomic_completed_to_drop_event()

async test_unacked_event_replayed_after_restart()

async test_ctx_queue_persist_metadata_round_trips()

```

## test_polling.py
```
# Contract tests for the pull-based :class:`~avitoapi.polling.PollingRunner` feed.


cls _RecordingDispatcher
  # Captures every event fed to it — stands in for the real Dispatcher.
  __init__() -> None
  async feed_event(event: Event) -> bool

cls _FakePoller(PollingRunner)
  __init__(dispatcher: object, storage: MemoryStorage, batches: list[PollBatch) -> None
  async poll(cursor: str?) -> PollBatch

async test_tick_emits_batch_and_persists_cursor() -> None

async test_tick_resumes_from_persisted_cursor() -> None

async test_start_runs_until_stop() -> None

async test_start_emits_pollerror_and_survives_a_failed_poll() -> None

test_update_cadence_rejects_non_positive() -> None

test_construction_rejects_non_positive_intervals() -> None

```

## test_postgres_storage.py
```
# Unit tests for :class:`PostgresStorage`.


cls _StubConn
  __init__(sink: list[tuple[str, tuple[Any, ..., rows: dict[str, Any) -> None
  async execute(sql: str, *args: Any) -> None
  async fetchrow(sql: str, *args: Any) -> dict[str, Any] | None
  async fetchval(sql: str, *args: Any) -> Any

cls _PoolAcquireCtx
  __init__(conn: _StubConn) -> None

cls _StubPool
  __init__() -> None
  acquire() -> _PoolAcquireCtx
  async close() -> None

pool() -> _StubPool

storage(pool: _StubPool) -> PostgresStorage

async test_lazy_schema_bootstrap_runs_create_table_once(storage, pool)

async test_put_writes_upsert(storage, pool)

async test_put_with_ttl_sets_expires_at(storage, pool)

async test_get_returns_none_for_missing_key(storage)

async test_get_returns_decoded_value(storage, pool)

async test_get_drops_expired_row(storage, pool)

async test_namespace_prefixes_key(pool)

async test_namespaced_returns_compound_namespace(storage)

async test_health_runs_select_one(storage)

test_invalid_table_name_rejected(pool)

test_requires_pool_or_dsn()

```

## test_promotion.py
```
# Promotion v1 — list / drop / bids / BBIP order / forecast round-trips.


async test_list_active_promotions_decodes_list(client: Client, fake_session: FakeSession) -> None

async test_drop_promotion_sends_body_with_item_ids(client: Client, fake_session: FakeSession) -> None

async test_list_bids_decodes(client: Client, fake_session: FakeSession) -> None

async test_create_bbip_order_idempotent(client: Client, fake_session: FakeSession) -> None

async test_bbip_forecast_decodes(client: Client, fake_session: FakeSession) -> None

```

## test_protocol_rest.py
```
# Unit tests for ``avitoapi.protocol.rest.RestProtocol``.


cls _EchoResponse(BaseModel)

cls _PostThing(BaseMethod[_EchoResponse])
  # POST /core/v1/things — body fields go in JSON body.

cls _GetThing(BaseMethod[_EchoResponse])
  # GET /core/v1/things/{thing_id} — path field + query field.

cls _UnsafePost(BaseMethod[_EchoResponse])
  # POST without idempotent_mutation — should NOT get an Idempotency-Key.

cls _StubClient
  # Tiny stub with the attributes RestProtocol expects on ``ctx.client``.
  __init__() -> None

_ctx(client_config: ClientConfig, storage: MemoryStorage, method: BaseMethod[Any) -> RequestContext

async test_build_request_routes_get_fields_into_query(client_config: ClientConfig, storage: MemoryStorage) -> None

async test_build_request_routes_post_fields_into_body(client_config: ClientConfig, storage: MemoryStorage) -> None

async test_build_request_substitutes_path_placeholders(client_config: ClientConfig, storage: MemoryStorage) -> None

async test_build_request_leaves_path_field_out_of_query(client_config: ClientConfig, storage: MemoryStorage) -> None

test_is_idempotent_true_for_get_methods() -> None

test_is_idempotent_false_for_non_retry_safe_post() -> None

async test_build_request_injects_idempotency_key_when_method_opts_in(client_config: ClientConfig, storage: MemoryStorage) -> None

async test_build_request_omits_idempotency_key_when_not_marked(client_config: ClientConfig, storage: MemoryStorage) -> None

async test_build_request_reuses_idempotency_key_across_calls_with_same_body(client_config: ClientConfig, storage: MemoryStorage) -> None

async test_build_request_uses_different_idempotency_key_for_different_body(client_config: ClientConfig, storage: MemoryStorage) -> None

test_decode_response_validates_into_returning_model(accounts_self_payload: dict[str, Any) -> None

```

## test_proxy_callback.py
```
# Unit tests for :class:`CallbackProxyTransport`.


async test_callback_called_on_acquire()

async test_keep_keeps_current_proxy()

async test_callback_invoked_on_error_with_metadata()

async test_initial_proxy_seeds_context()

async test_set_current_overrides_callback_state()

async test_async_callback_raises_helpful_error()

```

## test_proxy_middleware.py
```
# Unit tests for ``ProxyErrorMiddleware`` and ``RetryMiddleware``.


_ctx_with_proxy() -> RequestContext

async test_proxy_error_middleware_translates_connection_error()

async test_proxy_error_middleware_translates_timeout()

async test_proxy_error_middleware_passes_through_without_proxy()

async test_retry_middleware_retries_proxy_error_until_max()

async test_retry_middleware_gives_up_on_proxy_exhausted()

async test_retry_middleware_does_not_retry_unknown_errors()

async test_retry_middleware_returns_response_on_success()

test_proxy_banned_carries_failure_count()

```

## test_proxy_parser.py
```
# Unit tests for :func:`parse_proxy` / :func:`parse_proxy_list`.


test_full_url_with_auth()

test_socks5_scheme()

test_host_port_shorthand_defaults_to_http()

test_host_port_user_pass_legacy_format()

test_user_pass_at_host_port()

test_dict_input()

test_invalid_port_rejected()

test_unknown_scheme_rejected()

test_blank_string_rejected()

test_unsupported_type_rejected()

test_parse_list_skips_blank_and_comments()

test_parse_list_skip_invalid_flag()

test_parse_list_propagates_errors_by_default()

test_proxy_instance_returned_as_is()

test_label_override()

```

## test_proxy_rotating.py
```
# Unit tests for :class:`ListProxyTransport` rotation + ban logic.


async test_round_robin_cycles_through_pool()

async test_mark_invalid_increments_failure_count()

async test_ban_threshold_marks_proxy_unhealthy()

async test_ban_raises_when_raise_on_ban_true()

async test_pool_exhausted_when_every_proxy_banned()

async test_cooldown_reactivates_banned_proxy()

async test_random_strategy_uses_rng()

async test_sticky_per_account()

async test_invalid_hook_fires_on_failure()

_only_key(transport: ListProxyTransport) -> str

_last_context(transport: ListProxyTransport)

```

## test_queue_v2.py
```
# Unit tests for queue-v2: lease, DLQ, scheduled enqueue, JSONSerializer, worker, partition.


cls _Ping(BaseEvent)
  __init__() -> None

_reset_registry()

async test_json_serializer_roundtrips_event()

async test_event_registry_explicit_register_with_alias()

async test_event_registry_rejects_conflicting_registration()

async test_lease_marks_message_in_flight()

async test_lease_expires_after_visibility_timeout()

async test_release_returns_lease_without_ack()

async test_ack_rejects_foreign_lease_id()

async test_max_attempts_moves_to_dlq()

async test_run_at_defers_lease_until_due()

async test_enqueue_later_helper_uses_delay()

async test_stats_buckets_pending_scheduled_in_flight()

async test_worker_acks_on_handler_success()

async test_worker_releases_on_handler_failure()

async test_worker_serialises_same_partition_key()

async test_worker_parallelises_distinct_partitions()

```

## test_rate_limit.py
```
# Unit tests for :class:`AvitoRateLimitMiddleware`.


async test_token_bucket_acquire_blocks_after_burst()

async _noop_handler(prepared: PreparedRequest, ctx: RequestContext) -> RawResponse

async test_global_rps_limits_throughput()

async test_distinct_accounts_independent()

async test_per_chat_bucket_fires_when_chat_id_set()

```

## test_realty.py
```
# Realty / short-term-rent — bookings, calendar, period prices.


async test_list_bookings_returns_envelope_with_one_row(client: Client, fake_session: FakeSession) -> None

async test_get_calendar_coerces_date_keys(client: Client, fake_session: FakeSession) -> None

async test_get_period_prices_returns_typed_envelope(client: Client, fake_session: FakeSession) -> None

async test_update_period_prices_emits_put_with_idempotency_key(client: Client, fake_session: FakeSession) -> None

async test_item_bookings_uses_path_template(client: Client, fake_session: FakeSession) -> None

```

## test_realty_reports.py
```
# Unit tests for the realty-reports domain.

FIXTURES = …

_load(name: str) -> dict[str, Any]

rr_config() -> ClientConfig

async rr_client(rr_config: ClientConfig) -> Any

async test_market_price_correspondence_renders_two_path_fields(rr_client: tuple[Client, FakeSession) -> None

async test_create_realty_report_returns_task_and_is_idempotent(rr_client: tuple[Client, FakeSession) -> None

```

## test_reviews.py
```
# Reviews domain — list / info / reply / delete-reply round trips.


async test_list_reviews_decodes_envelope(client: Client, fake_session: FakeSession) -> None

async test_get_review_info_decodes_aggregates(client: Client, fake_session: FakeSession) -> None

async test_reply_to_review_round_trip(client: Client, fake_session: FakeSession) -> None

async test_review_bound_reply_to_uses_review_id(client: Client, fake_session: FakeSession) -> None

async test_review_reply_bound_delete_method() -> None
  # A manually-constructed reply has no client; deletion raises.

async test_delete_review_reply_emits_delete(client: Client, fake_session: FakeSession) -> None

```

## test_router_propagation.py
```
# Propagation semantics: single-fire sub-routers, stop-propagation, status fallback.


_order() -> OrderCreated

async _propagate(router: Router, event: Event) -> tuple[bool, EventContext]

async test_subrouter_handler_fires_exactly_once() -> None
  # A handler on an included child must fire once, not once per merge + walk.

async test_handler_registered_after_include_still_fires_once() -> None
  # Registration order must not change fire count (old snapshot-merge bug).

async test_stop_propagation_halts_remaining_handlers() -> None

async test_cancel_propagation_stops_without_error() -> None

async test_skip_handler_yields_to_next() -> None

test_unknown_order_status_maps_to_unknown() -> None
  # Unknown upstream status must not be silently coerced to NEW.

```

## test_special_offers.py
```
# Unit tests for the special-offers (SBC gateway) domain.

FIXTURES = …

_load(name: str) -> dict[str, Any] | list[Any]

so_config() -> ClientConfig

async so_client(so_config: ClientConfig) -> Any

async test_get_available_offers_posts_item_ids(so_client: tuple[Client, FakeSession) -> None

async test_multi_create_offers_is_idempotent(so_client: tuple[Client, FakeSession) -> None

async test_multi_confirm_offers_returns_per_row_outcome(so_client: tuple[Client, FakeSession) -> None

async test_get_offers_stats_decodes_envelope(so_client: tuple[Client, FakeSession) -> None

async test_get_offer_tariff_info_decodes(so_client: tuple[Client, FakeSession) -> None

```

## test_stock_management.py
```
# Unit tests for the stock-management domain.

FIXTURES = …

_load(name: str) -> dict[str, Any] | list[Any]

sm_config() -> ClientConfig

async sm_client(sm_config: ClientConfig) -> Any

async test_get_stock_info_posts_item_ids(sm_client: tuple[Client, FakeSession) -> None

async test_update_stocks_is_put_and_idempotent(sm_client: tuple[Client, FakeSession) -> None

```

## test_tariff.py
```
# Unit tests for the tariff domain.

FIXTURES = …

_load(name: str) -> dict[str, Any]

tr_config() -> ClientConfig

async tr_client(tr_config: ClientConfig) -> Any

async test_get_tariff_info_decodes_envelope(tr_client: tuple[Client, FakeSession) -> None

```

## test_trxpromo.py
```
# TrxPromo v1 — apply / cancel / commissions round-trips.


async test_apply_trx_promo_idempotent(client: Client, fake_session: FakeSession) -> None

async test_cancel_trx_promo_idempotent(client: Client, fake_session: FakeSession) -> None

async test_get_trx_commissions_decodes_rules(client: Client, fake_session: FakeSession) -> None

```

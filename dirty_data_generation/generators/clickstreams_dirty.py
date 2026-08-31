# dirty_data_generation/generators/clickstreams_dirty.py
import pandas as pd

from dirty_data_generation.context.generation_context import GenerationContext
from dirty_data_generation.corruption_rules.clickstream_session_rules import (
    add_to_cart_does_not_increase_cart,
    bounce_flag_on_non_first_event,
    bounce_session_multiple_events,
    checkout_start_without_cart,
    duplicate_event_order_within_session,
    future_event_timestamp,
    invalid_event_transition,
    invalid_first_event_for_referrer,
    non_cart_event_changes_cart,
    non_sequential_event_order,
    payment_failed_cart_mismatch,
    payment_successful_cart_mismatch,
    purchased_items_not_in_previous_cart,
    remove_from_cart_does_not_reduce_cart,
    timestamp_out_of_order,
)
from dirty_data_generation.corruption_rules.clickstream_structural_rules import (
    inject_orphan_sessions,
)
from dirty_data_generation.corruption_rules.clickstreams_rules import (
    bundle_does_not_belong_to_promotion,
    bundle_on_non_product_event,
    campaign_ids_without_indicator,
    cart_size_does_not_match_cart_content,
    category_event_missing_category,
    category_promotion_target_mismatch,
    control_campaign_without_campaign,
    customer_segment_mismatch,
    device_category_mismatch,
    duplicate_bundle_within_clickstream,
    duplicate_campaign_within_clickstream,
    duplicate_promotion_within_clickstream,
    invalid_bounce_flag,
    invalid_cart_size_range,
    invalid_clickstream_id_format,
    invalid_customer_segment,
    invalid_device_category,
    invalid_event_order_range,
    invalid_event_page,
    invalid_event_type,
    invalid_referrer,
    invalid_scroll_depth_range,
    invalid_session_id_format,
    invalid_stock_status,
    missing_bounce_flag,
    missing_cart_content,
    missing_cart_size,
    missing_customer_segment,
    missing_device_category,
    missing_event_order,
    missing_event_timestamp,
    missing_event_type,
    missing_location,
    missing_page,
    missing_purchased_items,
    missing_purchased_items_on_payment_successful,
    missing_referrer,
    missing_scroll_depth,
    non_category_event_has_category,
    non_product_event_has_product_id,
    non_product_event_has_product_name,
    non_product_view_has_stock_status,
    non_scroll_event_has_scroll_depth,
    product_event_missing_product_id,
    product_event_missing_product_name,
    product_information_mismatch,
    product_promotion_target_mismatch,
    product_view_missing_stock_status,
    promotion_ids_without_bundle_for_bundle_reference,
    promotion_on_non_product_event,
    purchased_items_on_payment_failed,
    scroll_event_missing_scroll_depth,
    treatment_and_control_campaign_both_true,
    treatment_campaign_without_campaign,
)
from dirty_data_generation.helpers.dirty_utils import apply_corruption
from dirty_data_generation.registry import register
from dirty_data_generation.utils.io_utils import save

# =============================================================================
# Row-Level Corruption Rules
# =============================================================================

CLICKSTREAM_RULES = [
    # -------------------------------------------------------------------------
    # Missing Values
    # -------------------------------------------------------------------------
    (0.03, missing_customer_segment),
    (0.03, missing_device_category),
    (0.03, missing_referrer),
    (0.03, missing_location),
    (0.03, missing_event_timestamp),
    (0.03, missing_event_order),
    (0.03, missing_event_type),
    (0.03, missing_page),
    (0.03, missing_scroll_depth),
    (0.03, missing_bounce_flag),
    (0.03, missing_cart_content),
    (0.03, missing_cart_size),
    (0.03, missing_purchased_items),
    # -------------------------------------------------------------------------
    # Formatting
    # -------------------------------------------------------------------------
    (0.02, invalid_clickstream_id_format),
    (0.02, invalid_session_id_format),
    # -------------------------------------------------------------------------
    # Accepted Values
    # -------------------------------------------------------------------------
    (0.02, invalid_customer_segment),
    (0.02, invalid_device_category),
    (0.02, invalid_referrer),
    (0.02, invalid_event_type),
    (0.02, invalid_bounce_flag),
    (0.02, invalid_stock_status),
    # -------------------------------------------------------------------------
    # Range Validation
    # -------------------------------------------------------------------------
    (0.02, invalid_event_order_range),
    (0.02, invalid_scroll_depth_range),
    (0.02, invalid_cart_size_range),
    # -------------------------------------------------------------------------
    # Customer / Product Consistency
    # -------------------------------------------------------------------------
    (0.02, customer_segment_mismatch),
    (0.02, device_category_mismatch),
    (0.02, product_information_mismatch),
    # -------------------------------------------------------------------------
    # Campaign Logic
    # -------------------------------------------------------------------------
    (0.02, treatment_campaign_without_campaign),
    (0.02, control_campaign_without_campaign),
    (0.02, campaign_ids_without_indicator),
    (0.02, treatment_and_control_campaign_both_true),
    (0.02, duplicate_campaign_within_clickstream),
    # -------------------------------------------------------------------------
    # Promotion / Bundle Logic
    # -------------------------------------------------------------------------
    (0.02, promotion_ids_without_bundle_for_bundle_reference),
    (0.02, duplicate_promotion_within_clickstream),
    (0.02, duplicate_bundle_within_clickstream),
    (0.02, bundle_does_not_belong_to_promotion),
    (0.02, product_promotion_target_mismatch),
    (0.02, category_promotion_target_mismatch),
    # -------------------------------------------------------------------------
    # Event Content
    # -------------------------------------------------------------------------
    (0.02, product_event_missing_product_id),
    (0.02, non_product_event_has_product_id),
    (0.02, product_event_missing_product_name),
    (0.02, non_product_event_has_product_name),
    (0.02, category_event_missing_category),
    (0.02, non_category_event_has_category),
    (0.02, scroll_event_missing_scroll_depth),
    (0.02, non_scroll_event_has_scroll_depth),
    # -------------------------------------------------------------------------
    # Page / Event Consistency
    # -------------------------------------------------------------------------
    (0.02, invalid_event_page),
    # -------------------------------------------------------------------------
    # Stock
    # -------------------------------------------------------------------------
    (0.02, product_view_missing_stock_status),
    (0.02, non_product_view_has_stock_status),
    # -------------------------------------------------------------------------
    # Promotion / Bundle Scope
    # -------------------------------------------------------------------------
    (0.02, promotion_on_non_product_event),
    (0.02, bundle_on_non_product_event),
    # -------------------------------------------------------------------------
    # Cart Size
    # -------------------------------------------------------------------------
    (0.02, cart_size_does_not_match_cart_content),
    # -------------------------------------------------------------------------
    # Purchased Items
    # -------------------------------------------------------------------------
    (0.02, missing_purchased_items_on_payment_successful),
    (0.02, purchased_items_on_payment_failed),
]


# =============================================================================
# Session-Level Corruption Rules
# =============================================================================

SESSION_RULES = [
    (0.02, duplicate_event_order_within_session),
    (0.02, non_sequential_event_order),
    (0.02, timestamp_out_of_order),
    (0.02, future_event_timestamp),
    (0.02, bounce_flag_on_non_first_event),
    (0.02, bounce_session_multiple_events),
    (0.02, invalid_first_event_for_referrer),
    (0.02, invalid_event_transition),
    (0.02, checkout_start_without_cart),
    (0.02, add_to_cart_does_not_increase_cart),
    (0.02, remove_from_cart_does_not_reduce_cart),
    (0.02, payment_successful_cart_mismatch),
    (0.02, payment_failed_cart_mismatch),
    (0.02, non_cart_event_changes_cart),
    (0.02, purchased_items_not_in_previous_cart),
]


# =============================================================================
# Generator
# =============================================================================


@register("dirty_clickstreams")
def dirty_clickstreams(ctx: GenerationContext):

    df = ctx.clickstreams.clickstreams_df.copy()

    # -------------------------------------------------------------------------
    # Phase 0: Structural corruption
    # -------------------------------------------------------------------------

    orphan_rows = inject_orphan_sessions(
        ctx=ctx,
        source_df=df,
    )

    if orphan_rows:
        orphan_df = pd.DataFrame(orphan_rows)
        df = pd.concat([df, orphan_df], ignore_index=True)

    # -------------------------------------------------------------------------
    # Internal corruption tracking
    # -------------------------------------------------------------------------

    # Used only by corruption rules to limit the number of
    # corruptions that can be applied to a single row.
    # This column is removed before the dirty dataset is saved.
    df["error_count"] = 0

    # -------------------------------------------------------------------------
    # Phase 1: Row-level corruption
    # -------------------------------------------------------------------------

    for rate, rule in CLICKSTREAM_RULES:
        apply_corruption(
            df=df,
            rate=rate,
            corruption=rule,
            ctx=ctx,
        )

    # -------------------------------------------------------------------------
    # Phase 2: Session-level corruption
    # -------------------------------------------------------------------------

    for rate, rule in SESSION_RULES:
        apply_corruption(
            df=df,
            rate=rate,
            corruption=rule,
            ctx=ctx,
        )

    # -------------------------------------------------------------------------
    # Remove internal corruption tracking column
    # -------------------------------------------------------------------------

    df = df.drop(columns=["error_count"])

    return save(
        df,
        "clickstreams_dirty.csv",
    )

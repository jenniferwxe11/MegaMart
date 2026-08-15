from dirty_data_generation.context.generation_context import GenerationContext
from dirty_data_generation.corruption_rules.campaigns_rules import (
    budget_out_of_range,
    campaign_without_marketing_channels,
    completed_campaign_future_end_date,
    duplicate_channel_inside_channels,
    invalid_campaign_id_format,
    invalid_campaign_name,
    invalid_campaign_period,
    invalid_campaign_type,
    invalid_status,
    invalid_target_segment,
    missing_budget,
    missing_campaign_name,
    missing_campaign_type,
    missing_channels,
    missing_end_date,
    missing_is_ab_test,
    missing_start_date,
    missing_status,
    missing_target_segment,
    season_campaign_type_inconsistency,
)
from dirty_data_generation.helpers.dirty_utils import apply_corruption
from dirty_data_generation.registry import register
from dirty_data_generation.utils.io_utils import save

CAMPAIGN_RULES = [
    # Missing Values
    (0.03, missing_campaign_name),
    (0.03, missing_campaign_type),
    (0.03, missing_target_segment),
    (0.03, missing_channels),
    (0.03, missing_start_date),
    (0.03, missing_end_date),
    (0.03, missing_budget),
    (0.03, missing_is_ab_test),
    (0.03, missing_status),
    # Accepted Values
    (0.02, invalid_campaign_type),
    (0.02, invalid_target_segment),
    (0.02, invalid_status),
    # Formatting
    (0.02, invalid_campaign_id_format),
    (0.02, invalid_campaign_name),
    # Range Validation
    (0.02, budget_out_of_range),
    # Business Rule Violations
    (0.03, duplicate_channel_inside_channels),
    (0.03, invalid_campaign_period),
    (0.03, season_campaign_type_inconsistency),
    (0.03, campaign_without_marketing_channels),
    (0.03, completed_campaign_future_end_date),
]


@register("dirty_campaigns")
def dirty_campaigns(ctx: GenerationContext):

    df = ctx.campaigns.campaigns_df.copy()

    for rate, rule in CAMPAIGN_RULES:
        apply_corruption(
            df=df,
            rate=rate,
            corruption=rule,
            ctx=ctx,
        )

    return save(df, "campaigns_dirty.csv")

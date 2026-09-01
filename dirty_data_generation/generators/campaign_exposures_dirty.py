# dirty_data_generation/generators/campaign_exposures_dirty.py

from dirty_data_generation.context.generation_context import GenerationContext
from dirty_data_generation.corruption_rules.campaign_exposures_rules import (
    assignment_group_mismatch,
    channel_not_in_campaign_channels,
    clicked_time_before_exposed_time,
    clicked_time_before_opened_time,
    clicked_without_clicked_time,
    clicked_without_open,
    control_group_exposure_violation,
    cost_per_msg_out_of_range,
    customer_campaign_pair_not_in_assignments,
    device_platform_mismatch,
    duplicate_campaign_exposure,
    eligible_must_be_true,
    exposed_time_without_exposure,
    exposed_without_exposed_time,
    future_clicked_time,
    future_exposed_time,
    future_opened_time,
    invalid_assignment_group,
    invalid_channel,
    invalid_cost_per_msg,
    invalid_device_platform,
    missing_assignment_group,
    missing_channel,
    missing_clicked,
    missing_clicked_time,
    missing_cost_per_msg,
    missing_device_platform,
    missing_eligible,
    missing_exposed,
    missing_exposed_time,
    missing_opened,
    missing_opened_time,
    opened_on_exposure_only_channel,
    opened_time_before_exposed_time,
    opened_without_exposure,
    opened_without_opened_time,
)
from dirty_data_generation.helpers.dirty_utils import apply_corruption
from dirty_data_generation.registry import register
from dirty_data_generation.utils.io_utils import save

CAMPAIGN_EXPOSURE_RULES = [
    # Missing Values
    (0.03, missing_channel),
    (0.03, missing_assignment_group),
    (0.03, missing_eligible),
    (0.03, missing_exposed),
    (0.03, missing_exposed_time),
    (0.03, missing_opened),
    (0.03, missing_opened_time),
    (0.03, missing_clicked),
    (0.03, missing_clicked_time),
    (0.03, missing_device_platform),
    (0.03, missing_cost_per_msg),
    # Accepted Values
    (0.02, invalid_channel),
    (0.02, invalid_assignment_group),
    (0.02, invalid_device_platform),
    # Range Validation
    (0.02, cost_per_msg_out_of_range),
    # Business Rule Violations
    (0.03, duplicate_campaign_exposure),
    (0.03, customer_campaign_pair_not_in_assignments),
    (0.03, channel_not_in_campaign_channels),
    (0.03, device_platform_mismatch),
    (0.03, control_group_exposure_violation),
    (0.03, assignment_group_mismatch),
    (0.03, eligible_must_be_true),
    (0.03, invalid_cost_per_msg),
    (0.03, exposed_without_exposed_time),
    (0.03, exposed_time_without_exposure),
    (0.03, opened_without_exposure),
    (0.03, clicked_without_open),
    (0.03, opened_on_exposure_only_channel),
    (0.03, opened_without_opened_time),
    (0.03, opened_time_before_exposed_time),
    (0.03, clicked_without_clicked_time),
    (0.03, clicked_time_before_opened_time),
    (0.03, clicked_time_before_exposed_time),
    # Date Issues
    (0.02, future_exposed_time),
    (0.02, future_opened_time),
    (0.02, future_clicked_time),
]


@register("dirty_campaign_exposures")
def dirty_campaign_exposures(ctx: GenerationContext):

    df = ctx.campaign_assignments.campaign_exposures_df.copy()

    for rate, rule in CAMPAIGN_EXPOSURE_RULES:
        apply_corruption(
            df=df,
            rate=rate,
            corruption=rule,
            ctx=ctx,
        )

    return save(df, "campaign_exposures_dirty.csv")

import pandas as pd
from pandas.testing import assert_frame_equal

from data_generation.config.campaigns_config import (
    CHANNEL_CONSENT_MAP,
    CONTROL_GROUP_PERCENTAGE,
    DIRECT_MESSAGE_CHANNELS,
    EXPOSURE_ONLY_CHANNELS,
)
from data_generation.config.generation_config import (
    MIN_CONTROL_SIZE,
    MIN_TREATMENT_SIZE,
)
from data_generation.services.campaigns.campaign_assignment_service import (
    apply_channel_filter,
    assign_ab_groups,
)
from data_generation.services.clickstreams.clickstream_lookup_service import (
    get_active_campaigns,
)

# ============================================================
# apply_channel_filter()
# ============================================================
# Integration contract: uses customer data


def test_campaign_assignment_flow_apply_channel_filter_exposure_channels(ctx):
    df = ctx.customers.customers_df
    result = apply_channel_filter(df, channels=EXPOSURE_ONLY_CHANNELS)
    assert result.equals(df)


def test_campaign_assignment_flow_apply_channel_filter_direct_channel(ctx):
    df = ctx.customers.customers_df
    result = apply_channel_filter(df, channels=DIRECT_MESSAGE_CHANNELS)

    consent_columns = [
        CHANNEL_CONSENT_MAP[channel] for channel in DIRECT_MESSAGE_CHANNELS
    ]

    expected = df[df[consent_columns].any(axis=1)]

    result = result.sort_index()
    expected = expected.sort_index()
    assert_frame_equal(result, expected)


# ============================================================
# assign_ab_groups()
# ============================================================
# Integration contract: uses campaign data


def test_campaign_assignment_flow_assign_ab_groups_non_ab_campaign(ctx, seed: int = 42):
    df = ctx.campaigns.campaigns_df
    campaign = df[~df["is_ab_test"]].sample(n=1, random_state=seed).iloc[0]
    audience = ctx.customers.customers_df
    treatment, control = assign_ab_groups(campaign, audience)

    assert control.empty
    assert_frame_equal(
        treatment.sort_index(),
        audience.sort_index(),
    )


def test_campaign_assignment_flow_assign_ab_groups_valid_split(ctx, seed: int = 42):
    df = ctx.campaigns.campaigns_df
    campaign = df[df["is_ab_test"]].sample(n=1, random_state=seed).iloc[0]
    audience = ctx.customers.customers_df
    treatment, control = assign_ab_groups(campaign, audience)

    if len(audience) < MIN_TREATMENT_SIZE + MIN_CONTROL_SIZE:
        assert treatment.empty and control.empty
    else:
        assert len(treatment) + len(control) == len(audience)
        expected_control = int(len(audience) * CONTROL_GROUP_PERCENTAGE)
        assert abs(len(control) - expected_control) <= 5
        # Ensure no overlaps between treatment and control group
        assert set(treatment.index).isdisjoint(set(control.index))


# ============================================================
# get_active_campaigns()
# ============================================================
# Integration contract: uses campaign assignment data


def test_campaign_assignment_flow_get_active_campaigns(ctx):
    camp_assign_df = ctx.campaign_assignments.campaign_assignments_df
    campaign_df = ctx.campaigns.campaigns_df

    # Pick one valid row
    row = camp_assign_df.iloc[0]
    customer_id = row["customer_id"]
    session_start_time = row["eligible_at"]

    # Expected result computed from merged logic
    merged = camp_assign_df[camp_assign_df["customer_id"] == customer_id].merge(
        campaign_df, on="campaign_id", how="left"
    )
    expected = merged[
        (merged["start_date"] <= session_start_time)
        & (merged["end_date"] >= session_start_time)
    ].drop_duplicates(subset=["customer_id", "campaign_id"])

    result = get_active_campaigns(ctx, customer_id, session_start_time)

    if expected.empty:
        assert result is None
    else:
        assert result is not None
        pd.testing.assert_frame_equal(
            result.sort_values(["customer_id", "campaign_id"]).reset_index(drop=True),
            expected.sort_values(["customer_id", "campaign_id"]).reset_index(drop=True),
        )

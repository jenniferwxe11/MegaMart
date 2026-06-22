import random
from unittest.mock import patch

from pandas.testing import assert_frame_equal

from data_generation.config.campaigns_config import (
    BUDGET_MULTIPLIER_BY_CAMPAIGN,
    BUDGET_RANGES_BY_CHANNEL,
    CHANNEL_CONSENT_MAP,
    CHANNEL_PROB_BY_CAMPAIGN,
    CHANNELS,
    CONTROL_GROUP_PERCENTAGE,
    DIRECT_MESSAGE_CHANNELS,
    EXPOSURE_ONLY_CHANNELS,
    MAX_CHANNELS_PER_CAMPAIGN_TYPE,
)
from data_generation.config.generation_config import (
    MIN_CONTROL_SIZE,
    MIN_TREATMENT_SIZE,
)
from data_generation.config.promotions_config import CAMPAIGN_PROMOTION_STRATEGY
from data_generation.services.campaigns.campaign_assignment_service import (
    apply_channel_filter,
    assign_ab_groups,
)
from data_generation.services.campaigns.campaign_exposure_service import (
    simulate_exposure,
)
from data_generation.services.campaigns.campaign_service import (
    calculate_budget,
    pick_channels,
)
from tests.unit_tests.helpers import (
    _build_campaign,
    _build_customer,
)

# ============================================================
# apply_channel_filter()
# ============================================================


def test_camapaign_apply_channel_filter_exposure_channels(customer_ctx):
    df = customer_ctx.customers.customers_df
    result = apply_channel_filter(df, channels=EXPOSURE_ONLY_CHANNELS)
    assert result.equals(df)


def test_campaign_apply_channel_filter_direct_channel(customer_ctx):
    df = customer_ctx.customers.customers_df
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


def test_campaign_assign_ab_groups_non_ab_campaign(campaign_ctx, seed: int = 42):
    df = campaign_ctx.campaigns.campaigns_df
    campaign = df[~df["is_ab_test"]].sample(n=1, random_state=seed).iloc[0]
    audience = df
    treatment, control = assign_ab_groups(campaign, audience)

    assert control.empty
    assert_frame_equal(
        treatment.sort_index(),
        audience.sort_index(),
    )


def test_campaign_assign_ab_groups_ab_campaign_insufficent_audience(
    campaign_ctx, seed: int = 42
):
    df = campaign_ctx.campaigns.campaigns_df
    campaign = df[df["is_ab_test"]].sample(n=1, random_state=seed).iloc[0]
    audience = df.head(MIN_TREATMENT_SIZE + MIN_CONTROL_SIZE - 1)
    treatment, control = assign_ab_groups(campaign, audience)
    assert treatment.empty and control.empty


def test_campaign_assign_ab_groups_valid_split(campaign_ctx, seed: int = 42):
    df = campaign_ctx.campaigns.campaigns_df
    campaign = df[df["is_ab_test"]].sample(n=1, random_state=seed).iloc[0]
    audience = df
    treatment, control = assign_ab_groups(campaign, audience)
    assert len(treatment) + len(control) == len(audience)
    expected_control = int(len(audience) * CONTROL_GROUP_PERCENTAGE)
    assert abs(len(control) - expected_control) <= 5
    # Ensure no overlaps between treatment and control group
    assert set(treatment.index).isdisjoint(set(control.index))


# ============================================================
# pick_channels()
# ============================================================


def test_campaign_pick_channels(seed: int = 42):
    rng = random.Random(seed)
    campaign_type = rng.choice(list(CAMPAIGN_PROMOTION_STRATEGY.keys()))
    channels = pick_channels(campaign_type)
    valid = set(CHANNEL_PROB_BY_CAMPAIGN[campaign_type].keys())

    assert len(channels) <= MAX_CHANNELS_PER_CAMPAIGN_TYPE[campaign_type]
    assert all(c in valid for c in channels)


# ============================================================
# calculate_budget()
# ============================================================


def test_campaign_calculate_budget(seed: int = 42):
    rng = random.Random(seed)
    campaign_type = rng.choice(list(CAMPAIGN_PROMOTION_STRATEGY.keys()))
    channels = rng.sample(CHANNELS, k=rng.randint(1, 2))

    with patch("random.randint") as mock_rand:
        mock_rand.return_value = 100

        calculate_budget(channels, campaign_type)

        for channel in channels:
            base_min, base_max = BUDGET_RANGES_BY_CHANNEL[channel]
            multiplier = BUDGET_MULTIPLIER_BY_CAMPAIGN[campaign_type]

            expected_min = int(base_min * multiplier)
            expected_max = int(base_max * multiplier)

            mock_rand.assert_any_call(expected_min, expected_max)


# ============================================================
# simulate_exposure()
# ============================================================


def test_campaign_simulate_exposure_control_group(
    customer_ctx, campaign_ctx, seed: int = 42
):
    rng = random.Random(seed)
    customer = _build_customer(customer_ctx)
    campaign = _build_campaign(campaign_ctx)
    channel = rng.choice(CHANNELS)

    result = simulate_exposure(
        customer,
        campaign,
        channel,
        "Control",
    )

    assert result["exposed"] is False
    assert result["opened"] is False
    assert result["clicked"] is False
    assert result["cost_per_msg"] == 0.0


def test_campaign_simulate_exposure_treatment_direct_msg_channel(
    customer_ctx, campaign_ctx, seed: int = 42
):
    rng = random.Random(seed)
    customer = _build_customer(customer_ctx)
    campaign = _build_campaign(campaign_ctx)
    channel = rng.choice(DIRECT_MESSAGE_CHANNELS)

    with patch("random.random") as mock_rand, patch(
        "random.randint", return_value=100
    ), patch("numpy.random.beta", return_value=0.5):

        # deliver -> open -> click
        mock_rand.side_effect = [0.0, 0.0, 0.0]

        result = simulate_exposure(
            customer,
            campaign,
            channel,
            "Treatment",
        )

    assert result["exposed"] is True
    assert result["opened"] is True
    assert result["clicked"] is True
    assert result["cost_per_msg"] > 0
    assert result["exposed_time"] is not None
    assert result["opened_time"] is not None
    assert result["clicked_time"] is not None


def test_campaign_simulate_exposure_treatment_exposure_only_channel(
    customer_ctx, campaign_ctx, seed: int = 42
):
    rng = random.Random(seed)
    customer = _build_customer(customer_ctx)
    campaign = _build_campaign(campaign_ctx)
    channel = rng.choice(EXPOSURE_ONLY_CHANNELS)

    with patch("random.random") as mock_rand, patch(
        "random.randint", return_value=50
    ), patch("numpy.random.beta", return_value=0.3):

        # deliver -> click
        mock_rand.side_effect = [0.0, 0.0]

        result = simulate_exposure(
            customer,
            campaign,
            channel,
            "Treatment",
        )

    assert result["exposed"] is True
    assert result["opened"] is False
    assert result["clicked"] is True


def test_campaign_simulate_exposure_treatment_not_exposed(
    customer_ctx, campaign_ctx, seed: int = 42
):
    rng = random.Random(seed)
    customer = _build_customer(customer_ctx)
    campaign = _build_campaign(campaign_ctx)
    channel = rng.choice(CHANNELS)

    with patch("random.random", return_value=0.99):
        result = simulate_exposure(
            customer,
            campaign,
            channel,
            "Treatment",
        )

    assert result["exposed"] is False
    assert result["opened"] is False
    assert result["clicked"] is False
    assert result["cost_per_msg"] == 0.0

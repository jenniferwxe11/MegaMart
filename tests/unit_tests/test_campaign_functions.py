import random
from unittest.mock import patch

from data_generation.config.campaigns_config import (
    BUDGET_MULTIPLIER_BY_CAMPAIGN,
    BUDGET_RANGES_BY_CHANNEL,
    CHANNEL_PROB_BY_CAMPAIGN,
    CHANNELS,
    DIRECT_MESSAGE_CHANNELS,
    EXPOSURE_ONLY_CHANNELS,
    MAX_CHANNELS_PER_CAMPAIGN_TYPE,
)
from data_generation.config.customers_config import DEVICE_CATEGORY, DEVICE_PLATFORM
from data_generation.config.promotions_config import CAMPAIGN_PROMOTION_STRATEGY
from data_generation.services.campaigns.campaign_exposure_service import (
    simulate_exposure,
)
from data_generation.services.campaigns.campaign_service import (
    calculate_budget,
    pick_channels,
)
from tests.helpers import (
    _build_datetime_range,
)

# ============================================================
# pick_channels()
# ============================================================


def test_campaign_functions_pick_channels(seed: int = 42):
    rng = random.Random(seed)
    campaign_type = rng.choice(list(CAMPAIGN_PROMOTION_STRATEGY.keys()))
    channels = pick_channels(campaign_type)
    valid = set(CHANNEL_PROB_BY_CAMPAIGN[campaign_type].keys())

    assert len(channels) <= MAX_CHANNELS_PER_CAMPAIGN_TYPE[campaign_type]
    assert all(c in valid for c in channels)


# ============================================================
# calculate_budget()
# ============================================================


def test_campaign_functions_calculate_budget(seed: int = 42):
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


def test_campaign_functions_simulate_exposure_control_group(seed: int = 42):
    rng = random.Random(seed)

    device_category = rng.choice(list(DEVICE_CATEGORY.keys()))
    device_platform = rng.choice(list(DEVICE_PLATFORM[device_category]))
    customer = {"device_platform": device_platform}

    start_date, end_date = _build_datetime_range()
    campaign = {
        "start_date": start_date,
        "end_date": end_date,
    }

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


def test_campaign_functions_simulate_exposure_treatment_direct_msg_channel(
    seed: int = 42,
):
    rng = random.Random(seed)

    device_category = rng.choice(list(DEVICE_CATEGORY.keys()))
    device_platform = rng.choice(list(DEVICE_PLATFORM[device_category]))
    customer = {"device_platform": device_platform}

    start_date, end_date = _build_datetime_range()
    campaign = {
        "start_date": start_date,
        "end_date": end_date,
    }

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


def test_campaign_functions_simulate_exposure_treatment_exposure_only_channel(
    seed: int = 42,
):
    rng = random.Random(seed)

    device_category = rng.choice(list(DEVICE_CATEGORY.keys()))
    device_platform = rng.choice(list(DEVICE_PLATFORM[device_category]))
    customer = {"device_platform": device_platform}

    start_date, end_date = _build_datetime_range()
    campaign = {
        "start_date": start_date,
        "end_date": end_date,
    }

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


def test_campaign_functions_simulate_exposure_treatment_not_exposed(seed: int = 42):
    rng = random.Random(seed)

    device_category = rng.choice(list(DEVICE_CATEGORY.keys()))
    device_platform = rng.choice(list(DEVICE_PLATFORM[device_category]))
    customer = {"device_platform": device_platform}

    start_date, end_date = _build_datetime_range()
    campaign = {
        "start_date": start_date,
        "end_date": end_date,
    }

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

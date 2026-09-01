# dirty_data_generation/corruption_rules/campaign_exposures_rules.py

import random
from datetime import timedelta

import pandas as pd

from data_generation.config.campaigns_config import (
    CHANNELS,
    DIRECT_MESSAGE_CHANNELS,
    EXPOSURE_ONLY_CHANNELS,
)
from dirty_data_generation.helpers.dirty_utils import generate_future_datetime

# =============================================================================
# Missing Values
# =============================================================================


def missing_channel(df, idx):

    df.at[idx, "channel"] = None


def missing_assignment_group(df, idx):

    df.at[idx, "assignment_group"] = None


def missing_eligible(df, idx):

    df.at[idx, "eligible"] = pd.NA


def missing_exposed(df, idx):

    df.at[idx, "exposed"] = pd.NA


def missing_exposed_time(df, idx):

    df.at[idx, "exposed_time"] = None


def missing_opened(df, idx):

    df.at[idx, "opened"] = pd.NA


def missing_opened_time(df, idx):

    df.at[idx, "opened_time"] = None


def missing_clicked(df, idx):

    df.at[idx, "clicked"] = pd.NA


def missing_clicked_time(df, idx):

    df.at[idx, "clicked_time"] = None


def missing_device_platform(df, idx):

    df.at[idx, "device_platform"] = None


def missing_cost_per_msg(df, idx):

    df.at[idx, "cost_per_msg"] = None


# =============================================================================
# Accepted Values
# =============================================================================


def invalid_channel(df, idx):

    if pd.isna(df.at[idx, "channel"]):
        return

    df.at[idx, "channel"] = random.choice(
        [
            "WhatsApp",
            "Telegram",
            "Direct Mail",
            "Website",
            "",
        ]
    )


def invalid_assignment_group(df, idx):

    if pd.isna(df.at[idx, "assignment_group"]):
        return

    df.at[idx, "assignment_group"] = random.choice(
        [
            "Test",
            "Experimental",
            "Holdout",
            "",
        ]
    )


def invalid_device_platform(df, idx):

    if pd.isna(df.at[idx, "device_platform"]):
        return

    df.at[idx, "device_platform"] = random.choice(
        [
            "Windows",
            "MacOS",
            "Linux",
            "Unknown",
            "",
        ]
    )


# =============================================================================
# Range Validation
# =============================================================================


def cost_per_msg_out_of_range(df, idx):
    """
    cost_per_msg must be more than 0 and less than 100000.
    """

    value = df.at[idx, "cost_per_msg"]

    if pd.isna(value):
        return

    corruptions = [
        lambda _: 0,
        lambda x: -abs(x),
        lambda _: random.uniform(100000, 500000),
    ]

    df.at[idx, "cost_per_msg"] = random.choice(corruptions)(value)


# =============================================================================
# Business Rule Violations
# =============================================================================


def duplicate_campaign_exposure(df, idx):
    """
    Creates a duplicate (customer_id, campaign_id, channel) combination.
    """

    key_columns = ["customer_id", "campaign_id", "channel"]
    other_rows = df[df.index != idx]

    if other_rows.empty:
        return

    source_idx = random.choice(other_rows.index.tolist())

    for column in key_columns:
        df.at[idx, column] = df.at[source_idx, column]


def customer_campaign_pair_not_in_assignments(df, idx, ctx):
    """
    customer_id + campaign_id must exist in campaign_assignments.
    """

    if ctx.campaign_assignments is None:
        return

    assignments = ctx.campaign_assignments.campaign_assignments_df

    if assignments.empty:
        return

    valid_pairs = set(
        zip(
            assignments["customer_id"],
            assignments["campaign_id"],
        )
    )

    pair = (
        df.at[idx, "customer_id"],
        df.at[idx, "campaign_id"],
    )

    if pair in valid_pairs:
        df.at[idx, "customer_id"] = f"CUST_INVALID_{random.randint(100000, 999999)}"


def channel_not_in_campaign_channels(df, idx, ctx):
    """
    channel must be configured in the campaign's channels.
    """

    campaign_id = df.at[idx, "campaign_id"]
    channel = df.at[idx, "channel"]

    if pd.isna(campaign_id) or pd.isna(channel):
        return

    campaigns = ctx.campaigns.campaigns_df

    matches = campaigns[campaigns["campaign_id"] == campaign_id]

    if matches.empty:
        return

    campaign_channels = matches.iloc[0]["channels"]

    if not isinstance(campaign_channels, (list, tuple)):
        return

    invalid_channels = [value for value in CHANNELS if value not in campaign_channels]

    if invalid_channels:
        df.at[idx, "channel"] = random.choice(invalid_channels)


def device_platform_mismatch(df, idx, ctx):
    """
    device_platform must equal the customer's device_platform.
    """

    customer_id = df.at[idx, "customer_id"]

    if pd.isna(customer_id):
        return

    customers = ctx.customers.customers_df

    matches = customers[customers["customer_id"] == customer_id]

    if matches.empty:
        return

    valid_platform = matches.iloc[0]["device_platform"]

    invalid_platforms = [
        value for value in ["iOS", "Android", "Web"] if value != valid_platform
    ]

    if invalid_platforms:
        df.at[idx, "device_platform"] = random.choice(invalid_platforms)


def control_group_exposure_violation(df, idx):
    """
    Control groups must not be exposed.
    """

    assignment_group = df.at[idx, "assignment_group"]

    if pd.isna(assignment_group):
        return

    if assignment_group != "Control":
        return

    df.at[idx, "exposed"] = True

    if pd.isna(df.at[idx, "exposed_time"]):
        df.at[idx, "exposed_time"] = pd.Timestamp.today().normalize()


def assignment_group_mismatch(df, idx, ctx):
    """
    assignment_group must match the corresponding campaign assignment.
    """

    if ctx.campaign_assignments is None:
        return

    assignments = ctx.campaign_assignments.campaign_assignments_df

    customer_id = df.at[idx, "customer_id"]
    campaign_id = df.at[idx, "campaign_id"]

    if pd.isna(customer_id) or pd.isna(campaign_id):
        return

    matches = assignments[
        (assignments["customer_id"] == customer_id)
        & (assignments["campaign_id"] == campaign_id)
    ]

    if matches.empty:
        return

    correct_group = matches.iloc[0]["assignment_group"]

    df.at[idx, "assignment_group"] = (
        "Control" if correct_group == "Treatment" else "Treatment"
    )


def eligible_must_be_true(df, idx):
    """
    eligible must always be TRUE.
    """

    if pd.isna(df.at[idx, "eligible"]):
        return

    df.at[idx, "eligible"] = False


def invalid_cost_per_msg(df, idx):
    """
    cost_per_msg must equal the configured channel cost when exposed,
    and must be 0 when not exposed.
    """

    exposed = df.at[idx, "exposed"]
    channel = df.at[idx, "channel"]

    if pd.isna(exposed) or pd.isna(channel):
        return

    if exposed is True or exposed == 1:
        # Deliberately use an incorrect positive cost.
        df.at[idx, "cost_per_msg"] = random.uniform(
            1.0,
            100.0,
        )
    else:
        df.at[idx, "cost_per_msg"] = random.uniform(
            1.0,
            100.0,
        )


def exposed_without_exposed_time(df, idx):
    """
    exposed=True must have an exposed_time.
    """

    exposed = df.at[idx, "exposed"]

    if pd.isna(exposed):
        return

    if exposed is True or exposed == 1:
        df.at[idx, "exposed_time"] = None


def exposed_time_without_exposure(df, idx):
    """
    exposed=False must have exposed_time=NULL.
    """

    exposed = df.at[idx, "exposed"]

    if exposed is False or exposed == 0:
        exposed_time = df.at[idx, "exposed_time"]

        if not pd.isna(exposed_time):
            return

        return

    # Force a timestamp even if exposure is false.
    df.at[idx, "exposed"] = False

    df.at[idx, "exposed_time"] = pd.Timestamp.today().normalize() - pd.Timedelta(
        days=random.randint(1, 30)
    )


def opened_without_exposure(df, idx):
    """
    opened must not be TRUE when exposed is FALSE.
    """

    exposed = df.at[idx, "exposed"]

    if pd.isna(exposed):
        return

    if exposed is False or exposed == 0:
        df.at[idx, "opened"] = True


def clicked_without_open(df, idx):
    """
    Direct messaging channels require opened=True before clicked=True.
    """

    channel = df.at[idx, "channel"]

    if pd.isna(channel):
        return

    if channel not in DIRECT_MESSAGE_CHANNELS:
        return

    df.at[idx, "clicked"] = True
    df.at[idx, "opened"] = False


def opened_on_exposure_only_channel(df, idx):
    """
    Paid Advertisements and In-App must not have opened events.
    """

    channel = df.at[idx, "channel"]

    if channel not in EXPOSURE_ONLY_CHANNELS:
        return

    df.at[idx, "opened"] = True


def opened_without_opened_time(df, idx):
    """
    opened=True must have opened_time.
    """

    opened = df.at[idx, "opened"]

    if pd.isna(opened):
        return

    if opened is True or opened == 1:
        df.at[idx, "opened_time"] = None


def opened_time_before_exposed_time(df, idx):
    """
    opened_time must occur on or after exposed_time.
    """

    exposed_time = df.at[idx, "exposed_time"]

    if pd.isna(exposed_time):
        return

    opened_time = df.at[idx, "opened_time"]

    if pd.isna(opened_time):
        return

    exposed_time = pd.Timestamp(exposed_time)

    df.at[idx, "opened_time"] = exposed_time - timedelta(
        seconds=random.randint(1, 3600)
    )


def clicked_without_clicked_time(df, idx):
    """
    clicked=True must have clicked_time.
    """

    clicked = df.at[idx, "clicked"]

    if pd.isna(clicked):
        return

    if clicked is True or clicked == 1:
        df.at[idx, "clicked_time"] = None


def clicked_time_before_opened_time(df, idx):
    """
    clicked_time must occur on or after opened_time.
    """

    opened_time = df.at[idx, "opened_time"]

    if pd.isna(opened_time):
        return

    clicked_time = df.at[idx, "clicked_time"]

    if pd.isna(clicked_time):
        return

    opened_time = pd.Timestamp(opened_time)

    df.at[idx, "clicked_time"] = opened_time - timedelta(seconds=random.randint(1, 300))


def clicked_time_before_exposed_time(df, idx):
    """
    For direct messaging channels, clicked_time must occur on or after
    exposed_time.
    """

    channel = df.at[idx, "channel"]

    if channel in EXPOSURE_ONLY_CHANNELS:
        return

    exposed_time = df.at[idx, "exposed_time"]

    if pd.isna(exposed_time):
        return

    clicked_time = df.at[idx, "clicked_time"]

    if pd.isna(clicked_time):
        return

    exposed_time = pd.Timestamp(exposed_time)

    df.at[idx, "clicked_time"] = exposed_time - timedelta(
        seconds=random.randint(1, 300)
    )


# =============================================================================
# Date Issues
# =============================================================================


def future_exposed_time(df, idx):

    if pd.isna(df.at[idx, "exposed_time"]):
        return

    df.at[idx, "exposed_time"] = pd.Timestamp(generate_future_datetime())


def future_opened_time(df, idx):

    if pd.isna(df.at[idx, "opened_time"]):
        return

    df.at[idx, "opened_time"] = pd.Timestamp(generate_future_datetime())


def future_clicked_time(df, idx):

    if pd.isna(df.at[idx, "clicked_time"]):
        return

    df.at[idx, "clicked_time"] = pd.Timestamp(generate_future_datetime())

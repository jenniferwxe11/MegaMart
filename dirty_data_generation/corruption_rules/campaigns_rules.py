import random
from datetime import timedelta

import pandas as pd

# =============================================================================
# Missing Values
# =============================================================================


def missing_campaign_name(df, idx, ctx):

    df.at[idx, "campaign_name"] = None


def missing_campaign_type(df, idx, ctx):

    df.at[idx, "campaign_type"] = None


def missing_target_segment(df, idx, ctx):

    df.at[idx, "target_segment"] = None


def missing_channels(df, idx, ctx):

    df.at[idx, "channels"] = []


def missing_start_date(df, idx, ctx):

    df.at[idx, "start_date"] = None


def missing_end_date(df, idx, ctx):

    df.at[idx, "end_date"] = None


def missing_budget(df, idx, ctx):

    df.at[idx, "budget"] = None


def missing_is_ab_test(df, idx, ctx):

    df.at[idx, "is_ab_test"] = pd.NA


def missing_status(df, idx, ctx):

    df.at[idx, "status"] = None


# =============================================================================
# Accepted Values
# =============================================================================


def invalid_campaign_type(df, idx, ctx):
    """
    campaign_type must be one of:
        Acquisition
        Retention
        Clearance
        Seasonal
    """

    if pd.isna(df.at[idx, "campaign_type"]):
        return

    df.at[idx, "campaign_type"] = random.choice(
        [
            "Awareness",
            "Promotional",
            "Loyalty",
            "Flash Sale",
            "",
        ]
    )


def invalid_target_segment(df, idx, ctx):
    """
    target_segment must be one of:
        New Customers
        Active Customers
        Churn Risk Customers
        High Spenders
        Budget Shoppers
    """

    if pd.isna(df.at[idx, "target_segment"]):
        return

    df.at[idx, "target_segment"] = random.choice(
        [
            "VIP Customers",
            "Inactive Customers",
            "Wholesale Customers",
            "General Audience",
            "",
        ]
    )


def invalid_status(df, idx, ctx):
    """
    status must be one of:
        Planned
        Active
        Completed
        Cancelled
    """

    if pd.isna(df.at[idx, "status"]):
        return

    df.at[idx, "status"] = random.choice(
        [
            "Draft",
            "Pending",
            "Expired",
            "On Hold",
            "",
        ]
    )


# =============================================================================
# Formatting
# =============================================================================


def invalid_campaign_id_format(df, idx, ctx):

    value = df.at[idx, "campaign_id"]

    if pd.isna(value):
        return

    value = str(value)

    corruptions = [
        lambda x: x.replace("000", "00", 1),
        lambda x: x.replace("CAMP", "CAMP-", 1),
        lambda x: x.lower(),
        lambda x: x.replace("CAMP", "CAM", 1),
        lambda x: x.replace("CAMP", "CAMPAIGN", 1),
        lambda x: x.replace("CAMP", "", 1),
        lambda x: x.replace("CAMP", "CAMP_", 1),
        lambda x: x.replace("CAMP", "CAMP ", 1),
    ]

    df.at[idx, "campaign_id"] = random.choice(corruptions)(value)


def invalid_campaign_name(df, idx, ctx):
    """
    campaign_name must start with 'MegaMart'.
    """

    value = df.at[idx, "campaign_name"]

    if pd.isna(value):
        return

    value = str(value)

    corruptions = [
        lambda x: x.replace("MegaMart", "Megamart", 1),
        lambda x: x.replace("MegaMart", "Mega Mart", 1),
        lambda x: x.replace("MegaMart", "Mega", 1),
        lambda x: " " + x,
        lambda x: x.replace("MegaMart", "", 1).lstrip(),
    ]

    df.at[idx, "campaign_name"] = random.choice(corruptions)(value)


# =============================================================================
# Range Validation
# =============================================================================


def budget_out_of_range(df, idx, ctx):
    """
    budget must be more than 0 and less than 10000000.
    """

    value = df.at[idx, "budget"]

    if pd.isna(value):
        return

    corruptions = [
        lambda _: 0,
        lambda x: -abs(x),
        lambda _: random.uniform(10000001, 20000000),
    ]

    df.at[idx, "budget"] = random.choice(corruptions)(value)


# =============================================================================
# Business Rule Violations
# =============================================================================


def duplicate_channel_inside_channels(df, idx, ctx):
    """
    channels must not contain duplicate channel values.
    """

    channels = df.at[idx, "channels"]

    if not isinstance(channels, list) or not channels:
        return

    channel = random.choice(channels)
    df.at[idx, "channels"] = channels + [channel]


def invalid_campaign_period(df, idx, ctx):
    """
    start_date must be <= end_date.
    """

    start = df.at[idx, "start_date"]
    end = df.at[idx, "end_date"]

    if pd.isna(start) or pd.isna(end):
        return

    start = pd.Timestamp(start)
    end = pd.Timestamp(end)

    if start <= end:
        df.at[idx, "start_date"] = end + timedelta(days=random.randint(1, 30))


def season_campaign_type_inconsistency(df, idx, ctx):
    """
    Seasonal campaigns must have a season.
    Non-seasonal campaigns must have NULL season.
    """

    campaign_type = df.at[idx, "campaign_type"]

    if pd.isna(campaign_type):
        return

    if campaign_type == "Seasonal":
        df.at[idx, "season"] = None
    else:
        df.at[idx, "season"] = random.choice(
            [
                "Chinese New Year",
                "Christmas",
                "11.11",
                "Hari Raya",
                "Black Friday",
            ]
        )


def campaign_without_marketing_channels(df, idx, ctx):
    """
    Campaign must contain at least one marketing channel.
    """

    channels = df.at[idx, "channels"]

    if channels is None:
        return

    if not isinstance(channels, (list, tuple)):
        return

    if len(channels) == 0:
        return

    df.at[idx, "channels"] = []


def completed_campaign_future_end_date(df, idx, ctx):
    """
    Completed campaigns must not have an end_date in the future.
    """

    status = df.at[idx, "status"]

    if pd.isna(status):
        return

    if status != "Completed":
        return

    df.at[idx, "end_date"] = pd.Timestamp.today().normalize() + pd.Timedelta(
        days=random.randint(1, 365)
    )

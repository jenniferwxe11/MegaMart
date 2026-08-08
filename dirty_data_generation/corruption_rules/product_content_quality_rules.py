# dirty_data_generation/corruption_rules/product_content_quality_rules.py

import random

import pandas as pd
from faker import Faker

fake = Faker()


# =============================================================================
# Missing Values
# =============================================================================


def missing_quality_tier(df, idx, ctx):

    df.at[idx, "quality_tier"] = None


def missing_has_image(df, idx, ctx):

    df.at[idx, "has_image"] = pd.NA


def missing_image_count(df, idx, ctx):

    df.at[idx, "image_count"] = None


def missing_has_description(df, idx, ctx):

    df.at[idx, "has_description"] = pd.NA


def missing_description_length(df, idx, ctx):

    df.at[idx, "description_length"] = None


def missing_attribute_count(df, idx, ctx):

    df.at[idx, "missing_attribute_count"] = None


# =============================================================================
# Formatting
# =============================================================================


def invalid_content_version_id_format(df, idx, ctx):

    value = df.at[idx, "content_version_id"]

    if pd.isna(value):
        return

    corruptions = [
        lambda x: x.replace("000", "00", 1),
        lambda x: x.replace("PCQ", "PCQ-", 1),
        lambda x: x.lower(),
        lambda x: x.replace("PCQ", "P", 1),
        lambda x: x.replace("PCQ", "PCQ ", 1),
    ]

    df.at[idx, "content_version_id"] = random.choice(corruptions)(value)


# =============================================================================
# Duplicates
# =============================================================================


def duplicate_content_version_id(df, idx, ctx):

    other_content_version_ids = (
        df[df.index != idx]["content_version_id"].dropna().tolist()
    )

    if not other_content_version_ids:
        return

    df.at[idx, "content_version_id"] = random.choice(other_content_version_ids)


# =============================================================================
# Range Validation
# =============================================================================


def image_quality_score_out_of_bounds(df, idx, ctx):
    """
    The image_quality_score should be between 0 and 1.
    """

    value = df.at[idx, "image_quality_score"]

    if pd.isna(value):
        return

    corruptions = [lambda x: -abs(x), lambda _: round(random.uniform(1.01, 1.5), 2)]

    df.at[idx, "image_quality_score"] = random.choice(corruptions)(value)


def description_length_out_of_bounds(df, idx, ctx):
    """
    The description_length should be between 0 and 400.
    """

    value = df.at[idx, "description_length"]

    if pd.isna(value):
        return

    corruptions = [lambda x: -abs(x), lambda _: random.randint(401, 1000)]

    df.at[idx, "description_length"] = random.choice(corruptions)(value)


def missing_attribute_count_out_of_bounds(df, idx, ctx):
    """
    The missing_attribute_count should be between 0 and 20.
    """

    value = df.at[idx, "missing_attribute_count"]

    if pd.isna(value):
        return

    corruptions = [lambda x: -abs(x), lambda _: random.randint(21, 100)]

    df.at[idx, "missing_attribute_count"] = random.choice(corruptions)(value)


# =============================================================================
# Business Rule Violations
# =============================================================================


def future_valid_from(df, idx, ctx):

    if pd.isna(df.at[idx, "valid_from"]):
        return

    df.at[idx, "valid_from"] = pd.Timestamp(fake.future_date("+5y"))


def image_indicator_mismatch(df, idx, ctx):
    """
    If has_image is False, then image_count should be 0.
    If has_image is True, then image_count should be greater than 0.
    """
    if pd.isna(df.at[idx, "has_image"]):
        return

    if df.at[idx, "has_image"] is False:
        df.at[idx, "image_count"] = random.randint(1, 8)
    else:
        df.at[idx, "image_count"] = 0


def description_indicator_mismatch(df, idx, ctx):
    """
    If has_description is False, then description_length should be 0.
    If has_description is True, then description_length should be greater than 0.
    """
    if pd.isna(df.at[idx, "has_description"]):
        return

    if df.at[idx, "has_description"] is False:
        df.at[idx, "description_length"] = random.randint(1, 400)
    else:
        df.at[idx, "description_length"] = 0


def invalid_validity_period(df, idx, ctx):
    """
    The valid_from date should be less than or equal to the valid_to date.
    """

    if pd.isna(df.at[idx, "valid_from"]) or pd.isna(df.at[idx, "valid_to"]):
        return

    df.at[idx, "valid_to"] = df.at[idx, "valid_from"] - pd.Timedelta(
        days=random.randint(1, 365)
    )


def current_record_has_end_date(df, idx, ctx):
    """
    If is_current is True, then valid_to should be None.
    """

    if pd.isna(df.at[idx, "is_current"]):
        return

    if df.at[idx, "is_current"] is True:
        if pd.isna(df.at[idx, "valid_to"]):
            df.at[idx, "valid_to"] = df.at[idx, "valid_from"]


def historical_record_without_end_date(df, idx, ctx):

    if pd.isna(df.at[idx, "is_current"]):
        return

    if df.at[idx, "is_current"] is False:
        df.at[idx, "valid_to"] = pd.NaT


def multiple_current_records(df, idx, ctx):
    """
    The same product should only have one current record.
    Creates two records for the same product
    with is_current set to True and valid_to set to None.
    """

    product_id = df.at[idx, "product_id"]

    others = df[(df["product_id"] == product_id) & (df.index != idx)]

    if others.empty:
        return

    other_idx = random.choice(others.index.tolist())

    df.at[idx, "is_current"] = True
    df.at[idx, "valid_to"] = pd.NaT

    df.at[other_idx, "is_current"] = True
    df.at[other_idx, "valid_to"] = pd.NaT


def overlapping_validity_period(df, idx, ctx):
    """
    Products with the same product_id should not have overlapping validity periods.
    Creates two records for the same product with overlapping validity periods.
    """

    product_id = df.at[idx, "product_id"]

    others = df[(df["product_id"] == product_id) & (df.index != idx)]

    if others.empty:
        return

    other_idx = random.choice(others.index.tolist())
    other_from = df.at[other_idx, "valid_from"]
    other_to = df.at[other_idx, "valid_to"]

    if pd.isna(other_from) or pd.isna(other_to):
        return

    df.at[idx, "valid_from"] = other_from + pd.Timedelta(days=10)
    df.at[idx, "valid_to"] = other_to + pd.Timedelta(days=10)


def incorrect_quality_tier(df, idx, ctx):
    """
    Quality tier inconsistent with content metrics.
    """

    quality_tier = df.at[idx, "quality_tier"]

    TIERS = ["Poor", "Average", "Good", "Excellent"]

    other_quality_tiers = [tier for tier in TIERS if tier != quality_tier]
    df.at[idx, "quality_tier"] = random.choice(other_quality_tiers)


def quality_tier_regression(df, idx, ctx):

    TIER_ORDER = {
        "Poor": 0,
        "Average": 1,
        "Good": 2,
        "Excellent": 3,
    }

    TIERS = ["Poor", "Average", "Good", "Excellent"]

    product_id = df.at[idx, "product_id"]

    rows = df[df["product_id"] == product_id].sort_values("valid_from")

    if len(rows) < 2:
        return

    latest_idx = rows.index[-1]
    previous_idx = rows.index[-2]

    previous_tier = df.at[previous_idx, "quality_tier"]

    if previous_tier == "Poor":
        return

    df.at[latest_idx, "quality_tier"] = TIERS[TIER_ORDER[previous_tier] - 1]

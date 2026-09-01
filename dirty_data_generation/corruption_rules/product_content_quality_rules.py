# dirty_data_generation/corruption_rules/product_content_quality_rules.py

import random

import pandas as pd

from data_generation.config.product_content_config import TIERS
from dirty_data_generation.helpers.dirty_utils import generate_future_date

# =============================================================================
# Missing Values
# =============================================================================


def missing_quality_tier(df, idx):

    df.at[idx, "quality_tier"] = None


def missing_has_image(df, idx):

    df.at[idx, "has_image"] = pd.NA


def missing_image_count(df, idx):

    df.at[idx, "image_count"] = None


def missing_has_description(df, idx):

    df.at[idx, "has_description"] = pd.NA


def missing_description_length(df, idx):

    df.at[idx, "description_length"] = None


def missing_attribute_count(df, idx):

    df.at[idx, "missing_attribute_count"] = None


def missing_has_nutritional_info(df, idx):
    df.at[idx, "has_nutritional_info"] = pd.NA


# =============================================================================
# Formatting
# =============================================================================


def invalid_content_version_id_format(df, idx):

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


def duplicate_content_version_id(df, idx):

    other_content_version_ids = (
        df[df.index != idx]["content_version_id"].dropna().tolist()
    )

    if not other_content_version_ids:
        return

    df.at[idx, "content_version_id"] = random.choice(other_content_version_ids)


# =============================================================================
# Range Validation
# =============================================================================


def image_quality_score_out_of_range(df, idx):
    """
    The image_quality_score must be between 0 and 1 inclusive.
    """

    value = df.at[idx, "image_quality_score"]

    if pd.isna(value):
        return

    corruptions = [lambda x: -abs(x), lambda _: round(random.uniform(1.01, 1.5), 2)]

    df.at[idx, "image_quality_score"] = random.choice(corruptions)(value)


def description_length_out_of_range(df, idx):
    """
    The description_length must be between 0 and 400 inclusive.
    """

    value = df.at[idx, "description_length"]

    if pd.isna(value):
        return

    corruptions = [lambda x: -abs(x), lambda _: random.randint(401, 1000)]

    df.at[idx, "description_length"] = random.choice(corruptions)(value)


def missing_attribute_count_out_of_range(df, idx):
    """
    The missing_attribute_count must be between 0 and 20 inclusive.
    """

    value = df.at[idx, "missing_attribute_count"]

    if pd.isna(value):
        return

    corruptions = [lambda x: -abs(x), lambda _: random.randint(21, 100)]

    df.at[idx, "missing_attribute_count"] = random.choice(corruptions)(value)


# =============================================================================
# Business Rule Violations
# =============================================================================


def no_current_record(df, idx):

    product_id = df.at[idx, "product_id"]

    rows = df[df["product_id"] == product_id]

    if rows.empty:
        return

    df.loc[rows.index, "is_current"] = False
    df.loc[rows.index, "valid_to"] = df.loc[rows.index, "valid_to"].fillna(
        pd.Timestamp.today().normalize()
    )


def future_valid_from(df, idx):

    if pd.isna(df.at[idx, "valid_from"]):
        return

    df.at[idx, "valid_from"] = pd.Timestamp(generate_future_date())


def image_indicator_mismatch(df, idx):
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


def image_quality_indicator_mismatch(df, idx):
    """
    If has_image is False, then image_quality_score should be None.
    If has_image is True, then image_quality_score should not be None.
    """

    if pd.isna(df.at[idx, "has_image"]):
        return

    if df.at[idx, "has_image"] is False:
        df.at[idx, "image_quality_score"] = round(random.uniform(0.1, 1.0), 2)
    else:
        df.at[idx, "image_quality_score"] = None


def image_quality_without_image_count(df, idx):
    """
    If image_count is missing, image_quality_score should also be missing.
    """

    if pd.isna(df.at[idx, "image_count"]):
        df.at[idx, "image_quality_score"] = round(random.uniform(0.1, 1.0), 2)


def description_indicator_mismatch(df, idx):
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


def invalid_validity_period(df, idx):
    """
    The valid_from date should be less than or equal to the valid_to date.
    """

    if pd.isna(df.at[idx, "valid_from"]) or pd.isna(df.at[idx, "valid_to"]):
        return

    df.at[idx, "valid_to"] = df.at[idx, "valid_from"] - pd.Timedelta(
        days=random.randint(1, 365)
    )


def current_record_has_end_date(df, idx):
    """
    If is_current is True, then valid_to should be None.
    """

    if pd.isna(df.at[idx, "is_current"]):
        return

    if df.at[idx, "is_current"] is True:
        if pd.isna(df.at[idx, "valid_to"]):
            df.at[idx, "valid_to"] = df.at[idx, "valid_from"]


def historical_record_without_end_date(df, idx):

    if pd.isna(df.at[idx, "is_current"]):
        return

    if df.at[idx, "is_current"] is False:
        df.at[idx, "valid_to"] = pd.NaT


def multiple_current_records(df, idx):
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


def overlapping_validity_period(df, idx):
    """
    Products with the same product_id should not have overlapping validity periods.
    Creates two records for the same product with overlapping validity periods.
    """

    product_id = df.at[idx, "product_id"]

    others = df[(df["product_id"] == product_id) & (df.index != idx)]

    if others.empty:
        return

    valid_others = others[others["valid_from"].notna() & others["valid_to"].notna()]

    if valid_others.empty:
        return

    other_idx = random.choice(valid_others.index.tolist())

    other_from = df.at[other_idx, "valid_from"]
    other_to = df.at[other_idx, "valid_to"]

    if other_to <= other_from:
        return

    overlap_start = other_from + (other_to - other_from) / 2

    df.at[idx, "valid_from"] = overlap_start
    df.at[idx, "valid_to"] = other_to


def incorrect_quality_tier(df, idx):
    """
    Quality tier inconsistent with content metrics.
    """

    quality_tier = df.at[idx, "quality_tier"]

    other_quality_tiers = [tier for tier in TIERS if tier != quality_tier]
    df.at[idx, "quality_tier"] = random.choice(other_quality_tiers)


def quality_tier_regression(df, idx):
    """
    Makes the latest content version regress one quality tier
    from the previous version.
    """

    product_id = df.at[idx, "product_id"]

    rows = df[df["product_id"] == product_id].sort_values("valid_from")

    if len(rows) < 2:
        return

    latest_idx = rows.index[-1]
    previous_idx = rows.index[-2]

    previous_tier = df.at[previous_idx, "quality_tier"]

    if previous_tier not in TIERS:
        return

    tier_index = TIERS.index(previous_tier)

    if tier_index == 0:
        return

    df.at[latest_idx, "quality_tier"] = TIERS[tier_index - 1]

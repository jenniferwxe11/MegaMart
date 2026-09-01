# dirty_data_generation/corruption_rules/competitor_price_history_rules.py

import random

import pandas as pd

from dirty_data_generation.helpers.dirty_utils import generate_future_date

# =============================================================================
# Missing Values
# =============================================================================


def missing_competitor(df, idx):
    df.at[idx, "competitor"] = None


def missing_scraped_product_name(df, idx):
    df.at[idx, "scraped_product_name"] = None


def missing_scraped_category(df, idx):
    df.at[idx, "scraped_category"] = None


def missing_scraped_price(df, idx):
    df.at[idx, "scraped_price"] = None


def missing_update_timestamp(df, idx):
    df.at[idx, "update_timestamp"] = None


# =============================================================================
# Range Validation
# =============================================================================


def scraped_price_out_of_range(df, idx):
    """
    scraped_price must be more than 0 and less than 100000.
    """

    value = df.at[idx, "scraped_price"]

    if pd.isna(value):
        return

    corruptions = [
        lambda _: 0,
        lambda x: -abs(x),
        lambda _: round(random.uniform(100001, 250000), 2),
    ]

    df.at[idx, "scraped_price"] = random.choice(corruptions)(value)


# =============================================================================
# Business Rule Violations
# =============================================================================


def future_update_timestamp(df, idx):

    value = df.at[idx, "update_timestamp"]

    if pd.isna(value):
        return

    df.at[idx, "update_timestamp"] = pd.Timestamp(generate_future_date())


def duplicate_competitor_scrape_record(df, idx):
    """
    Creates a duplicate (competitor, scraped_product_name, update_timestamp)
    combination.
    """

    key_columns = [
        "competitor",
        "scraped_product_name",
        "update_timestamp",
    ]

    other_rows = df[df.index != idx]

    if other_rows.empty:
        return

    source_idx = random.choice(other_rows.index.tolist())
    source = df.loc[source_idx]

    if any(pd.isna(source[column]) for column in key_columns):
        return

    for column in key_columns:
        df.at[idx, column] = source[column]

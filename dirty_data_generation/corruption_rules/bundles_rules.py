# dirty_data_generation/corruption_rules/bundles_rules.py

import random

import pandas as pd

# =============================================================================
# Missing Values
# =============================================================================


def missing_bundle_name(df, idx, ctx):

    df.at[idx, "bundle_name"] = None


def missing_bundle_type(df, idx, ctx):

    df.at[idx, "bundle_type"] = None


def missing_categories(df, idx, ctx):

    df.at[idx, "categories"] = None


# =============================================================================
# Formatting
# =============================================================================


def invalid_bundle_id_format(df, idx, ctx):

    value = df.at[idx, "bundle_id"]

    if pd.isna(value):
        return

    corruptions = [
        lambda x: x.replace("000", "00", 1),
        lambda x: x.replace("BUNDLE", "BUNDLE-", 1),
        lambda x: x.lower(),
        lambda x: x.replace("BUNDLE", "BUN", 1),
        lambda x: x.replace("BUNDLE", "B", 1),
        lambda x: x.replace("BUNDLE", "BUNDLE ", 1),
    ]

    df.at[idx, "bundle_id"] = random.choice(corruptions)(value)


# =============================================================================
# Business Rule Violations
# =============================================================================


def duplicate_category_inside_bundle(df, idx, ctx):
    """
    Categories within a bundle should not contain duplicate values.
    """

    categories = df.at[idx, "categories"]

    if categories is None or pd.isna(categories):
        return

    if len(categories) == 0:
        return

    unique_categories = list(dict.fromkeys(categories))

    if len(unique_categories) < 2:
        return

    category = random.choice(unique_categories)

    # Add a duplicate category.
    corrupted_categories = list(categories)
    corrupted_categories.append(category)

    df.at[idx, "categories"] = corrupted_categories


def empty_bundle_categories(df, idx, ctx):
    """
    Every bundle should contain at least one category.
    """

    categories = df.at[idx, "categories"]

    if categories is None or pd.isna(categories):
        return

    df.at[idx, "categories"] = []

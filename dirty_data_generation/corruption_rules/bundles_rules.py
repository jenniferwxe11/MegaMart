# dirty_data_generation/corruption_rules/bundles_rules.py

import random

import pandas as pd

# =============================================================================
# Missing Values
# =============================================================================


def missing_bundle_name(df, idx):

    df.at[idx, "bundle_name"] = None


def missing_bundle_type(df, idx):

    df.at[idx, "bundle_type"] = None


def missing_categories(df, idx):

    df.at[idx, "categories"] = None


# =============================================================================
# Formatting
# =============================================================================


def invalid_bundle_id_format(df, idx):

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


def duplicate_category_inside_bundle(df, idx):
    """
    Categories within a bundle should not contain duplicate values.
    """

    categories = df.at[idx, "categories"]

    if not isinstance(categories, (list, tuple)) or not categories:
        return

    category = random.choice(categories)

    corrupted_categories = list(categories)
    corrupted_categories.append(category)

    df.at[idx, "categories"] = corrupted_categories


def empty_bundle_categories(df, idx):
    """
    Every bundle should contain at least one category.
    """

    categories = df.at[idx, "categories"]

    if categories is None:
        return

    if not isinstance(categories, (list, tuple)):
        return

    if len(categories) == 0:
        return

    df.at[idx, "categories"] = []

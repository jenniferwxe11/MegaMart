# dirty_data_generation/corruption_rules/product_reviews_rules.py

import random

import pandas as pd
from faker import Faker

fake = Faker()

# =============================================================================
# Missing Values
# =============================================================================


def missing_review_date(df, idx, ctx):

    df.at[idx, "review_date"] = None


def missing_rating(df, idx, ctx):

    df.at[idx, "rating"] = None


# =============================================================================
# Formatting
# =============================================================================


def invalid_review_id_format(df, idx, ctx):

    value = df.at[idx, "review_id"]

    if pd.isna(value):
        return

    corruptions = [
        lambda x: x.replace("000", "00", 1),
        lambda x: x.replace("REV", "REV-", 1),
        lambda x: x.lower(),
        lambda x: x.replace("REV", "R", 1),
        lambda x: x.replace("REV", "REVIEW", 1),
        lambda x: x.replace("REV", "REV ", 1),
    ]

    df.at[idx, "review_id"] = random.choice(corruptions)(value)


# =============================================================================
# Duplicates
# =============================================================================


def duplicate_review_id(df, idx, ctx):

    other_review_ids = df[df.index != idx]["review_id"].dropna().tolist()

    if not other_review_ids:
        return

    df.at[idx, "review_id"] = random.choice(other_review_ids)


# =============================================================================
# Range Validation
# =============================================================================


def rating_out_of_bounds(df, idx, ctx):
    """
    Rating should be between 1 and 5.
    """

    value = df.at[idx, "rating"]

    if pd.isna(value):
        return

    corruptions = [
        lambda _: 0,
        lambda x: -abs(x),
        lambda _: random.randint(6, 10),
    ]

    df.at[idx, "rating"] = random.choice(corruptions)(value)


# =============================================================================
# Business Rule Violations
# =============================================================================


def future_review_date(df, idx, ctx):

    if pd.isna(df.at[idx, "review_date"]):
        return

    df.at[idx, "review_date"] = pd.Timestamp(fake.future_date("+5y"))


def review_before_transaction(df, idx, ctx):
    """
    Review date occurs before the transaction date.
    """

    transaction_id = df.at[idx, "transaction_id"]

    transaction = ctx.transactions.transactions_df.loc[
        ctx.transactions.transactions_df["transaction_id"] == transaction_id
    ]

    if transaction.empty:
        return

    transaction_date = pd.Timestamp(transaction.iloc[0]["transaction_time"])

    df.at[idx, "review_date"] = transaction_date - pd.Timedelta(
        days=random.randint(1, 30)
    )


def duplicate_transaction_product_pair(df, idx, ctx):
    """
    Duplicate (transaction_id, product_id) combination.
    """
    others = df[df.index != idx]

    if others.empty:
        return

    other = others.sample(1).iloc[0]

    df.at[idx, "transaction_id"] = other["transaction_id"]
    df.at[idx, "product_id"] = other["product_id"]

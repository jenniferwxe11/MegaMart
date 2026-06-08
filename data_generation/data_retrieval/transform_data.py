import ast

import pandas as pd

from data_generation.data_retrieval import load_data


# ─────────────────────────────────────────────────────────────
# DERIVED DATASETS
# ─────────────────────────────────────────────────────────────
def sorted_clickstream():
    return (
        load_data.load_clickstreams()
        .copy()
        .sort_values(["session_id", "timestamp"])
        .reset_index(drop=True)
    )


def get_product_with_lifecycle():
    return (
        load_data.load_products()
        .copy()
        .merge(
            load_data.load_product_lifecycles(),
            on="product_id",
            how="inner",
        )
    )


def get_bundle_full():
    return (
        load_data.load_bundle_pricings()
        .copy()
        .merge(
            load_data.load_bundles(),
            on="bundle_id",
            how="left",
        )
    )


# ─────────────────────────────────────────────────────────────
# TYPE PARSING
# ─────────────────────────────────────────────────────────────
def parse_channels(value):
    if pd.isna(value):
        return []
    return ast.literal_eval(value)


def get_campaigns_df():
    df = load_data.load_campaigns().copy()
    df.loc[:, "is_ab_test"] = (
        df["is_ab_test"].astype(str).str.lower().map({"true": True, "false": False})
    )
    df.loc[:, "channels"] = df["channels"].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else x
    )
    return df

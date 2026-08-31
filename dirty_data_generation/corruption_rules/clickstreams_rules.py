# dirty_data_generation/corruption_rules/clickstreams_rules.py

import random

import pandas as pd
from faker import Faker

from data_generation.config.clickstreams_config import EVENT_PAGE_MAPPING
from data_generation.config.customers_config import (
    DEVICE_CATEGORY,
    TARGET_SEGMENT,
)
from data_generation.config.products_config import CATEGORIES
from data_generation.config.stocks_config import STOCK_STATUSES
from dirty_data_generation.config.constants import MAX_ERRORS_PER_ROW

fake = Faker()


# =============================================================================
# Error Helpers
# =============================================================================


def _can_add_error(df, idx) -> bool:
    """
    Check whether another corruption can be applied to this row.

    error_count stores the number of corruptions applied to the row.
    """

    value = df.at[idx, "error_count"]

    if pd.isna(value):
        return True

    return int(value) < MAX_ERRORS_PER_ROW


def _add_error(df, idx) -> bool:
    """
    Increment error_count by one.

    Returns True if the error was successfully recorded.
    """

    if not _can_add_error(df, idx):
        return False

    current = df.at[idx, "error_count"]

    if pd.isna(current):
        current = 0

    df.at[idx, "error_count"] = int(current) + 1

    return True


def _is_missing(value) -> bool:
    """
    Safely check whether a scalar value is missing.

    Avoids pd.isna(list), which returns an array.
    """

    if value is None:
        return True

    if isinstance(value, (list, tuple)):
        return False

    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False


# =============================================================================
# Missing Values
# =============================================================================


def missing_customer_segment(df, idx):
    if not _add_error(df, idx):
        return

    df.at[idx, "customer_segment"] = None


def missing_device_category(df, idx):
    if not _add_error(df, idx):
        return

    df.at[idx, "device_category"] = None


def missing_referrer(df, idx):
    if not _add_error(df, idx):
        return

    df.at[idx, "referrer"] = None


def missing_location(df, idx):
    if not _add_error(df, idx):
        return

    df.at[idx, "location"] = None


def missing_event_timestamp(df, idx):
    if not _add_error(df, idx):
        return

    df.at[idx, "event_timestamp"] = None


def missing_event_order(df, idx):
    if not _add_error(df, idx):
        return

    df.at[idx, "event_order"] = None


def missing_event_type(df, idx):
    if not _add_error(df, idx):
        return

    df.at[idx, "event_type"] = None


def missing_page(df, idx):
    if not _add_error(df, idx):
        return

    df.at[idx, "page"] = None


def missing_scroll_depth(df, idx):
    if not _add_error(df, idx):
        return

    df.at[idx, "scroll_depth"] = None


def missing_bounce_flag(df, idx):
    if not _add_error(df, idx):
        return

    df.at[idx, "bounce_flag"] = None


def missing_cart_content(df, idx):
    if not _add_error(df, idx):
        return

    df.at[idx, "cart_content"] = None


def missing_cart_size(df, idx):
    if not _add_error(df, idx):
        return

    df.at[idx, "cart_size"] = None


def missing_purchased_items(df, idx):
    if not _add_error(df, idx):
        return

    df.at[idx, "purchased_items"] = None


# =============================================================================
# ID Formatting
# =============================================================================


def invalid_clickstream_id_format(df, idx):

    value = df.at[idx, "clickstream_id"]

    if _is_missing(value):
        return

    if not _can_add_error(df, idx):
        return

    value = str(value)

    corruptions = [
        # Remove event-order separator.
        lambda x: x.replace("_", "", 1),
        # Replace separator.
        lambda x: x.replace("_", "-", 1),
        # Remove part of UUID.
        lambda x: (
            x.split("_")[0][:-1] + "_" + x.split("_")[1] if "_" in x else x[:-1]
        ),
        # Add character.
        lambda x: "X" + x,
        # Invalid separator.
        lambda x: x.replace("_", "X_", 1),
        # Remove event-order portion.
        lambda x: x.split("_")[0],
        # Non-numeric event order.
        lambda x: (x.rsplit("_", 1)[0] + "_abc" if "_" in x else x + "_abc"),
        # Extra suffix.
        lambda x: x + "_extra",
        # Whitespace.
        lambda x: f" {x}",
        lambda x: f"{x} ",
    ]

    if _add_error(df, idx):
        df.at[idx, "clickstream_id"] = random.choice(corruptions)(value)


def invalid_session_id_format(df, idx):

    value = df.at[idx, "session_id"]

    if _is_missing(value):
        return

    if not _can_add_error(df, idx):
        return

    value = str(value)

    corruptions = [
        lambda x: x.replace("-", "", 1),
        lambda x: x.replace("-", "_", 1),
        lambda x: x[:10] + x[11:],
        lambda x: x[:10] + "X" + x[10:],
        lambda x: x[:10] + "X" + x[11:],
        lambda x: x + "_extra",
        lambda x: f" {x}",
        lambda x: f"{x} ",
    ]

    if _add_error(df, idx):
        df.at[idx, "session_id"] = random.choice(corruptions)(value)


# =============================================================================
# Accepted Values / Categorical Data
# =============================================================================


def invalid_customer_segment(df, idx):

    value = df.at[idx, "customer_segment"]

    if _is_missing(value):
        return

    invalid_values = [
        "Unknown Customers",
        "VIP Customers",
        "Inactive Customers",
        "Other",
        "",
        "Invalid Segment",
    ]

    if _add_error(df, idx):
        df.at[idx, "customer_segment"] = random.choice(invalid_values)


def invalid_device_category(df, idx):

    value = df.at[idx, "device_category"]

    if _is_missing(value):
        return

    invalid_values = [
        "Phone",
        "Laptop",
        "PC",
        "Smartphone",
        "Other",
        "Unknown",
        "",
    ]

    if _add_error(df, idx):
        df.at[idx, "device_category"] = random.choice(invalid_values)


def invalid_referrer(df, idx):

    value = df.at[idx, "referrer"]

    if _is_missing(value):
        return

    invalid_values = [
        "google",
        "facebook",
        "instagram",
        "paid_search",
        "affiliate",
        "other",
        "",
    ]

    if _add_error(df, idx):
        df.at[idx, "referrer"] = random.choice(invalid_values)


def invalid_event_type(df, idx):

    value = df.at[idx, "event_type"]

    if _is_missing(value):
        return

    invalid_values = [
        "Home",
        "Homepage",
        "Product",
        "Add Cart",
        "Checkout",
        "Payment",
        "Unknown Event",
        "",
    ]

    if _add_error(df, idx):
        df.at[idx, "event_type"] = random.choice(invalid_values)


def invalid_bounce_flag(df, idx):

    value = df.at[idx, "bounce_flag"]

    if _is_missing(value):
        return

    corruptions = [
        lambda _: -random.randint(2, 100),
        lambda _: random.randint(2, 100),
    ]

    if _add_error(df, idx):
        df.at[idx, "bounce_flag"] = random.choice(corruptions)(value)


def invalid_stock_status(df, idx):

    value = df.at[idx, "stock_status"]

    if _is_missing(value):
        return

    invalid_values = [
        "Available",
        "Sold Out",
        "Unknown",
        "Normal",
        "",
    ]

    if _add_error(df, idx):
        df.at[idx, "stock_status"] = random.choice(invalid_values)


# =============================================================================
# Range Validation
# =============================================================================


def invalid_event_order_range(df, idx):

    value = df.at[idx, "event_order"]

    if _is_missing(value):
        return

    corruptions = [
        lambda _: 0,
        lambda x: -abs(x),
        lambda _: random.randint(100001, 250000),
    ]

    if _add_error(df, idx):
        df.at[idx, "event_order"] = random.choice(corruptions)(value)


def invalid_scroll_depth_range(df, idx):

    value = df.at[idx, "scroll_depth"]

    if _is_missing(value):
        return

    corruptions = [
        lambda x: -abs(x),
        lambda _: random.uniform(101, 200),
    ]

    if _add_error(df, idx):
        df.at[idx, "scroll_depth"] = random.choice(corruptions)(value)


def invalid_cart_size_range(df, idx):

    value = df.at[idx, "cart_size"]

    if _is_missing(value):
        return

    corruptions = [
        lambda x: -abs(x),
        lambda _: random.randint(100001, 250000),
    ]

    if _add_error(df, idx):
        df.at[idx, "cart_size"] = random.choice(corruptions)(value)


# =============================================================================
# Customer Consistency
# =============================================================================


def customer_segment_mismatch(df, idx, ctx):

    customer_id = df.at[idx, "customer_id"]

    if _is_missing(customer_id):
        return

    customers_df = ctx.customers.customers_df

    customer_rows = customers_df[customers_df["customer_id"] == customer_id]

    if customer_rows.empty:
        return

    expected_segment = customer_rows.iloc[0]["customer_segment"]

    invalid_segments = [value for value in TARGET_SEGMENT if value != expected_segment]

    if not invalid_segments:
        return

    if _add_error(df, idx):
        df.at[idx, "customer_segment"] = random.choice(invalid_segments)


def device_category_mismatch(df, idx, ctx):

    customer_id = df.at[idx, "customer_id"]

    if _is_missing(customer_id):
        return

    customers_df = ctx.customers.customers_df

    customer_rows = customers_df[customers_df["customer_id"] == customer_id]

    if customer_rows.empty:
        return

    expected_device = customer_rows.iloc[0]["device_category"]

    invalid_devices = [
        value for value in DEVICE_CATEGORY.keys() if value != expected_device
    ]

    if not invalid_devices:
        return

    if _add_error(df, idx):
        df.at[idx, "device_category"] = random.choice(invalid_devices)


# =============================================================================
# Product Consistency
# =============================================================================


def product_information_mismatch(df, idx, ctx):
    """
    product_name and/or category should match product_id.
    """

    product_id = df.at[idx, "product_id"]

    if _is_missing(product_id):
        return

    products_df = ctx.products.products_df

    product_rows = products_df[products_df["product_id"] == product_id]

    if product_rows.empty:
        return

    corruption = random.choice(
        [
            "name",
            "category",
            "both",
        ]
    )

    corrupted = False

    if corruption in ("name", "both"):

        other_products = products_df[products_df["product_id"] != product_id]

        if not other_products.empty:
            other_names = other_products["product_name"].dropna().tolist()

            if other_names:
                df.at[idx, "product_name"] = random.choice(other_names)
                corrupted = True

    if corruption in ("category", "both"):

        expected_category = product_rows.iloc[0]["category"]

        invalid_categories = [
            category for category in CATEGORIES if category != expected_category
        ]

        if invalid_categories:
            df.at[idx, "category"] = random.choice(invalid_categories)
            corrupted = True

    if corrupted:
        _add_error(df, idx)


# =============================================================================
# Campaign Logic
# =============================================================================


def treatment_campaign_without_campaign(df, idx):

    campaign_ids = df.at[idx, "campaign_ids"]

    if isinstance(campaign_ids, (list, tuple)):
        if len(campaign_ids) > 0:
            if _add_error(df, idx):
                df.at[idx, "has_treatment_campaign"] = True
                df.at[idx, "campaign_ids"] = []

    elif campaign_ids is not None:
        if _add_error(df, idx):
            df.at[idx, "has_treatment_campaign"] = True
            df.at[idx, "campaign_ids"] = []


def control_campaign_without_campaign(df, idx):

    campaign_ids = df.at[idx, "campaign_ids"]

    if isinstance(campaign_ids, (list, tuple)):
        if len(campaign_ids) > 0:
            if _add_error(df, idx):
                df.at[idx, "has_control_campaign"] = True
                df.at[idx, "campaign_ids"] = []

    elif campaign_ids is not None:
        if _add_error(df, idx):
            df.at[idx, "has_control_campaign"] = True
            df.at[idx, "campaign_ids"] = []


def campaign_ids_without_indicator(df, idx):

    campaign_ids = df.at[idx, "campaign_ids"]

    if not isinstance(campaign_ids, (list, tuple)):
        return

    if not campaign_ids:
        return

    if _add_error(df, idx):
        df.at[idx, "has_treatment_campaign"] = False
        df.at[idx, "has_control_campaign"] = False


def treatment_and_control_campaign_both_true(df, idx):

    treatment = df.at[idx, "has_treatment_campaign"]
    control = df.at[idx, "has_control_campaign"]

    if treatment is True and control is True:
        return

    if _add_error(df, idx):
        df.at[idx, "has_treatment_campaign"] = True
        df.at[idx, "has_control_campaign"] = True


def duplicate_campaign_within_clickstream(df, idx):

    campaign_ids = df.at[idx, "campaign_ids"]

    if not isinstance(campaign_ids, (list, tuple)):
        return

    if not campaign_ids:
        return

    if _add_error(df, idx):
        corrupted_ids = list(campaign_ids)
        corrupted_ids.append(random.choice(corrupted_ids))

        df.at[idx, "campaign_ids"] = corrupted_ids


# =============================================================================
# Promotion Logic
# =============================================================================


def promotion_ids_without_bundle_for_bundle_reference(
    df,
    idx,
):
    """
    Bundle references require a promotion associated with the bundle.

    The actual relationship is validated against the promotion master
    in the relationship rule below.
    """

    bundle_ids = df.at[idx, "bundle_ids"]

    if not isinstance(bundle_ids, (list, tuple)):
        return

    if not bundle_ids:
        return

    promotion_ids = df.at[idx, "promotion_ids"]

    if isinstance(promotion_ids, (list, tuple)):
        if not promotion_ids:
            return

    if _add_error(df, idx):
        df.at[idx, "promotion_ids"] = []


def duplicate_promotion_within_clickstream(df, idx):

    promotion_ids = df.at[idx, "promotion_ids"]

    if not isinstance(promotion_ids, (list, tuple)):
        return

    if not promotion_ids:
        return

    if _add_error(df, idx):
        corrupted_ids = list(promotion_ids)
        corrupted_ids.append(random.choice(corrupted_ids))

        df.at[idx, "promotion_ids"] = corrupted_ids


def duplicate_bundle_within_clickstream(df, idx):

    bundle_ids = df.at[idx, "bundle_ids"]

    if not isinstance(bundle_ids, (list, tuple)):
        return

    if not bundle_ids:
        return

    if _add_error(df, idx):
        corrupted_ids = list(bundle_ids)
        corrupted_ids.append(random.choice(corrupted_ids))

        df.at[idx, "bundle_ids"] = corrupted_ids


# =============================================================================
# Promotion / Bundle Relationship
# =============================================================================


def bundle_does_not_belong_to_promotion(df, idx, ctx):

    bundle_ids = df.at[idx, "bundle_ids"]
    promotion_ids = df.at[idx, "promotion_ids"]

    if not isinstance(bundle_ids, (list, tuple)):
        return

    if not bundle_ids:
        return

    if not isinstance(promotion_ids, (list, tuple)):
        return

    if not promotion_ids:
        return

    promotions_df = ctx.promotions.promotions_df

    required_columns = {
        "promotion_id",
        "promotion_scope",
        "promotion_target_id",
    }

    if not required_columns.issubset(promotions_df.columns):
        return

    valid_bundle_promotions = promotions_df[
        promotions_df["promotion_scope"].astype(str).str.lower() == "bundle"
    ]

    if valid_bundle_promotions.empty:
        return

    valid_pairs = set(
        zip(
            valid_bundle_promotions["promotion_id"],
            valid_bundle_promotions["promotion_target_id"],
        )
    )

    invalid_bundles = [
        bundle_id
        for bundle_id in bundle_ids
        if not any(
            (promotion_id, bundle_id) in valid_pairs for promotion_id in promotion_ids
        )
    ]

    if not invalid_bundles:
        return

    if _add_error(df, idx):
        corrupted_ids = list(bundle_ids)

        corrupted_ids[random.randrange(len(corrupted_ids))] = random.choice(
            invalid_bundles
        )

        df.at[idx, "bundle_ids"] = corrupted_ids


def product_promotion_target_mismatch(df, idx, ctx):

    if df.at[idx, "event_type"] != "Product View":
        return

    product_id = df.at[idx, "product_id"]
    promotion_ids = df.at[idx, "promotion_ids"]

    if _is_missing(product_id):
        return

    if not isinstance(promotion_ids, (list, tuple)):
        return

    if not promotion_ids:
        return

    promotions_df = ctx.promotions.promotions_df

    required_columns = {
        "promotion_id",
        "promotion_scope",
        "promotion_target_id",
    }

    if not required_columns.issubset(promotions_df.columns):
        return

    promotion_rows = promotions_df[
        promotions_df["promotion_id"].isin(promotion_ids)
        & (promotions_df["promotion_scope"].astype(str).str.lower() == "product")
    ]

    if promotion_rows.empty:
        return

    target = promotion_rows.iloc[0]["promotion_target_id"]

    product_ids = ctx.products.products_df["product_id"].dropna().tolist()

    alternatives = [pid for pid in product_ids if pid != target]

    if not alternatives:
        return

    if _add_error(df, idx):
        df.at[idx, "product_id"] = random.choice(alternatives)


def category_promotion_target_mismatch(df, idx, ctx):

    if df.at[idx, "event_type"] != "Product View":
        return

    promotion_ids = df.at[idx, "promotion_ids"]

    if not isinstance(promotion_ids, (list, tuple)):
        return

    if not promotion_ids:
        return

    promotions_df = ctx.promotions.promotions_df

    required_columns = {
        "promotion_id",
        "promotion_scope",
        "promotion_target_id",
    }

    if not required_columns.issubset(promotions_df.columns):
        return

    promotion_rows = promotions_df[
        promotions_df["promotion_id"].isin(promotion_ids)
        & (promotions_df["promotion_scope"].astype(str).str.lower() == "category")
    ]

    if promotion_rows.empty:
        return

    target_category = promotion_rows.iloc[0]["promotion_target_id"]

    alternatives = [category for category in CATEGORIES if category != target_category]

    if not alternatives:
        return

    if _add_error(df, idx):
        df.at[idx, "category"] = random.choice(alternatives)


# =============================================================================
# Event Content Rules
# =============================================================================


PRODUCT_EVENTS = {
    "Product View",
    "Add to Cart",
    "Remove from Cart",
}

NON_PRODUCT_EVENTS = {
    "Home View",
    "Category View",
    "Search View",
    "Cart View",
    "Checkout Start",
    "Payment Attempt",
    "Payment Successful",
    "Payment Failed",
}

CATEGORY_EVENTS = {
    "Product View",
    "Add to Cart",
    "Remove from Cart",
    "Category View",
}

SCROLL_EVENTS = {
    "Home View",
    "Search View",
    "Category View",
    "Product View",
}


def product_event_missing_product_id(df, idx):

    if df.at[idx, "event_type"] not in PRODUCT_EVENTS:
        return

    if _add_error(df, idx):
        df.at[idx, "product_id"] = None


def non_product_event_has_product_id(df, idx, ctx):

    if df.at[idx, "event_type"] not in NON_PRODUCT_EVENTS:
        return

    product_ids = ctx.products.products_df["product_id"].dropna().tolist()

    if not product_ids:
        return

    if _add_error(df, idx):
        df.at[idx, "product_id"] = random.choice(product_ids)


def product_event_missing_product_name(df, idx):

    if df.at[idx, "event_type"] not in PRODUCT_EVENTS:
        return

    if _add_error(df, idx):
        df.at[idx, "product_name"] = None


def non_product_event_has_product_name(df, idx, ctx):

    if df.at[idx, "event_type"] not in NON_PRODUCT_EVENTS:
        return

    products_df = ctx.products.products_df

    if "product_name" not in products_df.columns:
        return

    valid_names = products_df["product_name"].dropna().tolist()

    if not valid_names:
        return

    if _add_error(df, idx):
        df.at[idx, "product_name"] = random.choice(valid_names)


def category_event_missing_category(df, idx):

    if df.at[idx, "event_type"] not in CATEGORY_EVENTS:
        return

    if _add_error(df, idx):
        df.at[idx, "category"] = None


def non_category_event_has_category(df, idx):

    if df.at[idx, "event_type"] in CATEGORY_EVENTS:
        return

    if not CATEGORIES:
        return

    if _add_error(df, idx):
        df.at[idx, "category"] = random.choice(CATEGORIES)


def scroll_event_missing_scroll_depth(df, idx):

    if df.at[idx, "event_type"] not in SCROLL_EVENTS:
        return

    if _add_error(df, idx):
        df.at[idx, "scroll_depth"] = None


def non_scroll_event_has_scroll_depth(df, idx):

    if df.at[idx, "event_type"] in SCROLL_EVENTS:
        return

    if _add_error(df, idx):
        df.at[idx, "scroll_depth"] = random.uniform(
            0,
            100,
        )


# =============================================================================
# Page / Event-Type Consistency
# =============================================================================


def _format_event_page(df, idx, event_type):

    template = EVENT_PAGE_MAPPING.get(event_type)

    if not template:
        return None

    values = {
        "category": df.at[idx, "category"],
        "product_id": df.at[idx, "product_id"],
        "search_term": fake.word(),
    }

    try:
        return template.format(**values)
    except (KeyError, ValueError):
        return None


def invalid_event_page(df, idx):

    event_type = df.at[idx, "event_type"]

    if event_type not in EVENT_PAGE_MAPPING:
        return

    other_event_types = [event for event in EVENT_PAGE_MAPPING if event != event_type]

    if not other_event_types:
        return

    invalid_event_type = random.choice(other_event_types)

    invalid_page = _format_event_page(
        df,
        idx,
        invalid_event_type,
    )

    if invalid_page and _add_error(df, idx):
        df.at[idx, "page"] = invalid_page


# =============================================================================
# Stock Status
# =============================================================================


def product_view_missing_stock_status(df, idx):

    if df.at[idx, "event_type"] != "Product View":
        return

    if _add_error(df, idx):
        df.at[idx, "stock_status"] = None


def non_product_view_has_stock_status(df, idx):

    if df.at[idx, "event_type"] == "Product View":
        return

    valid_statuses = list(STOCK_STATUSES.values())

    if not valid_statuses:
        return

    if _add_error(df, idx):
        df.at[idx, "stock_status"] = random.choice(valid_statuses)


# =============================================================================
# Promotion / Bundle Event Scope
# =============================================================================


def promotion_on_non_product_event(df, idx, ctx):

    if df.at[idx, "event_type"] in PRODUCT_EVENTS:
        return

    promotions_df = ctx.promotions.promotions_df

    if "promotion_id" not in promotions_df.columns:
        return

    valid_ids = promotions_df["promotion_id"].dropna().tolist()

    if not valid_ids:
        return

    if _add_error(df, idx):
        df.at[idx, "promotion_ids"] = [random.choice(valid_ids)]


def bundle_on_non_product_event(df, idx, ctx):

    if df.at[idx, "event_type"] in PRODUCT_EVENTS:
        return

    bundles_df = ctx.bundles.bundles_df

    if "bundle_id" not in bundles_df.columns:
        return

    valid_ids = bundles_df["bundle_id"].dropna().tolist()

    if not valid_ids:
        return

    if _add_error(df, idx):
        df.at[idx, "bundle_ids"] = [random.choice(valid_ids)]


# =============================================================================
# Purchased Items
# =============================================================================


def missing_purchased_items_on_payment_successful(df, idx):

    if df.at[idx, "event_type"] != "Payment Successful":
        return

    if _add_error(df, idx):
        df.at[idx, "purchased_items"] = []


def purchased_items_on_payment_failed(df, idx, ctx):

    if df.at[idx, "event_type"] != "Payment Failed":
        return

    products_df = ctx.products.products_df

    product_ids = products_df["product_id"].dropna().tolist()

    if not product_ids:
        return

    if _add_error(df, idx):
        df.at[idx, "purchased_items"] = [random.choice(product_ids)]


# =============================================================================
# Cart Content / Cart Size
# =============================================================================


def cart_size_does_not_match_cart_content(df, idx):

    cart_content = df.at[idx, "cart_content"]

    if isinstance(cart_content, (list, tuple)):
        actual_size = len(cart_content)
    else:
        actual_size = 0

    possible_sizes = [
        actual_size - 2,
        actual_size - 1,
        actual_size + 1,
        actual_size + 2,
    ]

    possible_sizes = [size for size in possible_sizes if size >= 0]

    if not possible_sizes:
        possible_sizes = [actual_size + 1]

    if _add_error(df, idx):
        df.at[idx, "cart_size"] = random.choice(possible_sizes)

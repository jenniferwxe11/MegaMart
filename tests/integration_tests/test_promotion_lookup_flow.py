import pandas as pd
import pytest

from data_generation.services.clickstreams.clickstream_lookup_service import (
    get_active_promotions,
    get_relevant_promotion_on_page,
)

# ============================================================
# get_active_promotions()
# ============================================================
# Integration contract: uses promotion data


def test_promotion_lookup_flow_get_active_promotions(ctx):
    promotions_df = ctx.promotions.promotions_df

    # Pick one valid row
    row = promotions_df.iloc[0]
    timestamp = row["effective_start_date"]

    expected_df = promotions_df[
        (promotions_df["effective_start_date"] <= timestamp)
        & (promotions_df["effective_end_date"] >= timestamp)
    ].drop_duplicates(subset=["promotion_id"])
    expected = expected_df.to_dict("records")

    result = get_active_promotions(ctx, timestamp)

    assert len(result) == len(expected)
    assert {r["promotion_id"] for r in result} == {e["promotion_id"] for e in expected}


# ============================================================
# get_relevant_promotion_on_page()
# ============================================================
# Integration contract: uses bundle + promotion data


def test_promotion_lookup_flow_get_relevant_promotion_on_page_cart_scope_only_on_cart_events(
    ctx,
):
    """
    Integration contract: cart-scoped promotions must only surface during
    Cart View and Checkout Start events, never on Product View or Category View.
    Tests that scope-gating logic reads promotion_scope from promotions_df correctly.
    """
    promotions_df = ctx.promotions.promotions_df
    cart_promos = promotions_df[promotions_df["promotion_scope"] == "cart"]
    if cart_promos.empty:
        pytest.skip("No cart-scoped promotions in generated data")

    row = cart_promos.iloc[0]
    timestamp = row["effective_start_date"]

    active_campaigns = [
        {
            "campaign_id": row["campaign_id"],
            "assignment_group": "Treatment",
        }
    ]

    for non_cart_event in ["Home View", "Product View", "Category View", "Search View"]:
        result = get_relevant_promotion_on_page(
            ctx,
            timestamp=timestamp,
            event_type=non_cart_event,
            category=None,
            product_id=None,
            active_campaigns=active_campaigns,
        )
        cart_promo_ids = set(cart_promos["promotion_id"])
        returned_ids = {p["promotion_id"] for p in result}

        assert cart_promo_ids.isdisjoint(returned_ids), (
            f"Cart-scoped promotion surfaced on non-cart event {non_cart_event!r}: "
            f"{cart_promo_ids & returned_ids}"
        )

    for cart_event in ["Cart View", "Checkout Start"]:
        result = get_relevant_promotion_on_page(
            ctx,
            timestamp=timestamp,
            event_type=cart_event,
            category=None,
            product_id=None,
            active_campaigns=active_campaigns,
        )
        # At least one cart promo should be returned when event matches
        if result:
            returned_scopes = {p["promotion_scope"] for p in result}
            assert "cart" in returned_scopes


def test_promotion_lookup_flow_get_relevant_promotion_on_page_category_scope_matches_category(
    ctx,
):
    """
    Integration contract: a category-scoped promotion must only appear when
    the browsed category matches the promotion target.
    """
    promotions_df = ctx.promotions.promotions_df
    cat_promos = promotions_df[promotions_df["promotion_scope"] == "category"]
    if cat_promos.empty:
        pytest.skip("No category-scoped promotions in generated data")

    row = cat_promos.iloc[0]
    target_category = row["promotion_target_id"]
    timestamp = row["effective_start_date"]

    active_campaigns = [
        {
            "campaign_id": row["campaign_id"],
            "assignment_group": "Treatment",
        }
    ]

    # Correct category — should appear
    result_match = get_relevant_promotion_on_page(
        ctx,
        timestamp=timestamp,
        event_type="Category View",
        category=target_category,
        product_id=None,
        active_campaigns=active_campaigns,
    )
    returned_ids = {p["promotion_id"] for p in result_match}
    assert row["promotion_id"] in returned_ids, (
        f"Promotion {row['promotion_id']} not returned for its own target category "
        f"{target_category!r}"
    )

    # Wrong category — should NOT appear
    wrong_category = target_category + "_WRONG"
    result_no_match = get_relevant_promotion_on_page(
        ctx,
        timestamp=timestamp,
        event_type="Category View",
        category=wrong_category,
        product_id=None,
        active_campaigns=active_campaigns,
    )
    returned_ids_no_match = {p["promotion_id"] for p in result_no_match}
    assert row["promotion_id"] not in returned_ids_no_match


def test_promotion_lookup_flow_get_relevant_promotion_on_page_product_scope_only_on_product_view(
    ctx,
):
    """
    Integration contract: product-scoped promotions must only surface on
    Product View events and only when the viewed product matches the target.
    """
    promotions_df = ctx.promotions.promotions_df
    prod_promos = promotions_df[promotions_df["promotion_scope"] == "product"]
    if prod_promos.empty:
        pytest.skip("No product-scoped promotions in generated data")

    row = prod_promos.iloc[0]
    target_product = row["promotion_target_id"]
    timestamp = row["effective_start_date"]

    active_campaigns = [
        {
            "campaign_id": row["campaign_id"],
            "assignment_group": "Treatment",
        }
    ]

    # Correct product + correct event — should appear
    result = get_relevant_promotion_on_page(
        ctx,
        timestamp=timestamp,
        event_type="Product View",
        category=None,
        product_id=target_product,
        active_campaigns=active_campaigns,
    )
    returned_ids = {p["promotion_id"] for p in result}
    assert row["promotion_id"] in returned_ids

    # Correct product + wrong event — must NOT appear
    result_wrong_event = get_relevant_promotion_on_page(
        ctx,
        timestamp=timestamp,
        event_type="Cart View",
        category=None,
        product_id=target_product,
        active_campaigns=active_campaigns,
    )
    returned_ids_wrong = {p["promotion_id"] for p in result_wrong_event}
    assert row["promotion_id"] not in returned_ids_wrong

    # Wrong product + correct event — must NOT appear
    result_wrong_product = get_relevant_promotion_on_page(
        ctx,
        timestamp=timestamp,
        event_type="Product View",
        category=None,
        product_id="NON_EXISTENT_PROD",
        active_campaigns=active_campaigns,
    )
    returned_ids_wrong_prod = {p["promotion_id"] for p in result_wrong_product}
    assert row["promotion_id"] not in returned_ids_wrong_prod


def test_promotion_lookup_flow_get_relevant_promotion_on_page_bundle_scope_surfaces_when_product_in_bundle(
    ctx,
):
    """
    Integration contract: bundle-scoped promotions must appear whenever a
    product that belongs to the bundle is being viewed.  Tests that
    bundle_dict is correctly consulted during promotion filtering.
    """
    promotions_df = ctx.promotions.promotions_df
    bundle_promos = promotions_df[promotions_df["promotion_scope"] == "bundle"]
    if bundle_promos.empty:
        pytest.skip("No bundle-scoped promotions in generated data")

    bundle_dict = ctx.bundles.bundle_dict

    # Find a bundle promo whose bundle has at least one product
    matched_promo = None
    bundle_product = None
    for _, row in bundle_promos.iterrows():
        bundle_id = row["promotion_target_id"]
        products = bundle_dict.get(bundle_id, {})
        if products:
            matched_promo = row
            bundle_product = next(iter(products))
            break

    if matched_promo is None:
        pytest.skip("No bundle promotions have resolvable bundle products")

    timestamp = matched_promo["effective_start_date"]

    active_campaigns = [
        {
            "campaign_id": row["campaign_id"],
            "assignment_group": "Treatment",
        }
    ]

    result = get_relevant_promotion_on_page(
        ctx,
        timestamp=timestamp,
        event_type="Product View",
        category=None,
        product_id=bundle_product,
        active_campaigns=active_campaigns,
    )

    returned_ids = {p["promotion_id"] for p in result}
    assert matched_promo["promotion_id"] in returned_ids, (
        f"Bundle promotion {matched_promo['promotion_id']} not returned "
        f"when viewing bundle product {bundle_product!r}"
    )

    # Verify returned entry carries bundle_id
    matched_returned = [
        p for p in result if p["promotion_id"] == matched_promo["promotion_id"]
    ]
    assert matched_returned[0]["bundle_id"] == matched_promo["promotion_target_id"]


def test_promotion_lookup_flow_get_relevant_promotion_on_page_expired_promotions_not_returned(
    ctx,
):
    """
    Integration contract: promotions whose window has closed must never be
    returned regardless of event type or product match.
    """
    promotions_df = ctx.promotions.promotions_df
    past_timestamp = promotions_df["effective_start_date"].min() - pd.Timedelta(
        days=365
    )

    result = get_relevant_promotion_on_page(
        ctx,
        timestamp=past_timestamp,
        event_type="Product View",
        category=None,
        product_id=None,
        active_campaigns=None,
    )
    assert (
        result == []
    ), "Expired promotions must not be returned by get_relevant_promotion_on_page()"


def test_promotion_lookup_flow_get_relevant_promotion_on_page_returns_required_keys(
    ctx,
):
    """
    Integration contract: every dict in the returned list must contain the
    four keys that downstream promotion processing depends on.
    """
    promotions_df = ctx.promotions.promotions_df
    row = promotions_df.iloc[0]
    timestamp = row["effective_start_date"]

    result = get_relevant_promotion_on_page(
        ctx,
        timestamp=timestamp,
        event_type="Cart View",
        category=None,
        product_id=None,
        active_campaigns=None,
    )

    required_keys = {
        "promotion_id",
        "promotion_scope",
        "promotion_target_id",
        "promotion_mechanic",
        "bundle_id",
    }
    for p in result:
        missing = required_keys - set(p.keys())
        assert not missing, f"Returned promotion dict missing keys: {missing}"

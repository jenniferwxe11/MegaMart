import copy
import random

import pandas as pd
import pytest
from faker import Faker

from data_generation.config.clickstreams_config import (
    VALID_EVENT_TRANSITIONS,
)
from data_generation.services.clickstreams.clickstream_event_service import (
    resolve_add_to_cart,
    resolve_category_view,
    resolve_page,
    resolve_payment_successful,
    resolve_product_view,
    resolve_remove_from_cart,
)
from data_generation.services.clickstreams.clickstream_lookup_service import (
    get_relevant_promotion_on_page,
    slugify,
)
from data_generation.services.clickstreams.clickstream_promotion_service import (
    process_promotion_exposure,
)
from data_generation.services.clickstreams.clickstream_transition_service import (
    apply_promotion_uplift,
)
from tests.helpers import _build_datetime

fake = Faker()
fake.seed_instance(42)


def test_clickstream_pipeline_flow_promotion_exposure_drives_followup_actions(
    ctx, seed: int = 42
):
    """
    Integration contract:

    A product promotion on a page must be discoverable,tracked as seen,
    and if engaged, drive Add to Cart uplift and inject
    a pending Add to Cart event.
    """
    rng = random.Random(seed)
    promotions_df = ctx.promotions.promotions_df
    product_promotions = promotions_df[promotions_df["promotion_scope"] == "product"]

    if product_promotions.empty:
        pytest.skip("No product promotions found")

    promo = product_promotions.iloc[rng.randrange(len(product_promotions))]
    timestamp = fake.date_time_between(
        start_date=pd.Timestamp(promo["effective_start_date"]),
        end_date=pd.Timestamp(promo["effective_end_date"]),
    )
    product_id = promo["promotion_target_id"]
    category = ctx.products.product_category_map[product_id]

    # Build active_campaigns context based on whether this promo is campaign-linked
    campaign_id = promo.get("campaign_id")
    if pd.notna(campaign_id):
        campaigns_df = ctx.campaigns.campaigns_df
        campaign_row = campaigns_df[campaigns_df["campaign_id"] == campaign_id]
        if campaign_row.empty:
            pytest.skip("Campaign not found for promo")

        # Synthesise a minimal assignment row: one Treatment customer
        active_campaigns = campaign_row.copy()
        active_campaigns["assignment_group"] = "Treatment"
    else:
        active_campaigns = None

    # --- TIER 1: Promotion must be discoverable ---
    promotions = get_relevant_promotion_on_page(
        ctx,
        timestamp,
        "Product View",
        category=category,
        product_id=product_id,
        active_campaigns=active_campaigns,
    )

    assert any(
        p["promotion_id"] == promo["promotion_id"] for p in promotions
    ), f"{promo['promotion_id']} not visible on Product View for {product_id} at {timestamp}"

    # --- TIER 2: Seen tracking always updates ---
    selected_promotions: list[dict] = []
    seen_promotions: dict[str, int] = {}
    seen_promo_types: dict[str, int] = {}
    pending_events: list[dict] = []

    process_promotion_exposure(
        ctx,
        promotions,
        "Product View",
        product_id,
        seen_promotions,
        seen_promo_types,
        selected_promotions,
        pending_events,
    )

    assert (
        seen_promotions.get(promo["promotion_id"]) == 1
    ), "Seen count should be 1 after first exposure"
    assert promo["promotion_mechanic"] in seen_promo_types, "Mechanic type not tracked"

    # --- TIER 3: Engagement outcome ---
    if selected_promotions:
        # Capture ATC before and after on identical isolated matrices
        tp_base = copy.deepcopy(VALID_EVENT_TRANSITIONS)
        tp_uplifted = copy.deepcopy(VALID_EVENT_TRANSITIONS)

        # Apply uplift only to uplifted copy
        apply_promotion_uplift(
            tp_uplifted,
            selected_promotions,
            seen_promotions,
            seen_promo_types,
            progress=0.5,
        )

        # ATC raw value in uplifted matrix should exceed or equal base
        # (normalisation can shift absolute values, so compare the ratio ATC/total)

        total_uplifted = sum(tp_uplifted["Product View"].values())
        atc_uplifted: float = (
            tp_uplifted["Product View"]["Add to Cart"] / total_uplifted
            if total_uplifted > 0
            else 0.0
        )

        total_base = sum(tp_base["Product View"].values())
        atc_base: float = (
            tp_base["Product View"]["Add to Cart"] / total_base
            if total_base > 0
            else 0.0
        )

        assert (
            atc_uplifted >= atc_base
        ), "Engaged promotion should increase Add to Cart share of Product View transitions"

        selected_product_promo = any(
            p["promotion_id"] == promo["promotion_id"] for p in selected_promotions
        )

        if selected_product_promo:
            assert any(
                e["type"] == "Add to Cart" and e.get("product_id") == product_id
                for e in pending_events
            ), f"Product promotion should inject Add to Cart for {product_id} into pending_events"

    else:
        # No engagement: matrix must be untouched
        tp_base = copy.deepcopy(VALID_EVENT_TRANSITIONS)
        tp_result = copy.deepcopy(VALID_EVENT_TRANSITIONS)
        apply_promotion_uplift(
            tp_result,
            [],
            seen_promotions,
            seen_promo_types,
            progress=0.5,
        )
        assert (
            tp_result["Product View"]["Add to Cart"]
            == tp_base["Product View"]["Add to Cart"]
        ), "No engagement — transition matrix should be unchanged"
        assert pending_events == [], "No engagement — pending_events should be empty"


def test_clickstream_pipeline_flow_product_discovery_to_purchase_journey(
    ctx, seed: int = 42
):
    """
    Integration contract:

    A customer should be able to progress through a realistic
    discovery → cart → purchase journey while maintaining
    consistent state across clickstream services.

    Flow tested:

        Category View
            -> Product View
            -> Add to Cart
            -> Product View
            -> Add to Cart
            -> Remove from Cart
            -> Payment Successful

    Validates:

    - Category selection feeds product selection
    - Product View returns a valid product/category
    - Add to Cart updates cart state correctly
    - Remove from Cart updates cart state correctly
    - Page generation is consistent with event context
    - Payment Successful removes purchased items from cart
    - Cart accounting reconciles exactly
    """
    rng = random.Random(seed)

    customer_segment = "Regular Customers"
    store_id = ctx.stores.online_store_id
    timestamp = _build_datetime()

    # Build a realistic session affinity cluster
    categories = list(set(ctx.products.product_category_map.values()))
    session_affinity_categories = set(rng.sample(categories, min(3, len(categories))))

    cart_content: list[str] = []

    # ============================================================
    # Step 1: Category View
    # ============================================================

    category = resolve_category_view(
        previous_category=None,
        customer_segment=customer_segment,
        session_affinity_categories=session_affinity_categories,
    )

    assert category is not None

    category_page = resolve_page(
        event_type="Category View",
        product_id=None,
        category=category,
        search_term=None,
    )

    assert category_page
    assert slugify(category) in category_page

    # ============================================================
    # Step 2: Product View
    # ============================================================

    (
        product_id_1,
        category_1,
        product_name_1,
        stock_status_1,
    ) = resolve_product_view(
        ctx,
        product_id=None,
        previous_event_type="Category View",
        previous_category=category,
        previous_product_id=None,
        previous_search_term=None,
        cart_content=cart_content,
        customer_segment=customer_segment,
        session_affinity_categories=session_affinity_categories,
        store_id=store_id,
        timestamp=timestamp,
    )

    assert product_id_1 is not None
    assert category_1 is not None
    assert product_name_1 is not None

    product_page_1 = resolve_page(
        event_type="Product View",
        product_id=product_id_1,
        category=category_1,
        search_term=None,
    )

    assert product_page_1
    assert str(product_id_1) in product_page_1

    # ============================================================
    # Step 3: Add To Cart
    # ============================================================

    (
        added_product_1,
        added_category_1,
        _,
        cart_content,
    ) = resolve_add_to_cart(
        ctx,
        product_id_1,
        product_id_1,
        category_1,
        cart_content,
        store_id,
        timestamp,
    )

    assert added_product_1 == product_id_1
    assert added_category_1 == category_1
    assert len(cart_content) == 1
    assert product_id_1 in cart_content

    # ============================================================
    # Step 4: Product View Again
    # ============================================================

    (
        product_id_2,
        category_2,
        product_name_2,
        stock_status_2,
    ) = resolve_product_view(
        ctx,
        product_id=None,
        previous_event_type="Add to Cart",
        previous_category=category_1,
        previous_product_id=product_id_1,
        previous_search_term=None,
        cart_content=cart_content,
        customer_segment=customer_segment,
        session_affinity_categories=session_affinity_categories,
        store_id=store_id,
        timestamp=timestamp,
    )

    assert product_id_2 is not None
    assert category_2 is not None
    assert product_name_2 is not None

    product_page_2 = resolve_page(
        event_type="Product View",
        product_id=product_id_2,
        category=category_2,
        search_term=None,
    )

    assert product_page_2
    assert str(product_id_2) in product_page_2

    # ============================================================
    # Step 5: Add Second Item
    # ============================================================

    (
        added_product_2,
        added_category_2,
        _,
        cart_content,
    ) = resolve_add_to_cart(
        ctx,
        product_id_2,
        product_id_2,
        category_2,
        cart_content,
        store_id,
        timestamp,
    )

    assert added_product_2 == product_id_2
    assert added_category_2 == category_2

    initial_cart = cart_content.copy()

    assert len(initial_cart) == 2

    # ============================================================
    # Step 6: Remove One Item
    # ============================================================
    cart_before = cart_content.copy()

    removed_product, _, _, cart_content = resolve_remove_from_cart(
        ctx,
        cart_content,
    )

    assert cart_content.count(removed_product) == cart_before.count(removed_product) - 1
    assert len(cart_content) == len(cart_before) - 1

    initial_cart = cart_content.copy()

    # ============================================================
    # Step 7: Purchase
    # ============================================================

    purchased_items, remaining_cart = resolve_payment_successful(
        ctx,
        cart_content,
        selected_promotions=[],
        mission_choice="Purchase",
        has_treatment=False,
        customer_segment=customer_segment,
    )

    # ============================================================
    # Reconciliation Checks
    # ============================================================

    assert len(purchased_items) >= 1

    assert len(initial_cart) == len(purchased_items) + len(remaining_cart)

    # Purchased items must come from original cart
    for pid in purchased_items:
        assert pid in initial_cart

    # Remaining items must come from original cart
    for pid in remaining_cart:
        assert pid in initial_cart

    # Verify exact multiset reconciliation
    original_counter: dict[str, int] = {}
    for pid in initial_cart:
        original_counter[pid] = original_counter.get(pid, 0) + 1

    final_counter: dict[str, int] = {}
    for pid in purchased_items:
        final_counter[pid] = final_counter.get(pid, 0) + 1

    for pid in remaining_cart:
        final_counter[pid] = final_counter.get(pid, 0) + 1

    assert original_counter == final_counter, (
        f"Cart reconciliation failed. "
        f"Original={original_counter}, "
        f"Purchased={purchased_items}, "
        f"Remaining={remaining_cart}"
    )

    # Purchased items should not remain in cart more times than allowed
    purchased_counter: dict[str, int] = {}
    for pid in purchased_items:
        purchased_counter[pid] = purchased_counter.get(pid, 0) + 1

    remaining_counter: dict[str, int] = {}
    for pid in remaining_cart:
        remaining_counter[pid] = remaining_counter.get(pid, 0) + 1

    for pid, purchased_qty in purchased_counter.items():
        assert remaining_counter.get(pid, 0) <= original_counter[pid] - purchased_qty

    # Stock statuses returned by Product View should always be populated
    assert stock_status_1 is not None
    assert stock_status_2 is not None

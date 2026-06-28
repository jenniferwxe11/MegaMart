import random

from data_generation.config.bundles_config import BUNDLE_DEFINITIONS
from data_generation.services.bundles.bundle_pricing_service import (
    calculate_bundle_pricing,
    phase_prices,
    split_window,
)
from data_generation.services.bundles.bundle_selection_service import (
    select_products_for_bundle,
)
from tests.helpers import (
    _build_bundle_lifecycle,
    _build_bundle_pricing_inputs,
    _build_bundle_products_dict,
    _build_category,
)

# ============================================================
# calculate_bundle_pricing()
# ============================================================
# UNIT: selected_products is a plain list of (pid, qty) tuples.
# product_price_map and product_cost_map are the only ctx reads,
# which we satisfy by passing ctx (lightweight fixture).


def test_bundle_functions_calculate_bundle_pricing_price_covers_cost(ctx):
    for bundle_type in BUNDLE_DEFINITIONS:
        selected_products = _build_bundle_products_dict(ctx)

        total_cost = round(
            sum(
                ctx.products.product_cost_map[pid] * qty
                for pid, qty in selected_products
            ),
            2,
        )

        bundle_price, discount_value = calculate_bundle_pricing(
            ctx,
            bundle_type,
            selected_products,
        )

        assert bundle_price >= total_cost
        assert discount_value <= bundle_price


# ============================================================
# split_window()
# ============================================================


def test_bundle_functions_split_window_non_overlapping():
    scenario = _build_bundle_lifecycle()
    phases = split_window(scenario["start"], scenario["end"])
    for i in range(len(phases) - 1):
        assert phases[i][1] < phases[i + 1][0]


def test_bundle_functions_split_window_phases_covers_full_window():
    scenario = _build_bundle_lifecycle()
    phases = split_window(scenario["start"], scenario["end"])
    assert phases[0][0] == scenario["start"]
    assert phases[-1][1] == scenario["end"]


def test_bundle_functions_split_window_launch_always_first():
    scenario = _build_bundle_lifecycle()
    phases = split_window(scenario["start"], scenario["end"])
    assert phases[0][2] == "LAUNCH"


# ============================================================
# phase_prices()
# ============================================================


def test_bundle_functions_phase_prices_never_increase_across_phases():
    """
    LAUNCH >= PROMO >= EOL
    """
    scenario = _build_bundle_pricing_inputs()
    results = phase_prices(
        scenario["base_price"],
        scenario["base_discount"],
        scenario["phases"],
    )
    prices = [r[0] for r in results]
    assert all(prices[i] >= prices[i + 1] for i in range(len(prices) - 1))


def test_bundle_functions_phase_prices_discounts_never_decrease_across_phases():
    scenario = _build_bundle_pricing_inputs()
    results = phase_prices(
        scenario["base_price"],
        scenario["base_discount"],
        scenario["phases"],
    )
    discounts = [r[1] for r in results]
    assert all(discounts[i] <= discounts[i + 1] for i in range(len(discounts) - 1))


def test_bundle_functions_phase_prices_discount_less_than_phase_price():
    scenario = _build_bundle_pricing_inputs()
    results = phase_prices(
        scenario["base_price"],
        scenario["base_discount"],
        scenario["phases"],
    )
    for price, discount in results:
        assert discount < price


# ============================================================
# select_products_for_bundle()
# ============================================================
# UNIT: the only ctx usage is products_df, which is available from
# the lightweight ctx fixture. We are testing the selection
# logic in isolation — not how lifecycle or pricing interacts with it.


def test_bundle_functions_select_products_for_set_bundle(ctx, seed: int = 42):
    rng = random.Random(seed)
    n = 2

    category1, category2 = _build_category(ctx, n)
    buy_quantity = rng.randint(1, 3)

    selected_products, selected_categories = select_products_for_bundle(
        ctx,
        "Set",
        [category1, category2],
        buy_quantity,
    )

    assert selected_categories[0] in [category1, category2]
    assert len(selected_products) == n
    for pid, qty in selected_products:
        assert (
            pid in ctx.products.category_to_products[category1]
            or pid in ctx.products.category_to_products[category2]
        )
        assert qty > 0


def test_bundle_functions_select_products_for_non_set_bundle(ctx, seed: int = 42):
    rng = random.Random(seed)
    n = 1

    for bundle_type in BUNDLE_DEFINITIONS:
        if bundle_type == "Set":
            continue

        (category,) = _build_category(ctx, n)
        buy_quantity = rng.randint(1, 3)

        selected_products, selected_categories = select_products_for_bundle(
            ctx,
            bundle_type,
            [category],
            buy_quantity,
        )

        assert selected_categories == [category]
        assert len(selected_products) == n
        for pid, qty in selected_products:
            assert pid in ctx.products.category_to_products[category]
            assert qty > 0

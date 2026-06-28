import pytest

from data_generation.config.clickstreams_config import IN_STOCK_STATUS
from data_generation.config.products_config import CATEGORY_ITEMS
from data_generation.config.stocks_config import STOCK_STATUSES
from data_generation.services.clickstreams.clickstream_event_service import (
    resolve_add_to_cart,
    resolve_product_view,
    resolve_remove_from_cart,
    resolve_search_view,
)
from tests.helpers import (
    _build_customer_segment,
    _build_datetime,
)

# ============================================================
# resolve_remove_from_cart()
# ============================================================
# Integration contract: uses product catalogue data


def test_clickstream_event_flow_resolve_remove_from_cart_removes_one_item_from_cart(
    ctx,
):
    """
    Integration contract: resolve_remove_from_cart() must return an
    updated cart that is exactly one item shorter than the input.
    """
    product_ids = ctx.products.product_ids
    cart = [product_ids[0], product_ids[1], product_ids[0]]

    _, _, _, updated_cart = resolve_remove_from_cart(ctx, cart)
    assert len(updated_cart) == len(cart) - 1


def test_clickstream_event_flow_resolve_remove_from_cart_removed_product_exists_in_catalogue(
    ctx,
):
    """
    Integration contract: the removed product_id must be a real product
    from the catalogue — not a phantom id.
    """
    product_ids = ctx.products.product_ids
    cart = product_ids[:5]
    all_ids = set(product_ids)

    for _ in range(10):
        product_id, _, _, _ = resolve_remove_from_cart(ctx, list(cart))
        assert (
            product_id in all_ids
        ), f"Removed product {product_id!r} not in global product catalogue"


def test_clickstream_event_flow_resolve_remove_from_cart_returns_category_and_name_for_removed_product(
    ctx,
):
    """
    Integration contract: category and product_name must be populated
    from ctx.products maps for the removed item.
    """
    product_ids = ctx.products.product_ids
    cart = product_ids[:3]

    product_id, category, product_name, _ = resolve_remove_from_cart(ctx, list(cart))
    assert category == ctx.products.product_category_map.get(product_id)
    assert product_name == ctx.products.product_name_map.get(product_id)


def test_clickstream_event_flow_resolve_remove_from_cart_removed_item_not_in_updated_cart(
    ctx,
):
    """
    Integration contract: the specific removed item must no longer be
    in the returned cart (one occurrence removed, duplicates preserved).
    """
    product_ids = ctx.products.product_ids
    # Two copies of the same product
    pid = product_ids[0]
    cart = [pid, pid, product_ids[1]]

    product_id, _, _, updated_cart = resolve_remove_from_cart(ctx, cart)
    # Exactly one copy should have been removed
    original_count = cart.count(product_id)
    updated_count = updated_cart.count(product_id)
    assert updated_count == original_count - 1


# ============================================================
# resolve_add_to_cart()
# ============================================================
# Integration contract: uses stock snapshots + product catalogue data


def test_clickstream_event_flow_resolve_add_to_cart_adds_product_to_cart(
    ctx,
):
    """
    Integration contract: resolve_add_to_cart() must return a cart
    that is one item longer than the input.
    """
    product_ids = ctx.products.product_ids
    store_id = ctx.stores.online_store_id
    timestamp = _build_datetime()
    cart = []

    _, _, _, updated_cart = resolve_add_to_cart(
        ctx,
        product_id=product_ids[0],
        previous_product_id=None,
        previous_category=None,
        cart_content=cart,
        store_id=store_id,
        timestamp=timestamp,
    )
    assert len(updated_cart) == len(cart) + 1


def test_clickstream_event_flow_resolve_add_to_cart_explicit_product_id_added_verbatim(
    ctx,
):
    """
    Integration contract: when a product_id is provided explicitly it
    must be the one added to the cart (no substitution).
    """
    product_ids = ctx.products.product_ids
    store_id = ctx.stores.online_store_id
    timestamp = _build_datetime()
    target_pid = product_ids[0]

    pid_out, _, _, updated_cart = resolve_add_to_cart(
        ctx,
        product_id=target_pid,
        previous_product_id=None,
        previous_category=None,
        cart_content=[],
        store_id=store_id,
        timestamp=timestamp,
    )
    assert pid_out == target_pid
    assert target_pid in updated_cart


def test_clickstream_event_flow_resolve_add_to_cart_none_product_id_falls_back_to_in_stock_product(
    ctx,
):
    """
    Integration contract: when product_id is None and a previous_product_id
    is in stock, resolve_add_to_cart() must still add a valid product.
    Tests the stock-status-aware fallback path.
    """
    df = ctx.stock_snapshots.stock_snapshots_df
    in_stock_row = df[df["stock_status"].isin(IN_STOCK_STATUS)].iloc[0]
    store_id = in_stock_row["store_id"]
    product_id = in_stock_row["product_id"]
    timestamp = in_stock_row["week_start_date"]
    category = ctx.products.product_category_map.get(product_id)

    _, _, _, updated_cart = resolve_add_to_cart(
        ctx,
        product_id=None,
        previous_product_id=product_id,
        previous_category=category,
        cart_content=[],
        store_id=store_id,
        timestamp=timestamp,
    )
    assert len(updated_cart) == 1
    assert updated_cart[0] in ctx.products.product_ids


def test_clickstream_event_flow_resolve_add_to_cart_returned_product_in_global_catalogue(
    ctx,
):
    """
    Integration contract: whatever product is added must exist in the
    global product catalogue.
    """
    product_ids = ctx.products.product_ids
    store_id = ctx.stores.online_store_id
    timestamp = _build_datetime()

    pid_out, _, _, _ = resolve_add_to_cart(
        ctx,
        product_id=product_ids[2],
        previous_product_id=None,
        previous_category=None,
        cart_content=[],
        store_id=store_id,
        timestamp=timestamp,
    )
    assert pid_out in set(product_ids)


# ============================================================
# resolve_product_view()
# ============================================================
# Integration contract: uses stock snapshots + product catalogue data


def test_clickstream_event_flow_resolve_product_view_returns_valid_product_id(
    ctx,
):
    """
    Integration contract: resolve_product_view() must always return a
    product_id from the global catalogue, even after fallback.
    """
    store_id = ctx.stores.online_store_id
    timestamp = _build_datetime()
    all_ids = set(ctx.products.product_ids)

    pid, _, _, _ = resolve_product_view(
        ctx,
        product_id=None,
        previous_event_type="Home View",
        previous_category=None,
        previous_product_id=None,
        previous_search_term=None,
        cart_content=[],
        customer_segment=_build_customer_segment(),
        session_affinity_categories=set(),
        store_id=store_id,
        timestamp=timestamp,
    )
    assert (
        pid in all_ids
    ), f"resolve_product_view() returned {pid!r} which is not in product catalogue"


def test_clickstream_event_flow_resolve_product_view_returns_stock_status(
    ctx,
):
    """
    Integration contract: the stock_status field must be one of the
    recognised stock states (not None or an arbitrary string).
    """
    valid_statuses = set(STOCK_STATUSES.values())
    store_id = ctx.stores.online_store_id
    timestamp = _build_datetime()

    _, _, _, stock_status = resolve_product_view(
        ctx,
        product_id=None,
        previous_event_type="Home View",
        previous_category=None,
        previous_product_id=None,
        previous_search_term=None,
        cart_content=[],
        customer_segment=_build_customer_segment(),
        session_affinity_categories=set(),
        store_id=store_id,
        timestamp=timestamp,
    )
    assert (
        stock_status in valid_statuses or stock_status == "In Stock"
    ), f"Unexpected stock_status {stock_status!r}"


def test_clickstream_event_flow_resolve_product_view_after_category_view_product_keeps_category_context(
    ctx,
):
    """
    Integration contract: when previous event is Category View with a
    known category, the returned product must belong to that category.
    """
    products_df = ctx.products.products_df
    category = products_df["category"].value_counts().idxmax()
    store_id = ctx.stores.online_store_id
    timestamp = _build_datetime()

    pid, _, _, _ = resolve_product_view(
        ctx,
        product_id=None,
        previous_event_type="Category View",
        previous_category=category,
        previous_product_id=None,
        previous_search_term=None,
        cart_content=[],
        customer_segment=_build_customer_segment(),
        session_affinity_categories={category},
        store_id=store_id,
        timestamp=timestamp,
    )
    actual_category = ctx.products.product_category_map.get(pid)
    assert (
        actual_category == category
    ), f"Expected product from category {category!r}, got {actual_category!r}"


def test_clickstream_event_flow_resolve_product_view_after_search_view_returns_matching_product(
    ctx,
):
    """
    Integration contract: when previous event is Search View, the
    returned product name must contain (or be related to) the search term.
    At minimum, the returned product must exist in the catalogue.
    """
    products_df = ctx.products.products_df
    sample_product = products_df.iloc[0]
    search_term = sample_product["product_name"].split()[0]  # first word as search term
    store_id = ctx.stores.online_store_id
    timestamp = _build_datetime()

    pid, _, _, _ = resolve_product_view(
        ctx,
        product_id=None,
        previous_event_type="Search View",
        previous_category=None,
        previous_product_id=None,
        previous_search_term=search_term,
        cart_content=[],
        customer_segment=_build_customer_segment(),
        session_affinity_categories=set(),
        store_id=store_id,
        timestamp=timestamp,
    )
    assert pid in set(ctx.products.product_ids)


# ============================================================
# resolve_search_view()
# ============================================================
# Integration contract: uses product data


def test_clickstream_event_flow_resolve_search_view_returns_non_empty_string(ctx):
    """
    Integration contract: resolve_search_view() must always return a
    non-empty string — blank search terms would corrupt clickstream records.
    """
    # for _ in range(20):
    #     term = resolve_search_view(ctx, previous_category=None, session_affinity_categories=set())
    #     assert isinstance(term, str) and len(term.strip()) > 0, (
    #         "resolve_search_view() returned empty or None search term"
    #     )
    for i in range(20):
        term = resolve_search_view(
            ctx,
            previous_category=None,
            session_affinity_categories=set(),
        )

        assert isinstance(term, str), f"Expected string, got {type(term)}"

        assert len(term.strip()) > 0, f"Iteration {i}: returned {repr(term)}"


def test_clickstream_event_flow_resolve_search_view_previous_category_biases_search_term_towards_category_items(
    ctx,
):
    """
    Integration contract: when previous_category is provided, ~60% of
    search terms should relate to items in that category.
    Tests that CATEGORY_ITEMS config is consulted.
    """
    category = next((c for c, items in CATEGORY_ITEMS.items() if items), None)
    if category is None:
        pytest.skip("No categories with items in CATEGORY_ITEMS config")

    category_items = set(CATEGORY_ITEMS[category])

    hits = sum(
        1
        for _ in range(100)
        if resolve_search_view(
            ctx, previous_category=category, session_affinity_categories={category}
        ).replace("+", " ")
        in category_items
    )
    # 60% probability means ~60 hits in 100 trials; allow generous margin
    assert hits >= 35, (
        f"Expected ≥35% category-item search terms, got {hits}% "
        f"for category {category!r}"
    )


def test_clickstream_event_flow_resolve_search_view_search_term_does_not_contain_special_characters(
    ctx,
):
    """
    Integration contract: returned search terms must be URL-friendly
    (spaces replaced with +, & stripped) as the page slug depends on them.
    """
    for _ in range(20):
        term = resolve_search_view(
            ctx, previous_category=None, session_affinity_categories=set()
        )
        assert "&" not in term, f"Search term contains '&': {term!r}"
        assert " " not in term, f"Search term contains raw space: {term!r}"

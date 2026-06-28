import random

from data_generation.config.products_config import CATEGORIES
from data_generation.services.clickstreams.clickstream_lookup_service import (
    get_random_product_from_category,
    get_random_product_from_search_term,
    get_search_term,
    get_segment_category,
    slugify,
)
from tests.helpers import (
    _build_category,
    _build_customer_segment,
)

# ============================================================
# get_search_term()
# ============================================================
# UNIT: only reads ctx.reference_data.search_terms — a static list,
# not a generated DataFrame.


def test_clickstream_lookup_functions_get_search_term(ctx):
    result = get_search_term(ctx)
    assert isinstance(result, str)
    assert "&" not in result
    assert " " not in result
    assert len(result) > 0


# ============================================================
# slugify()
# ============================================================


def test_clickstream_lookup_functions_slugify_space():
    assert slugify("Hello World") == "hello-world"


def test_clickstream_lookup_functions_slugify_ampersand_replaced():
    assert slugify("A & B") == "a-and-b"


def test_clickstream_lookup_functions_slugify_removes_punctuation():
    assert slugify("Python, Rocks!") == "python-rocks"


def test_clickstream_lookup_functions_slugify_multiple_spaces():
    assert slugify("Hello    World") == "hello-world"


def test_clickstream_lookup_functions_slugify_empty_string():
    assert slugify("") == ""


# ============================================================
# get_random_product_from_search_term()
# ============================================================
# UNIT: reads ctx.products.products_df (via ctx).
# The logic under test is string matching — not cross table joins.


def test_clickstream_lookup_functions_get_random_product_from_search_term(
    ctx, seed: int = 42
):
    # Simulate user search term using product
    df = ctx.products.products_df
    row = df.sample(n=1, random_state=seed).iloc[0]
    product_name = row["product_name"]
    search_term = product_name.split()[0]

    result = get_random_product_from_search_term(ctx, search_term)

    # Validate all returned products actually match search logic
    assert result is None or isinstance(result, list)
    if result:
        for pid in result:
            matched_name = df.loc[df["product_id"] == pid, "product_name"].iloc[0]
            assert search_term.replace("+", " ").lower() in matched_name.lower()


# ============================================================
# get_segment_category()
# ============================================================


def test_clickstream_lookup_functions_get_segment_category():
    customer_segment = _build_customer_segment()
    result = get_segment_category(customer_segment)
    assert isinstance(result, str)
    assert result in CATEGORIES


# ============================================================
# get_random_product_from_category()
# ============================================================
# UNIT: reads ctx.products.category_to_products (built from products_df).
# The logic is a dict lookup + random choice — no multi table wiring.


def test_clickstream_lookup_functions_get_random_product_from_category(
    ctx, seed: int = 42
):
    random.seed(seed)
    (category,) = _build_category(ctx, 1)
    result = get_random_product_from_category(ctx, category)
    assert result in ctx.products.category_to_products[category]


def test_clickstream_lookup_functions_get_random_product_from_category_empty(ctx):
    category = "NON_EXISTENT_CATEGORY"
    result = get_random_product_from_category(ctx, category)
    assert result is None

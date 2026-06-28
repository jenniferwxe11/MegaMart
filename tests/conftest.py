import pytest

from data_generation.context.context_factory import build_base_context
from data_generation.context.context_updater import refresh_context
from data_generation.data_retrieval import load_data

# from data_generation.run import generate_all_raw_data


# @pytest.fixture(scope="session")
# def generate_data():
#     print(">>> generate_data fixture is running")
#     generate_all_raw_data()


@pytest.fixture(scope="session")
def dataframes():
    return {
        "customers": load_data.load_customers(),
        "stores": load_data.load_stores(),
        "products": load_data.load_products(),
        "competitor_products": load_data.load_competitor_products(),
        "competitor_price_history": load_data.load_competitor_price_history(),
        "store_catalogues": load_data.load_store_catalogues(),
        "product_lifecycles": load_data.load_product_lifecycles(),
        "product_content_quality": load_data.load_product_content_quality(),
        "stockout_events": load_data.load_stockout_events(),
        "stock_snapshots": load_data.load_stock_snapshots(),
        "inventory_change_events": load_data.load_inventory_change_events(),
        "campaigns": load_data.load_campaigns(),
        "campaign_assignments": load_data.load_campaign_assignments(),
        "campaign_exposures": load_data.load_campaign_exposures(),
        "bundles": load_data.load_bundles(),
        "bundle_items": load_data.load_bundle_items(),
        "bundle_pricings": load_data.load_bundle_pricings(),
        "promotions": load_data.load_promotions(),
        "clickstreams": load_data.load_clickstreams(),
        "transactions": load_data.load_transactions(),
        "transaction_items": load_data.load_transaction_items(),
        "product_reviews": load_data.load_product_reviews(),
    }


@pytest.fixture(scope="session")
def ctx():
    ctx = build_base_context()
    refresh_context(ctx, "customers_generator")
    refresh_context(ctx, "stores_generator")
    refresh_context(ctx, "products_generator")
    refresh_context(ctx, "store_catalogues_generator")
    refresh_context(ctx, "product_lifecycles_generator")
    refresh_context(ctx, "product_content_quality_generator")
    refresh_context(ctx, "stockout_events_generator")
    refresh_context(ctx, "stock_snapshots_generator")
    refresh_context(ctx, "competitor_products_generator")
    refresh_context(ctx, "campaigns_generator")
    refresh_context(ctx, "campaign_assignments_generator")
    refresh_context(ctx, "bundles_generator")
    refresh_context(ctx, "promotions_generator")
    refresh_context(ctx, "clickstreams_generator")
    refresh_context(ctx, "transactions_generator")
    refresh_context(ctx, "product_reviews_generator")
    return ctx

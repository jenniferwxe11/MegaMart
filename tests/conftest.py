import pytest

from data_generation.data_retrieval import load_data


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

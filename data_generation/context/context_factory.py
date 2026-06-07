import pandas as pd

from data_generation.config.constants import (
    DATA_END_DATE,
    DATA_START_DATE,
    SIMULATION_DATE,
)
from data_generation.context.generation_context import (
    AppConfig,
    BundleContext,
    CampaignAssignmentContext,
    CampaignContext,
    ClickstreamContext,
    CompetitorProductContext,
    CustomerContext,
    GenerationContext,
    ProductContentQualityContext,
    ProductContext,
    ProductLifecycleContext,
    ProductReviewContext,
    PromotionContext,
    ReferenceDataContext,
    RegionAreaContext,
    StockoutEventContext,
    StockSnapshotContext,
    StoreCatalogueContext,
    StoreContext,
    TransactionContext,
)
from data_generation.data_retrieval import data_lookup, load_data


def build_base_context() -> GenerationContext:
    # =========================================================
    # LOAD DATAFRAMES
    # =========================================================

    region_area_df = load_data.load_region_areas()
    customers_df = load_data.load_customers()
    stores_df = load_data.load_stores()
    products_df = load_data.load_products()

    # =========================================================
    # LOOKUP MAPS
    # =========================================================

    region_area_map = data_lookup.get_region_area_map()
    area_region_map = data_lookup.get_area_region_map(region_area_map)
    customer_maps = data_lookup.get_customer_maps()
    store_maps = data_lookup.get_store_maps()
    product_maps = data_lookup.get_product_maps()

    # =========================================================
    # BUILD CONTEXT
    # =========================================================

    return GenerationContext(
        config=AppConfig(
            DATA_START_DATE=DATA_START_DATE,
            DATA_END_DATE=DATA_END_DATE,
            SIMULATION_DATE=SIMULATION_DATE,
        ),
        region_areas=RegionAreaContext(
            region_area_df=region_area_df,
            region_area_map=region_area_map,
            area_region_map=area_region_map,
        ),
        reference_data=ReferenceDataContext(
            search_terms=data_lookup.get_search_term(),
            locations=data_lookup.get_areas(),
        ),
        customers=CustomerContext(
            customers_df=customers_df,
            customer_ids=customer_maps["customer_ids"],
            customer_type_map=customer_maps["customer_type_map"],
            customer_segment_map=customer_maps["customer_segment_map"],
            customer_area_map=customer_maps["customer_area_map"],
            customer_region_map=customer_maps["customer_region_map"],
        ),
        stores=StoreContext(
            stores_df=stores_df,
            store_ids=store_maps["store_ids"],
            store_area_map=store_maps["store_area_map"],
            store_region_map=store_maps["store_region_map"],
            online_store_id=store_maps["online_store_id"],
            retail_store_ids=store_maps["retail_store_ids"],
        ),
        products=ProductContext(
            products_df=products_df,
            product_ids=product_maps["product_ids"],
            essential_product_ids=product_maps["essential_product_ids"],
            non_essential_product_ids=product_maps["non_essential_product_ids"],
            product_map=data_lookup.get_product_map(products_df),
            product_name_map=product_maps["product_name_map"],
            product_price_map=product_maps["product_price_map"],
            product_category_map=product_maps["product_category_map"],
            product_cost_map=product_maps["product_cost_map"],
            category_to_products=data_lookup.get_category_to_products(products_df),
        ),
        store_catalogues=StoreCatalogueContext(
            store_catalogues_df=pd.DataFrame(),
            store_product_price_map={},
            store_product_name_map={},
            store_product_category_map={},
        ),
        product_lifecycles=ProductLifecycleContext(
            product_lifecycles_df=pd.DataFrame(),
            product_discontinuation_map={},
            product_launch_map={},
            product_with_lifecycle_df=pd.DataFrame(),
        ),
        product_content_quality=ProductContentQualityContext(
            product_content_quality_df=pd.DataFrame(),
        ),
        stockout_events=StockoutEventContext(
            stockout_events_df=pd.DataFrame(),
            stockout_event_map={},
        ),
        stock_snapshots=StockSnapshotContext(
            stock_snapshots_df=pd.DataFrame(),
        ),
        competitor_products=CompetitorProductContext(
            competitor_products_df=pd.DataFrame(),
            competitor_price_history_df=pd.DataFrame(),
        ),
        campaigns=CampaignContext(
            campaigns_df=pd.DataFrame(),
        ),
        campaign_assignments=CampaignAssignmentContext(
            campaign_assignments_df=pd.DataFrame(),
            campaign_exposures_df=pd.DataFrame(),
        ),
        bundles=BundleContext(
            bundles_df=pd.DataFrame(),
            bundle_items_df=pd.DataFrame(),
            bundle_pricings_df=pd.DataFrame(),
            bundle_full_df=pd.DataFrame(),
            bundle_dict={},
        ),
        promotions=PromotionContext(
            promotions_df=pd.DataFrame(),
        ),
        clickstreams=ClickstreamContext(
            clickstreams_df=pd.DataFrame(),
            payment_success=pd.DataFrame(),
        ),
        transactions=TransactionContext(
            transactions_df=pd.DataFrame(),
            transaction_items_df=pd.DataFrame(),
            valid_transactions=pd.DataFrame(),
        ),
        product_reviews=ProductReviewContext(
            product_reviews_df=pd.DataFrame(),
        ),
    )

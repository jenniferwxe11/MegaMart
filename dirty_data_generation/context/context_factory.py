from data_generation.config.constants import (
    DATA_END_DATE,
    DATA_START_DATE,
    SIMULATION_DATE,
)
from data_generation.data_retrieval import data_lookup, load_data, transform_data
from dirty_data_generation.context.generation_context import (
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


def build_base_context() -> GenerationContext:

    # =========================================================
    # LOAD DATAFRAMES
    # =========================================================

    customers_df = load_data.load_customers()
    stores_df = load_data.load_stores()
    products_df = load_data.load_products()
    store_catalogues_df = load_data.load_store_catalogues()
    product_lifecycles_df = load_data.load_product_lifecycles()
    product_content_quality_df = load_data.load_product_content_quality()
    stockout_events_df = load_data.load_stockout_events()
    stock_snapshots_df = load_data.load_stock_snapshots()
    competitor_products_df = load_data.load_competitor_products()
    competitor_price_history_df = load_data.load_competitor_price_history()
    campaigns_df = transform_data.get_campaigns_df()
    campaign_assignments_df = load_data.load_campaign_assignments()
    campaign_exposures_df = load_data.load_campaign_exposures()
    bundles_df = load_data.load_bundles()
    bundle_pricings_df = load_data.load_bundle_pricings()
    bundle_items_df = load_data.load_bundle_items()
    bundle_full_df = transform_data.get_bundle_full()
    promotions_df = load_data.load_promotions()
    clickstreams_df = load_data.load_clickstreams()
    transactions_df = load_data.load_transactions()
    transaction_items_df = load_data.load_transaction_items()
    product_reviews_df = load_data.load_product_reviews()

    # =========================================================
    # LOOKUP MAPS
    # =========================================================

    customer_maps = data_lookup.get_customer_maps()
    store_maps = data_lookup.get_store_maps()
    product_maps = data_lookup.get_product_maps()
    catalogue_maps = data_lookup.get_store_catalogue_maps()
    lifecycle_maps = data_lookup.get_product_lifecycle_maps()
    bundle_dict = data_lookup.get_bundle_dict(bundle_items_df)

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
            area_region_map=data_lookup.get_area_region_map(),
            areas=data_lookup.get_areas(),
            regions=data_lookup.get_regions(),
        ),
        reference_data=ReferenceDataContext(
            search_terms=data_lookup.get_search_term(),
        ),
        customers=CustomerContext(
            customers_df=customers_df,
            customer_ids=customer_maps["customer_ids"],
            customer_type_to_ids_map=customer_maps["customer_type_to_ids_map"],
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
            store_catalogues_df=store_catalogues_df,
            store_product_price_map=catalogue_maps["store_product_price_map"],
            store_product_name_map=catalogue_maps["store_product_name_map"],
            store_product_category_map=catalogue_maps["store_product_category_map"],
        ),
        product_lifecycles=ProductLifecycleContext(
            product_lifecycles_df=product_lifecycles_df,
            product_discontinuation_map=lifecycle_maps["product_discontinuation_map"],
            product_launch_map=lifecycle_maps["product_launch_map"],
            product_with_lifecycle_df=transform_data.get_product_with_lifecycle(),
        ),
        product_content_quality=ProductContentQualityContext(
            product_content_quality_df=product_content_quality_df
        ),
        stockout_events=StockoutEventContext(
            stockout_events_df=stockout_events_df,
            stockout_event_map=data_lookup.get_stockout_event_map(),
        ),
        stock_snapshots=StockSnapshotContext(stock_snapshots_df=stock_snapshots_df),
        competitor_products=CompetitorProductContext(
            competitor_products_df=competitor_products_df,
            competitor_price_history_df=competitor_price_history_df,
        ),
        campaigns=CampaignContext(
            campaigns_df=campaigns_df,
        ),
        campaign_assignments=CampaignAssignmentContext(
            campaign_assignments_df=campaign_assignments_df,
            campaign_exposures_df=campaign_exposures_df,
        ),
        bundles=BundleContext(
            bundles_df=bundles_df,
            bundle_items_df=bundle_items_df,
            bundle_pricings_df=bundle_pricings_df,
            bundle_full_df=bundle_full_df,
            bundle_dict=bundle_dict,
        ),
        promotions=PromotionContext(promotions_df=promotions_df),
        clickstreams=ClickstreamContext(
            clickstreams_df=clickstreams_df,
            payment_success=data_lookup.get_payment_success(clickstreams_df),
        ),
        transactions=TransactionContext(
            transactions_df=transactions_df,
            transaction_items_df=transaction_items_df,
            valid_transactions=data_lookup.get_valid_transactions(
                transactions_df, transaction_items_df
            ),
        ),
        product_reviews=ProductReviewContext(product_reviews_df=product_reviews_df),
    )

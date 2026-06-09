from data_generation.context.generation_context import (
    BundleContext,
    CampaignAssignmentContext,
    CampaignContext,
    ClickstreamContext,
    CompetitorProductContext,
    CustomerContext,
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
from data_generation.data_retrieval import data_lookup, load_data, transform_data


def refresh_context(ctx, generator_name):

    # =========================================================
    # CUSTOMERS
    # =========================================================

    if generator_name == "customers_generator":
        customers_df = load_data.load_customers()
        customer_maps = data_lookup.get_customer_maps()
        ctx.customers = CustomerContext(
            customers_df=customers_df,
            customer_ids=customer_maps["customer_ids"],
            customer_type_to_ids_map=customer_maps["customer_type_to_ids_map"],
            customer_type_map=customer_maps["customer_type_map"],
            customer_segment_map=customer_maps["customer_segment_map"],
            customer_area_map=customer_maps["customer_area_map"],
            customer_region_map=customer_maps["customer_region_map"],
        )
        ctx.region_areas = RegionAreaContext(
            area_region_map=data_lookup.get_area_region_map(),
            areas=data_lookup.get_areas(),
            regions=data_lookup.get_regions(),
        )
        ctx.reference_data = ReferenceDataContext(
            search_terms=data_lookup.get_search_term(),
        )

    # =========================================================
    # STORES
    # =========================================================

    elif generator_name == "stores_generator":
        stores_df = load_data.load_stores()
        store_maps = data_lookup.get_store_maps()
        ctx.stores = StoreContext(
            stores_df=stores_df,
            store_ids=store_maps["store_ids"],
            store_area_map=store_maps["store_area_map"],
            store_region_map=store_maps["store_region_map"],
            online_store_id=store_maps["online_store_id"],
            retail_store_ids=store_maps["retail_store_ids"],
        )

    # =========================================================
    # PRODUCTS
    # =========================================================

    elif generator_name == "products_generator":
        products_df = load_data.load_products()
        product_maps = data_lookup.get_product_maps()
        ctx.products = ProductContext(
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
        )

    # =========================================================
    # STORE CATALOGUES
    # =========================================================

    elif generator_name == "store_catalogues_generator":

        store_catalogues_df = load_data.load_store_catalogues()
        catalogue_maps = data_lookup.get_store_catalogue_maps()

        ctx.store_catalogues = StoreCatalogueContext(
            store_catalogues_df=store_catalogues_df,
            store_product_price_map=catalogue_maps["store_product_price_map"],
            store_product_name_map=catalogue_maps["store_product_name_map"],
            store_product_category_map=catalogue_maps["store_product_category_map"],
        )

    # =========================================================
    # PRODUCT LIFECYCLES
    # =========================================================

    elif generator_name == "product_lifecycles_generator":

        product_lifecycles_df = load_data.load_product_lifecycles()
        lifecycle_maps = data_lookup.get_product_lifecycle_maps()

        ctx.product_lifecycles = ProductLifecycleContext(
            product_lifecycles_df=product_lifecycles_df,
            product_discontinuation_map=lifecycle_maps["product_discontinuation_map"],
            product_launch_map=lifecycle_maps["product_launch_map"],
            product_with_lifecycle_df=transform_data.get_product_with_lifecycle(),
        )

    # =========================================================
    # PRODUCT CONTENT QUALITY
    # =========================================================

    elif generator_name == "product_content_quality_generator":

        product_content_quality_df = load_data.load_product_content_quality()

        ctx.product_content_quality = ProductContentQualityContext(
            product_content_quality_df=product_content_quality_df
        )

    # =========================================================
    # STOCKOUT EVENTS
    # =========================================================

    elif generator_name == "stockout_events_generator":

        stockout_events_df = load_data.load_stockout_events()

        ctx.stockout_events = StockoutEventContext(
            stockout_events_df=stockout_events_df,
            stockout_event_map=data_lookup.get_stockout_event_map(),
        )

    # =========================================================
    # STOCK SNAPSHOTS
    # =========================================================

    elif generator_name == "stock_snapshots_generator":

        stock_snapshots_df = load_data.load_stock_snapshots()

        ctx.stock_snapshots = StockSnapshotContext(
            stock_snapshots_df=stock_snapshots_df
        )

    # =========================================================
    # COMPETITOR PRODUCTS
    # =========================================================

    elif generator_name == "competitor_products_generator":

        competitor_products_df = load_data.load_competitor_products()
        competitor_price_history_df = load_data.load_competitor_price_history()

        ctx.competitor_products = CompetitorProductContext(
            competitor_products_df=competitor_products_df,
            competitor_price_history_df=competitor_price_history_df,
        )

    # =========================================================
    # CAMPAIGNS
    # =========================================================

    elif generator_name == "campaigns_generator":

        campaigns_df = transform_data.get_campaigns_df()

        ctx.campaigns = CampaignContext(
            campaigns_df=campaigns_df,
        )

    # =========================================================
    # CAMPAIGN ASSIGNMENTS
    # =========================================================

    elif generator_name == "campaign_assignments_generator":

        campaign_assignments_df = load_data.load_campaign_assignments()
        campaign_exposures_df = load_data.load_campaign_exposures()

        ctx.campaign_assignments = CampaignAssignmentContext(
            campaign_assignments_df=campaign_assignments_df,
            campaign_exposures_df=campaign_exposures_df,
        )

    # =========================================================
    # BUNDLES
    # =========================================================

    elif generator_name == "bundles_generator":

        bundles_df = load_data.load_bundles()
        bundle_pricings_df = load_data.load_bundle_pricings()
        bundle_items_df = load_data.load_bundle_items()
        bundle_full_df = transform_data.get_bundle_full()
        bundle_dict = data_lookup.get_bundle_dict(bundle_items_df)

        ctx.bundles = BundleContext(
            bundles_df=bundles_df,
            bundle_items_df=bundle_items_df,
            bundle_pricings_df=bundle_pricings_df,
            bundle_full_df=bundle_full_df,
            bundle_dict=bundle_dict,
        )

    # =========================================================
    # PROMOTIONS
    # =========================================================

    elif generator_name == "promotions_generator":

        promotions_df = load_data.load_promotions()

        ctx.promotions = PromotionContext(promotions_df=promotions_df)

    # =========================================================
    # CLICKSTREAMS
    # =========================================================

    elif generator_name == "clickstreams_generator":

        clickstreams_df = load_data.load_clickstreams()

        ctx.clickstreams = ClickstreamContext(
            clickstreams_df=clickstreams_df,
            payment_success=data_lookup.get_payment_success(clickstreams_df),
        )

    # =========================================================
    # TRANSACTIONS
    # =========================================================

    elif generator_name == "transactions_generator":

        transactions_df = load_data.load_transactions()
        transaction_items_df = load_data.load_transaction_items()

        ctx.transactions = TransactionContext(
            transactions_df=transactions_df,
            transaction_items_df=transaction_items_df,
            valid_transactions=data_lookup.get_valid_transactions(
                transactions_df, transaction_items_df
            ),
        )

    # =========================================================
    # PRODUCT REVIEWS
    # =========================================================

    elif generator_name == "product_reviews_generator":

        product_reviews_df = load_data.load_product_reviews()

        ctx.product_reviews = ProductReviewContext(
            product_reviews_df=product_reviews_df
        )

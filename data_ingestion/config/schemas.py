# data_ingestion/config/schemas.py

from google.cloud import bigquery

BUNDLE_ITEMS_SCHEMA = [
    bigquery.SchemaField("bundle_id", "STRING"),
    bigquery.SchemaField("product_id", "STRING"),
    bigquery.SchemaField("quantity", "INTEGER"),
]
BUNDLE_PRICINGS_SCHEMA = [
    bigquery.SchemaField("bundle_pricing_id", "STRING"),
    bigquery.SchemaField("bundle_id", "STRING"),
    bigquery.SchemaField("bundle_price", "FLOAT"),
    bigquery.SchemaField("discount_value", "FLOAT"),
    bigquery.SchemaField("effective_start_date", "DATE"),
    bigquery.SchemaField("effective_end_date", "DATE"),
    bigquery.SchemaField("pricing_phase", "STRING"),
]
BUNDLES_SCHEMA = [
    bigquery.SchemaField("bundle_id", "STRING"),
    bigquery.SchemaField("bundle_name", "STRING"),
    bigquery.SchemaField("bundle_type", "STRING"),
    bigquery.SchemaField("categories", "STRING"),
]
CAMPAIGN_ASSIGNMENTS_SCHEMA = [
    bigquery.SchemaField("campaign_id", "STRING"),
    bigquery.SchemaField("customer_id", "STRING"),
    bigquery.SchemaField("assignment_group", "STRING"),
    bigquery.SchemaField("eligible_at", "TIMESTAMP"),
]
CAMPAIGN_EXPOSURES_SCHEMA = [
    bigquery.SchemaField("customer_id", "STRING"),
    bigquery.SchemaField("campaign_id", "STRING"),
    bigquery.SchemaField("channel", "STRING"),
    bigquery.SchemaField("assignment_group", "STRING"),
    bigquery.SchemaField("eligible", "BOOL"),
    bigquery.SchemaField("exposed", "BOOL"),
    bigquery.SchemaField("exposed_time", "TIMESTAMP"),
    bigquery.SchemaField("opened", "BOOL"),
    bigquery.SchemaField("opened_time", "TIMESTAMP"),
    bigquery.SchemaField("clicked", "BOOL"),
    bigquery.SchemaField("clicked_time", "TIMESTAMP"),
    bigquery.SchemaField("device_platform", "STRING"),
    bigquery.SchemaField("cost_per_msg", "FLOAT"),
]
CAMPAIGNS_SCHEMA = [
    bigquery.SchemaField("campaign_id", "STRING"),
    bigquery.SchemaField("campaign_name", "STRING"),
    bigquery.SchemaField("campaign_type", "STRING"),
    bigquery.SchemaField("target_segment", "STRING"),
    bigquery.SchemaField("season", "STRING"),
    bigquery.SchemaField("channels", "STRING"),
    bigquery.SchemaField("start_date", "DATE"),
    bigquery.SchemaField("end_date", "DATE"),
    bigquery.SchemaField("budget", "INTEGER"),
    bigquery.SchemaField("is_ab_test", "STRING"),
    bigquery.SchemaField("status", "STRING"),
]
CLICKSTREAM_SCHEMA = [
    bigquery.SchemaField("clickstream_id", "STRING"),
    bigquery.SchemaField("session_id", "STRING"),
    bigquery.SchemaField("customer_id", "STRING"),
    bigquery.SchemaField("customer_segment", "STRING"),
    bigquery.SchemaField("campaign_ids", "STRING"),
    bigquery.SchemaField("has_treatment_campaign", "BOOL"),
    bigquery.SchemaField("has_control_campaign", "BOOL"),
    bigquery.SchemaField("device_category", "STRING"),
    bigquery.SchemaField("referrer", "STRING"),
    bigquery.SchemaField("location", "STRING"),
    bigquery.SchemaField("event_timestamp", "TIMESTAMP"),
    bigquery.SchemaField("event_order", "INTEGER"),
    bigquery.SchemaField("event_type", "STRING"),
    bigquery.SchemaField("page", "STRING"),
    bigquery.SchemaField("scroll_depth", "FLOAT"),
    bigquery.SchemaField("product_id", "STRING"),
    bigquery.SchemaField("product_name", "STRING"),
    bigquery.SchemaField("category", "STRING"),
    bigquery.SchemaField("promotion_ids", "STRING"),
    bigquery.SchemaField("bundle_ids", "STRING"),
    bigquery.SchemaField("bounce_flag", "STRING"),
    bigquery.SchemaField("cart_size", "INTEGER"),
    bigquery.SchemaField("cart_content", "STRING"),
    bigquery.SchemaField("purchased_items", "STRING"),
    bigquery.SchemaField("stock_status", "STRING"),
]
COMPETITOR_PRICE_HISTORY_SCHEMA = [
    bigquery.SchemaField("competitor", "STRING"),
    bigquery.SchemaField("product_id", "STRING"),
    bigquery.SchemaField("scraped_product_name", "STRING"),
    bigquery.SchemaField("scraped_category", "STRING"),
    bigquery.SchemaField("scraped_price", "FLOAT"),
    bigquery.SchemaField("has_active_promo", "STRING"),
    bigquery.SchemaField("update_timestamp", "TIMESTAMP"),
]
COMPETITOR_PRODUCTS_SCHEMA = [
    bigquery.SchemaField("competitor", "STRING"),
    bigquery.SchemaField("product_id", "STRING"),
    bigquery.SchemaField("product_name", "STRING"),
    bigquery.SchemaField("brand", "STRING"),
    bigquery.SchemaField("category", "STRING"),
    bigquery.SchemaField("is_exclusive", "BOOL"),
]
CUSTOMERS_SCHEMA = [
    bigquery.SchemaField("customer_id", "STRING"),
    bigquery.SchemaField("customer_type", "STRING"),
    bigquery.SchemaField("customer_name", "STRING"),
    bigquery.SchemaField("email", "STRING"),
    bigquery.SchemaField("gender", "STRING"),
    bigquery.SchemaField("dob", "DATE"),
    bigquery.SchemaField("area", "STRING"),
    bigquery.SchemaField("region", "STRING"),
    bigquery.SchemaField("signup_date", "DATE"),
    bigquery.SchemaField("loyalty_points", "INTEGER"),
    bigquery.SchemaField("customer_segment", "STRING"),
    bigquery.SchemaField("email_marketing_opt_in", "BOOL"),
    bigquery.SchemaField("sms_marketing_opt_in", "BOOL"),
    bigquery.SchemaField("push_notifications_opt_in", "BOOL"),
    bigquery.SchemaField("device_category", "STRING"),
    bigquery.SchemaField("device_platform", "STRING"),
]
INVENTORY_CHANGE_EVENTS_SCHEMA = [
    bigquery.SchemaField("store_id", "STRING"),
    bigquery.SchemaField("product_id", "STRING"),
    bigquery.SchemaField("event_timestamp", "TIMESTAMP"),
    bigquery.SchemaField("delta", "INTEGER"),
    bigquery.SchemaField("reason", "STRING"),
    bigquery.SchemaField("stock_after", "INTEGER"),
]
PRODUCT_CONTENT_QUALITY_SCHEMA = [
    bigquery.SchemaField("content_version_id", "STRING"),
    bigquery.SchemaField("product_id", "STRING"),
    bigquery.SchemaField("quality_tier", "STRING"),
    bigquery.SchemaField("has_image", "BOOL"),
    bigquery.SchemaField("image_count", "INTEGER"),
    bigquery.SchemaField("image_quality_score", "FLOAT"),
    bigquery.SchemaField("has_nutritional_info", "BOOL"),
    bigquery.SchemaField("has_description", "BOOL"),
    bigquery.SchemaField("description_length", "INTEGER"),
    bigquery.SchemaField("missing_attribute_count", "INTEGER"),
    bigquery.SchemaField("valid_from", "DATE"),
    bigquery.SchemaField("valid_to", "DATE"),
    bigquery.SchemaField("is_current", "BOOL"),
]
PRODUCT_LIFECYCLES_SCHEMA = [
    bigquery.SchemaField("product_id", "STRING"),
    bigquery.SchemaField("status", "STRING"),
    bigquery.SchemaField("launch_date", "DATE"),
    bigquery.SchemaField("discontinuation_date", "DATE"),
    bigquery.SchemaField("valid_from", "DATE"),
    bigquery.SchemaField("valid_to", "DATE"),
    bigquery.SchemaField("is_current", "BOOL"),
]
PRODUCT_REVIEWS_SCHEMA = [
    bigquery.SchemaField("review_id", "STRING"),
    bigquery.SchemaField("transaction_id", "STRING"),
    bigquery.SchemaField("product_id", "STRING"),
    bigquery.SchemaField("customer_id", "STRING"),
    bigquery.SchemaField("rating", "INTEGER"),
    bigquery.SchemaField("review_text", "STRING"),
    bigquery.SchemaField("review_date", "DATE"),
]
PRODUCTS_SCHEMA = [
    bigquery.SchemaField("product_id", "STRING"),
    bigquery.SchemaField("product_name", "STRING"),
    bigquery.SchemaField("brand", "STRING"),
    bigquery.SchemaField("category", "STRING"),
    bigquery.SchemaField("selling_price", "FLOAT"),
    bigquery.SchemaField("cost_price", "FLOAT"),
]
PROMOTIONS_SCHEMA = [
    bigquery.SchemaField("promotion_id", "STRING"),
    bigquery.SchemaField("promotion_name", "STRING"),
    bigquery.SchemaField("promotion_theme", "STRING"),
    bigquery.SchemaField("campaign_id", "STRING"),
    bigquery.SchemaField("promotion_mechanic", "STRING"),
    bigquery.SchemaField("promotion_scope", "STRING"),
    bigquery.SchemaField("promotion_target_id", "STRING"),
    bigquery.SchemaField("promotion_value", "FLOAT"),
    bigquery.SchemaField("min_spend", "FLOAT"),
    bigquery.SchemaField("discount_code", "STRING"),
    bigquery.SchemaField("effective_start_date", "DATE"),
    bigquery.SchemaField("effective_end_date", "DATE"),
    bigquery.SchemaField("priority", "INTEGER"),
]
STOCK_SNAPSHOTS_SCHEMA = [
    bigquery.SchemaField("week_start_date", "DATE"),
    bigquery.SchemaField("store_id", "STRING"),
    bigquery.SchemaField("product_id", "STRING"),
    bigquery.SchemaField("stock_status", "STRING"),
    bigquery.SchemaField("stock_band", "STRING"),
]
STOCKOUT_EVENTS_SCHEMA = [
    bigquery.SchemaField("store_id", "STRING"),
    bigquery.SchemaField("product_id", "STRING"),
    bigquery.SchemaField("stockout_start_date", "DATE"),
    bigquery.SchemaField("stockout_end_date", "DATE"),
]
STORE_CATALOGUES_SCHEMA = [
    bigquery.SchemaField("store_id", "STRING"),
    bigquery.SchemaField("product_id", "STRING"),
    bigquery.SchemaField("store_product_name", "STRING"),
    bigquery.SchemaField("store_brand", "STRING"),
    bigquery.SchemaField("store_category", "STRING"),
    bigquery.SchemaField("store_selling_price", "FLOAT"),
]
STORES_SCHEMA = [
    bigquery.SchemaField("store_id", "STRING"),
    bigquery.SchemaField("store_name", "STRING"),
    bigquery.SchemaField("area", "STRING"),
    bigquery.SchemaField("region", "STRING"),
    bigquery.SchemaField("store_type", "STRING"),
]
TRANSACTION_ITEMS_SCHEMA = [
    bigquery.SchemaField("transaction_id", "STRING"),
    bigquery.SchemaField("product_id", "STRING"),
    bigquery.SchemaField("product_name", "STRING"),
    bigquery.SchemaField("category", "STRING"),
    bigquery.SchemaField("quantity", "INTEGER"),
    bigquery.SchemaField("unit_price", "FLOAT"),
    bigquery.SchemaField("item_subtotal", "FLOAT"),
    bigquery.SchemaField("item_discount", "FLOAT"),
    bigquery.SchemaField("final_item_price", "FLOAT"),
]
TRANSACTIONS_SCHEMA = [
    bigquery.SchemaField("transaction_id", "STRING"),
    bigquery.SchemaField("customer_id", "STRING"),
    bigquery.SchemaField("store_id", "STRING"),
    bigquery.SchemaField("transaction_time", "TIMESTAMP"),
    bigquery.SchemaField("cart_subtotal", "FLOAT"),
    bigquery.SchemaField("total_discount", "FLOAT"),
    bigquery.SchemaField("shipping_fee", "FLOAT"),
    bigquery.SchemaField("shipping_discount", "FLOAT"),
    bigquery.SchemaField("transaction_total", "FLOAT"),
    bigquery.SchemaField("payment_method", "STRING"),
    bigquery.SchemaField("basket_size", "INTEGER"),
    bigquery.SchemaField("num_unique_items", "INTEGER"),
    bigquery.SchemaField("applied_promotions", "STRING"),
]

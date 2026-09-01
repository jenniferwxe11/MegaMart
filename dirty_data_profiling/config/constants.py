from pathlib import Path

REPORTS_DIR = Path("dirty_data_profiling/reports")
DIRTY_DIR = Path("dirty_data_generation/dirty_data")


FILES = [
    "customers_dirty.csv",
    "products_dirty.csv",
    "promotions_dirty.csv",
    "campaigns_dirty.csv",
    "bundles_dirty.csv",
    "bundle_pricings_dirty.csv",
    "clickstreams_dirty.csv",
    "transactions_dirty.csv",
    "transaction_items_dirty.csv",
    "store_catalogues_dirty.csv",
    "stock_snapshots_dirty.csv",
    "product_reviews_dirty.csv",
    "competitor_price_history_dirty.csv",
    "campaign_exposures_dirty.csv",
    "product_content_quality_dirty.csv",
]


SEVERITY_MAP = {
    "duplicate": "Medium",
    "duplicate row": "Medium",
    "missing": "Medium",
    "formatting": "Low",
    "whitespace": "Low",
    "future": "High",
    "negative": "High",
    "invalid": "High",
    "mismatch": "Medium",
    "orphan": "High",
    "outlier": "High",
}


CATEGORY_MAP = {
    "missing": "Missing Values",
    "duplicate": "Duplicate Records",
    "duplicate row": "Duplicate Records",
    "formatting": "Formatting",
    "whitespace": "Formatting",
    "future": "Date Issues",
    "negative": "Numeric Issues",
    "invalid": "Business Rule Violations",
    "mismatch": "Business Rule Violations",
    "orphan": "Referential Integrity",
    "outlier": "Outliers",
}


BUSINESS_IMPACT = {
    "Missing Values": "Missing information may reduce reporting completeness and affect downstream analytics.",
    "Formatting": "Formatting inconsistencies may create duplicate entities and reduce data standardisation.",
    "Duplicate Records": "Duplicate records may result in double-counting and inaccurate KPI calculations.",
    "Date Issues": "Incorrect dates affect historical reporting and time-based analyses.",
    "Numeric Issues": "Invalid numeric values reduce the accuracy of operational and financial reporting.",
    "Business Rule Violations": "Business rules have been violated and should be corrected before analytics.",
    "Referential Integrity": "Broken relationships may prevent datasets from joining correctly.",
    "Outliers": "Extreme values may distort trend analysis and predictive models.",
    "Other": "Additional data quality issues require further investigation.",
}


CLEANING_RULES = {
    "Missing Values": "Replace missing values using defaults, NULL handling or business rules.",
    "Formatting": "Trim whitespace, standardise casing and remove unnecessary characters.",
    "Duplicate Records": "Retain only the latest valid record using ROW_NUMBER().",
    "Date Issues": "Validate dates using SAFE_CAST() and reject impossible values.",
    "Numeric Issues": "Remove or correct invalid numeric values before analysis.",
    "Business Rule Violations": "Correct records that violate business constraints using CASE expressions or filtering.",
    "Referential Integrity": "Validate foreign keys before loading curated tables.",
    "Outliers": "Review extreme values using business thresholds before removal.",
    "Other": "Manual review required.",
}


DBT_RECOMMENDATIONS = {
    "Missing Values": "coalesce(), nullif()",
    "Formatting": "trim(), upper(), lower(), initcap()",
    "Duplicate Records": "row_number() over (...) qualify row_number() = 1",
    "Date Issues": "safe_cast(), least(), greatest()",
    "Numeric Issues": "abs(), safe_cast(), filter invalid values",
    "Business Rule Violations": "case when ... end",
    "Referential Integrity": "relationship tests + left joins",
    "Outliers": "IQR filtering or business thresholds",
    "Other": "Manual investigation",
}

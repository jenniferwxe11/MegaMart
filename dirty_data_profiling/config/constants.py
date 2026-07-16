REPORTS_DIR = "dirty_data_profiling/reports"


SEVERITY_MAP = {
    "duplicate": "Medium",
    "duplicate row": "Medium",
    "missing": "Medium",
    "formatting": "Low",
    "whitespace": "Low",
    "future": "High",
    "negative": "High",
    "invalid": "High",
    "outlier": "High",
    "mismatch": "Medium",
    "orphan": "High",
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
    "Missing Values": "Missing information reduces reporting completeness and may affect downstream analytics.",
    "Formatting": "Formatting inconsistencies create duplicate entities and reduce search accuracy.",
    "Duplicate Records": "Duplicate records may inflate KPIs and produce incorrect aggregations.",
    "Date Issues": "Invalid dates affect trend analysis, scheduling and time based reporting.",
    "Numeric Issues": "Invalid numeric values lead to inaccurate financial and operational metrics.",
    "Business Rule Violations": "Business rules have been violated and should be corrected before analytics.",
    "Referential Integrity": "Broken relationships prevent reliable joins across datasets.",
    "Outliers": "Extreme values may represent data entry errors or unusual business events.",
    "Other": "Miscellaneous data quality issues requiring further investigation.",
}

BUSINESS_IMPACT = {
    "Missing Values": "Missing information may reduce reporting completeness and affect downstream analytics.",
    "Formatting": "Formatting inconsistencies may create duplicate entities and reduce data standardisation.",
    "Duplicate Records": "Duplicate records may result in double-counting and inaccurate KPI calculations.",
    "Invalid Values": "Invalid values violate business rules and reduce confidence in analytical outputs.",
    "Date Issues": "Incorrect dates affect historical reporting and time-based analyses.",
    "Relationship Issues": "Broken relationships may prevent datasets from joining correctly.",
    "Outliers": "Extreme values may distort averages, forecasting models and trend analysis.",
    "Other": "Additional data quality issues require further investigation.",
}

DBT_RECOMMENDATIONS = {
    "Missing Values": "coalesce(), nullif()",
    "Formatting": "trim(), initcap(), lower(), upper()",
    "Duplicate Records": "row_number() over (...) qualify row_number = 1",
    "Date Issues": "safe_cast(), least(), greatest()",
    "Numeric Issues": "abs(), safe_cast(), filter invalid values",
    "Business Rule Violations": "case when ... end",
    "Referential Integrity": "relationship tests + left joins",
    "Outliers": "IQR filtering or business thresholds",
    "Other": "Manual investigation",
}

CLEANING_RULES = {
    "Formatting": "Trim whitespace, standardise casing and remove unnecessary characters.",
    "Missing Values": "Replace missing values using defaults, NULL handling or business rules.",
    "Duplicate Records": "Retain only the latest valid record using ROW_NUMBER().",
    "Date Issues": "Validate dates using SAFE_CAST() and reject impossible values.",
    "Invalid Values": "Replace invalid values or remove records failing business rules.",
    "Relationship Issues": "Validate foreign keys before loading curated tables.",
    "Outliers": "Review extreme values and determine whether to retain or exclude.",
}

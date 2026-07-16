from __future__ import annotations

import ast
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from dirty_data_generation.utils.error_registry import load_registry
from dirty_data_profiling.config.constants import (
    BUSINESS_IMPACT,
    CATEGORY_MAP,
    SEVERITY_MAP,
)

# ---------------------------
# Data Classes
# ---------------------------


@dataclass(slots=True)
class DatasetStats:
    total_rows: int
    dirty_rows: int
    clean_rows: int
    dirty_ratio: float
    health_score: float


@dataclass(slots=True)
class ProfileResult:
    dataset: str
    dataframe: pd.DataFrame
    stats: DatasetStats
    error_counter: Counter
    category_counter: Counter
    severity_counter: Counter
    numeric_profile: dict[str, Any]
    outlier_results: dict[str, Any]
    corrupted_columns: Counter
    error_density: pd.Series
    dirty_examples: pd.DataFrame


# ---------------------------
# Helper Functions
# ---------------------------


def _parse(value):
    if pd.isna(value):
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, str):
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return []

    return []


def parse_error_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Safely convert the error_types column from strings into Python lists.
    """
    if "error_types" not in df.columns:
        df = df.copy()
        df["error_types"] = [[] for _ in range(len(df))]
        return df

    parsed = [_parse(x) for x in df["error_types"]]
    df = df.copy()
    df["error_types"] = pd.Series(
        parsed,
        index=df.index,
        dtype="object",
    )

    return df


def profile_from_csv(
    dataset_name: str,
    csv_path: str | Path,
) -> ProfileResult:
    """
    Convenience wrapper around profile_dataset().
    """
    return profile_dataset(
        dataset_name=dataset_name,
        file_path=csv_path,
    )


def total_error_count(result: ProfileResult) -> int:
    """
    Total number of detected errors.
    """
    return int(sum(result.error_counter.values()))


def dominant_error(result: ProfileResult) -> str:
    """
    Most common error.
    """
    if not result.error_counter:
        return "None"

    return result.error_counter.most_common(1)[0][0]


def dominant_category(result: ProfileResult) -> str:
    """
    Largest business issue category.
    """
    if not result.category_counter:
        return "None"

    return result.category_counter.most_common(1)[0][0]


def dominant_column(result: ProfileResult) -> str:
    """
    Most frequently affected column.
    """
    if not result.corrupted_columns:
        return "None"

    return result.corrupted_columns.most_common(1)[0][0]


def build_summary_dict(result: ProfileResult) -> dict[str, Any]:
    """
    Convert a ProfileResult into a single row suitable for
    summary_report.csv.
    """
    return {
        "dataset": result.dataset,
        "total_rows": result.stats.total_rows,
        "dirty_rows": result.stats.dirty_rows,
        "clean_rows": result.stats.clean_rows,
        "dirty_ratio": round(result.stats.dirty_ratio, 4),
        "health_score": result.stats.health_score,
        "total_errors": total_error_count(result),
        "unique_error_types": len(result.error_counter),
        "largest_category": dominant_category(result),
        "top_error": dominant_error(result),
        "worst_column": dominant_column(result),
        "high_severity": result.severity_counter.get("High", 0),
        "medium_severity": result.severity_counter.get("Medium", 0),
        "low_severity": result.severity_counter.get("Low", 0),
        "numeric_columns": len(result.numeric_profile),
        "outlier_columns": len(result.outlier_results),
    }


# ---------------------------
# Error Type Functions
# ---------------------------


def calculate_health_score(dirty_ratio: float) -> float:
    """
    Convert dirty ratio into a simple health score.
    100 = perfectly clean
    0 = completely dirty
    """
    return round(max(0.0, 100 - dirty_ratio * 100), 2)


def build_dataset_stats(df: pd.DataFrame) -> DatasetStats:
    """
    Compute overall dataset statistics.
    """
    dirty_rows = df["error_types"].apply(len).gt(0).sum()
    clean_rows = len(df) - dirty_rows
    dirty_ratio = dirty_rows / len(df) if len(df) else 0

    return DatasetStats(
        total_rows=len(df),
        dirty_rows=int(dirty_rows),
        clean_rows=int(clean_rows),
        dirty_ratio=dirty_ratio,
        health_score=calculate_health_score(dirty_ratio),
    )


def count_errors(df: pd.DataFrame) -> Counter:
    """
    Count occurrences of every unique error.
    """
    counter: Counter[str] = Counter()
    for errors in df["error_types"]:
        counter.update(errors)
    return counter


def classify_error(error_name: str) -> tuple[str, str]:
    """
    Classify an error into a business friendly category and severity level.
    """
    error_lower = error_name.lower()
    category = "Other"
    severity = "Unknown"

    for keyword, value in CATEGORY_MAP.items():
        if keyword in error_lower:
            category = value
            break

    for keyword, value in SEVERITY_MAP.items():
        if keyword in error_lower:
            severity = value
            break

    return category, severity


def build_category_counter(error_counter: Counter) -> Counter:
    """
    Aggregate errors into business friendly categories.
    """
    categories: Counter[str] = Counter()
    for error, count in error_counter.items():
        category, _ = classify_error(error)
        categories[category] += count
    return categories


def build_severity_counter(error_counter: Counter) -> Counter:
    """
    Aggregate errors into Low, Medium, High severity.
    """
    severities: Counter[str] = Counter()
    for error, count in error_counter.items():
        _, severity = classify_error(error)
        severities[severity] += count
    return severities


def build_error_density(df: pd.DataFrame) -> pd.Series:
    """
    Distribution of number of errors per row.
    """
    density = df.copy()
    density["num_errors"] = density["error_types"].apply(len)
    return density["num_errors"].value_counts().sort_index()


def infer_corrupted_columns(error_counter: Counter) -> Counter:
    """
    Infer the most frequently affected columns.
    """
    ERROR_METADATA = load_registry()

    columns: Counter[str] = Counter()
    for error, count in error_counter.items():
        metadata = ERROR_METADATA.get(error)
        if metadata is None:
            continue

        for col in metadata["columns"]:
            columns[col] += count

    return columns


# ---------------------------
# Numeric Profiling Functions
# ---------------------------


def profile_numeric_columns(df: pd.DataFrame) -> dict[str, dict[str, float]]:
    """
    Generate descriptive statistics for all numeric columns.
    """
    numeric_columns = [
        column
        for column in df.select_dtypes(include="number").columns
        if column != "num_errors"
    ]

    profile = {}

    for column in numeric_columns:
        series = df[column].dropna()
        if series.empty:
            continue

        profile[column] = {
            "count": int(series.count()),
            "missing": int(df[column].isna().sum()),
            "mean": float(round(series.mean(), 2)),
            "median": float(round(series.median(), 2)),
            "std": float(round(series.std(), 2)),
            "min": float(round(series.min(), 2)),
            "q1": float(round(series.quantile(0.25), 2)),
            "q3": float(round(series.quantile(0.75), 2)),
            "max": float(round(series.max(), 2)),
        }

    return profile


def detect_outliers(df: pd.DataFrame) -> dict[str, dict]:
    """
    Detect outliers using the IQR rule.
    """
    numeric_columns = [
        column
        for column in df.select_dtypes(include="number").columns
        if column != "num_errors"
    ]

    results = {}

    for column in numeric_columns:
        series = df[column].dropna()

        # Need at least 10 data points to perform outlier detection
        if len(series) < 10:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        outliers = series[(series < lower) | (series > upper)]

        results[column] = {
            "valid_rows": len(series),
            "outlier_count": int(len(outliers)),
            "outlier_ratio": round(len(outliers) / len(series), 4),
            "lower_bound": round(lower, 2),
            "upper_bound": round(upper, 2),
        }

    return results


def extract_dirty_examples(
    df: pd.DataFrame,
    sample_size: int = 20,
) -> pd.DataFrame:
    """
    Return representative dirty rows.

    Attempts to include at least one example of every detected error type
    before filling the remaining quota with additional dirty records.
    """

    dirty = df[df["error_types"].apply(len).gt(0)].copy()

    if dirty.empty:
        return dirty

    selected_indices = []
    covered_errors = set()

    # First pass: one row per unseen error type
    for index, row in dirty.iterrows():

        unseen = [error for error in row["error_types"] if error not in covered_errors]

        if unseen:
            selected_indices.append(index)
            covered_errors.update(unseen)

    selected = dirty.loc[selected_indices]

    # Fill remaining rows
    remaining = dirty.drop(index=selected_indices)

    if len(selected) < sample_size:
        selected = pd.concat(
            [
                selected,
                remaining.head(sample_size - len(selected)),
            ]
        )

    return selected.head(sample_size)


def generate_business_summary(
    stats: DatasetStats,
    category_counter: Counter,
) -> str:
    """
    Generate an executive summary describing overall dataset quality.
    """
    if not category_counter:
        return (
            "No significant data quality issues were detected. "
            "The dataset is suitable for downstream analytics."
        )

    dominant_issue = category_counter.most_common(1)[0][0]

    impact = BUSINESS_IMPACT.get(
        dominant_issue,
        BUSINESS_IMPACT["Other"],
    )

    return (
        f"The dataset contains {stats.dirty_ratio:.1%} dirty records "
        f"with an overall health score of {stats.health_score}/100. "
        f"The most prevalent issue category is **{dominant_issue}**. "
        f"{impact}"
    )


def build_dataset_kpis(
    stats: DatasetStats,
    errors: Counter,
    categories: Counter,
    severity: Counter,
) -> dict[str, Any]:
    """
    High level KPIs for executive dashboards.
    """
    return {
        "Health Score": stats.health_score,
        "Dirty Ratio": round(stats.dirty_ratio * 100, 2),
        "Total Errors": int(sum(errors.values())),
        "Unique Error Types": int(len(errors)),
        "Most Common Issue": (errors.most_common(1)[0][0] if errors else "None"),
        "Largest Category": (categories.most_common(1)[0][0] if categories else "None"),
        "High Severity Issues": severity.get("High", 0),
        "Medium Severity Issues": severity.get("Medium", 0),
        "Low Severity Issues": severity.get("Low", 0),
    }


def print_profile_summary(result: ProfileResult) -> None:
    """
    Pretty console summary for quick debugging.
    """
    print("=" * 70)
    print(f"DATASET: {result.dataset}")
    print("=" * 70)
    print(f"Rows                : {result.stats.total_rows}")
    print(f"Dirty Rows          : {result.stats.dirty_rows}")
    print(f"Health Score        : {result.stats.health_score}")
    print(f"Total Errors        : {total_error_count(result)}")
    print(f"Top Error           : {dominant_error(result)}")
    print(f"Top Category        : {dominant_category(result)}")
    print(f"Worst Column        : {dominant_column(result)}")
    print("=" * 70)


# ---------------------------
# Main Function
# ---------------------------


def profile_dataset(
    dataset_name: str,
    file_path: str | Path,
) -> ProfileResult:
    """
    Profile a dirty dataset and return a structured ProfileResult.
    """
    # ---------------------------
    # Load Dataset
    # ---------------------------

    file_path = Path(file_path)
    df = pd.read_csv(file_path)
    df = parse_error_types(df)

    # ---------------------------
    # Dataset Stats
    # ---------------------------

    stats = build_dataset_stats(df)

    # ---------------------------
    # Error Stats
    # ---------------------------

    error_counter = count_errors(df)
    category_counter = build_category_counter(error_counter)
    severity_counter = build_severity_counter(error_counter)
    corrupted_columns = infer_corrupted_columns(error_counter)
    density = build_error_density(df)

    # ---------------------------
    # Profiling
    # ---------------------------

    numeric_profile = profile_numeric_columns(df)
    outlier_results = detect_outliers(df)
    dirty_examples = extract_dirty_examples(df)

    return ProfileResult(
        dataset=dataset_name,
        dataframe=df,
        stats=stats,
        error_counter=error_counter,
        category_counter=category_counter,
        severity_counter=severity_counter,
        numeric_profile=numeric_profile,
        outlier_results=outlier_results,
        corrupted_columns=corrupted_columns,
        error_density=density,
        dirty_examples=dirty_examples,
    )

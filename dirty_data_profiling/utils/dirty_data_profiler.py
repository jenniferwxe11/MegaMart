import ast
from collections import Counter
from pathlib import Path
from typing import Counter as CounterType

import pandas as pd

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────


def parse_error_types(df: pd.DataFrame) -> pd.DataFrame:

    if "error_types" not in df.columns:
        df["error_types"] = [[] for _ in range(len(df))]
        return df

    def _parse(x):
        if pd.isna(x):
            return []

        if isinstance(x, list):
            return x

        if isinstance(x, str):
            try:
                return ast.literal_eval(x)
            except Exception:
                return []

        return []

    parsed = [_parse(x) for x in df["error_types"]]

    df = df.copy()

    # force object dtype before assignment
    df["error_types"] = pd.Series(
        parsed,
        index=df.index,
        dtype="object",
    )

    return df


def count_errors(df: pd.DataFrame) -> Counter:
    """
    Count occurrences of all error types.
    """

    counter: CounterType[str] = Counter()

    for errors in df["error_types"]:
        counter.update(errors)

    return counter


def dirty_row_stats(df: pd.DataFrame) -> dict:
    """
    Compute overall dirty row statistics.
    """

    dirty_rows = df["error_types"].apply(len).gt(0).sum()

    return {
        "total_rows": len(df),
        "dirty_rows": dirty_rows,
        "clean_rows": len(df) - dirty_rows,
        "dirty_ratio": dirty_rows / len(df) if len(df) > 0 else 0,
    }


def error_density(df: pd.DataFrame) -> pd.Series:
    """
    Distribution of number of errors per row.
    """

    df.loc[:, "num_errors"] = df["error_types"].apply(len)

    return df["num_errors"].value_counts().sort_index()


def top_corrupted_columns(error_counter: Counter) -> Counter:
    """
    Infer most corrupted columns from error labels.
    """

    col_counter: CounterType[str] = Counter()

    for err, count in error_counter.items():

        tokens = err.split()

        if len(tokens) == 0:
            continue

        possible_col = tokens[-1]

        col_counter[possible_col] += count

    return col_counter


# ─────────────────────────────────────────────────────────────
# Numeric profiling
# ─────────────────────────────────────────────────────────────


def profile_numeric_columns(df: pd.DataFrame) -> dict:
    """
    Generate descriptive statistics for numeric columns.
    """
    numeric_cols = [
        c
        for c in df.select_dtypes(include=["number"]).columns
        if c not in {"num_errors"}
    ]

    results = {}

    for col in numeric_cols:

        series = df[col].dropna()

        if len(series) == 0:
            continue

        results[col] = {
            "mean": round(series.mean(), 2),
            "median": round(series.median(), 2),
            "std": round(series.std(), 2),
            "min": round(series.min(), 2),
            "max": round(series.max(), 2),
        }

    return results


# ─────────────────────────────────────────────────────────────
# Outlier detection
# ─────────────────────────────────────────────────────────────


def detect_outliers(df: pd.DataFrame) -> dict:
    """
    Detect outliers using IQR rule.
    """
    numeric_cols = [
        c
        for c in df.select_dtypes(include=["number"]).columns
        if c not in {"num_errors"}
    ]

    outlier_results = {}

    for col in numeric_cols:

        series = df[col].dropna()

        if len(series) < 10:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)

        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        outliers = series[(series < lower) | (series > upper)]

        outlier_results[col] = {
            "outlier_count": len(outliers),
            "outlier_ratio": round(len(outliers) / len(series), 4),
        }

    return outlier_results


# ─────────────────────────────────────────────────────────────
# Severity scoring
# ─────────────────────────────────────────────────────────────

SEVERITY_MAP = {
    "duplicate": "medium",
    "future": "high",
    "negative": "high",
    "missing": "medium",
    "formatting": "low",
    "whitespace": "low",
    "mismatch": "medium",
    "outlier": "high",
    "invalid": "high",
    "orphan": "high",
    "duplicate row": "medium",
}


def severity_breakdown(error_counter: Counter) -> dict:

    sev_counter: CounterType[str] = Counter()

    for err, count in error_counter.items():

        assigned = False

        for keyword, severity in SEVERITY_MAP.items():

            if keyword in err.lower():
                sev_counter[severity] += count
                assigned = True
                break

        if not assigned:
            sev_counter["unknown"] += count

    return dict(sev_counter)


# ─────────────────────────────────────────────────────────────
# Dataset health score
# ─────────────────────────────────────────────────────────────


def dataset_health_score(dirty_ratio: float) -> float:
    """
    Very simple health scoring.
    """

    return round(max(0, 100 - dirty_ratio * 100), 2)


# ─────────────────────────────────────────────────────────────
# Validation checks
# ─────────────────────────────────────────────────────────────


def run_validation_checks(df: pd.DataFrame) -> dict:
    """
    Rule-based validation checks.
    """

    checks = {}

    cols = set(df.columns)

    # Transactions
    if {"transaction_total", "cart_subtotal", "shipping_fee"}.issubset(cols):

        expected_total = (
            df["cart_subtotal"]
            - df.get("total_discount", 0)
            + df.get("shipping_fee", 0)
            - df.get("shipping_discount", 0)
        )

        mismatches = ((df["transaction_total"] - expected_total).abs() > 0.01).sum()

        checks["transaction_math_mismatch"] = int(mismatches)

    # Promotions
    if {"effective_start_date", "effective_end_date"}.issubset(cols):

        try:
            bad_dates = (
                pd.to_datetime(df["effective_end_date"])
                < pd.to_datetime(df["effective_start_date"])
            ).sum()

            checks["inverted_date_ranges"] = int(bad_dates)

        except Exception:
            pass

    # Negative prices
    price_cols = [c for c in df.columns if "price" in c.lower()]

    for col in price_cols:

        if pd.api.types.is_numeric_dtype(df[col]):

            checks[f"negative_{col}"] = int((df[col] < 0).sum())

    return checks


# ─────────────────────────────────────────────────────────────
# Main profiling function
# ─────────────────────────────────────────────────────────────


def profile_dataset(file_path, reports_dir="profiling/reports"):
    """
    Main reusable profiling function.
    """

    path = Path(file_path)

    dataset_name = path.stem

    df = pd.read_csv(file_path)

    df = parse_error_types(df)

    error_counter = count_errors(df)

    stats = dirty_row_stats(df)

    density = error_density(df)

    outliers = detect_outliers(df)

    severity = severity_breakdown(error_counter)

    validations = run_validation_checks(df)

    numeric_profile = profile_numeric_columns(df)

    health_score = dataset_health_score(stats["dirty_ratio"])

    os_report = []

    os_report.append("=" * 60)
    os_report.append(f"DATASET: {dataset_name}")
    os_report.append("=" * 60)

    os_report.append(f"Total rows: {stats['total_rows']}")

    os_report.append(f"Dirty rows: {stats['dirty_rows']}")

    os_report.append(f"Dirty ratio: {stats['dirty_ratio']:.2%}")

    os_report.append(f"Health score: {health_score}/100")

    os_report.append("\nTOP ERRORS")

    for err, count in error_counter.most_common(15):
        os_report.append(f"{err}: {count}")

    os_report.append("\nERROR DENSITY")

    for k, v in density.items():
        os_report.append(f"{k} errors -> {v} rows")

    os_report.append("\nSEVERITY BREAKDOWN")

    for sev, count in severity.items():
        os_report.append(f"{sev}: {count}")

    os_report.append("\nVALIDATION CHECKS")

    for k, v in validations.items():
        os_report.append(f"{k}: {v}")

    os_report.append("\nNUMERIC PROFILING")

    for col, num_stats in numeric_profile.items():
        os_report.append(
            f"{col}: "
            f"mean={num_stats['mean']}, "
            f"median={num_stats['median']}, "
            f"std={num_stats['std']}, "
            f"min={num_stats['min']}, "
            f"max={num_stats['max']}"
        )

    os_report.append("\nOUTLIERS")

    for col, info in outliers.items():
        os_report.append(
            f"{col}: "
            f"{info['outlier_count']} outliers "
            f"({info['outlier_ratio']:.2%})"
        )

    reports_dir = Path(reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)

    report_path = reports_dir / f"{dataset_name}_report.txt"

    with open(report_path, "w") as f:
        f.write("\n".join(os_report))

    print(f"  ✓ {dataset_name} → {dataset_name}_report.txt")

    return {
        "dataset": dataset_name,
        "total_rows": stats["total_rows"],
        "dirty_rows": stats["dirty_rows"],
        "dirty_ratio": round(stats["dirty_ratio"], 4),
        "health_score": health_score,
        "total_error_types": len(error_counter),
        "total_errors": sum(error_counter.values()),
        "top_error": (
            error_counter.most_common(1)[0][0] if len(error_counter) > 0 else None
        ),
        "numeric_columns": len(numeric_profile),
    }

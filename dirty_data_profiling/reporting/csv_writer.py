"""
Write profiling outputs as CSV files for downstream visualisation
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from dirty_data_profiling.profiler.dirty_data_profiler import (
    ProfileResult,
    build_summary_dict,
)

# ---------------------------
# CSV Functions
# ---------------------------


def write_error_summary(result: ProfileResult) -> pd.DataFrame:
    df = pd.DataFrame(
        {
            "error_type": list(result.error_counter.keys()),
            "count": list(result.error_counter.values()),
        }
    )

    return df.sort_values(
        by="count",
        ascending=False,
    )


def write_category_summary(result: ProfileResult) -> pd.DataFrame:
    df = pd.DataFrame(
        {
            "category": list(result.category_counter.keys()),
            "count": list(result.category_counter.values()),
        }
    )

    return df.sort_values(
        by="count",
        ascending=False,
    )


def write_severity_summary(result: ProfileResult) -> pd.DataFrame:
    df = pd.DataFrame(
        {
            "severity": list(result.severity_counter.keys()),
            "count": list(result.severity_counter.values()),
        }
    )

    return df.sort_values(
        by="count",
        ascending=False,
    )


def write_corrupted_columns(result: ProfileResult) -> pd.DataFrame:
    df = pd.DataFrame(
        {
            "column": list(result.corrupted_columns.keys()),
            "issues": list(result.corrupted_columns.values()),
        }
    )

    return df.sort_values(
        by="issues",
        ascending=False,
    )


def write_numeric_profile(result: ProfileResult) -> pd.DataFrame:
    rows = []
    for column, stats in result.numeric_profile.items():
        rows.append(
            {
                "column": column,
                **stats,
            }
        )

    return pd.DataFrame(rows)


def write_outlier_summary(result: ProfileResult) -> pd.DataFrame:
    rows = []
    for column, stats in result.outlier_results.items():
        rows.append(
            {
                "column": column,
                **stats,
            }
        )

    return pd.DataFrame(rows)


# ---------------------------
# Main Function
# ---------------------------


def write_profile_workbook(
    result: ProfileResult,
    output_directory: Path,
) -> None:
    """
    Generate a single Excel workbook containing all profiling
    outputs to reports/{dataset}/{dataset}_profile_data.xlsx
    """
    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    workbook_path = output_directory / f"{result.dataset}_profile_data.xlsx"

    with pd.ExcelWriter(workbook_path) as writer:

        pd.DataFrame([build_summary_dict(result)]).to_excel(
            writer,
            sheet_name="Dataset Summary",
            index=False,
        )

        write_error_summary(result).to_excel(
            writer,
            sheet_name="Error Types",
            index=False,
        )

        write_category_summary(result).to_excel(
            writer,
            sheet_name="Categories",
            index=False,
        )

        write_severity_summary(result).to_excel(
            writer,
            sheet_name="Severity",
            index=False,
        )

        write_corrupted_columns(result).to_excel(
            writer,
            sheet_name="Corrupted Columns",
            index=False,
        )

        write_numeric_profile(result).to_excel(
            writer,
            sheet_name="Numeric Profile",
            index=False,
        )

        write_outlier_summary(result).to_excel(
            writer,
            sheet_name="Outlier Summary",
            index=False,
        )

        result.dirty_examples.to_excel(
            writer,
            sheet_name="Dirty Examples",
            index=False,
        )

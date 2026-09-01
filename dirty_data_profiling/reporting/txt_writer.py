"""
Plain text audit report intended for developers and auditors to reports/{dataset}/report.txt
"""

from __future__ import annotations

from pathlib import Path

from dirty_data_profiling.profiler.dirty_data_profiler import (
    ProfileResult,
    dominant_category,
    dominant_error,
)


def write_text_report(
    result: ProfileResult,
    output_directory: Path,
):
    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    report = []
    report.append("=" * 80)
    report.append("MEGAMART DATA QUALITY REPORT")
    report.append("=" * 80)
    report.append("")

    report.append(f"Dataset               : {result.dataset}")
    report.append(f"Total Rows            : {result.stats.total_rows}")
    report.append(f"Dirty Rows            : {result.stats.dirty_rows}")
    report.append(f"Clean Rows            : {result.stats.clean_rows}")
    report.append(f"Dirty Ratio           : {result.stats.dirty_ratio:.2%}")
    report.append(f"Health Score          : {result.stats.health_score}")

    report.append("")
    report.append("-" * 80)
    report.append("")

    report.append("BUSINESS OVERVIEW")
    report.append("")

    report.append(f"The dominant issue category is " f"{dominant_category(result)}.")

    report.append(f"The most common detected error is " f"{dominant_error(result)}.")

    report.append("")
    report.append("-" * 80)
    report.append("")

    # --- Error Summary ---
    report.append("TOP ERROR TYPES")
    report.append("")

    if result.error_counter:
        for error, count in result.error_counter.most_common():
            report.append(f"{error:<45} {count:>6}")
    else:
        report.append("No errors detected.")

    report.append("")
    report.append("-" * 80)
    report.append("")

    # --- Category Summary ---
    report.append("ERROR CATEGORIES")
    report.append("")

    for category, count in result.category_counter.items():
        report.append(f"{category:<35} {count:>8}")

    report.append("")
    report.append("-" * 80)
    report.append("")

    # --- Severity Summary ---
    report.append("SEVERITY BREAKDOWN")
    report.append("")

    for severity, count in result.severity_counter.items():
        report.append(f"{severity:<20} {count}")

    report.append("")
    report.append("-" * 80)
    report.append("")

    # --- Severity Summary ---
    report.append("NUMERIC PROFILE")
    report.append("")

    if result.numeric_profile:
        for column, stats in result.numeric_profile.items():
            report.append(column)
            for metric, value in stats.items():
                report.append(f"    {metric:<12}: {value}")
            report.append("")
    else:
        report.append("No numeric columns.")

    report.append("")
    report.append("-" * 80)
    report.append("")

    # --- Outlier Summary ---
    report.append("OUTLIER SUMMARY")
    report.append("")

    if result.outlier_results:
        for column, stats in result.outlier_results.items():
            report.append(column)
            report.append(f"    Outliers : {stats['outlier_count']}")
            report.append(f"    Ratio    : {stats['outlier_ratio']:.2%}")
            report.append(f"    Lower    : {stats['lower_bound']}")
            report.append(f"    Upper    : {stats['upper_bound']}")
            report.append("")
    else:
        report.append("No outlier analysis.")

    report.append("")
    report.append("-" * 80)
    report.append("")

    # --- Dirty Examples ---
    report.append("DIRTY SAMPLE RECORDS")
    report.append("")

    if len(result.dirty_examples):
        report.append(result.dirty_examples.to_string(index=False))
    else:
        report.append("No dirty records detected.")

    report.append("")
    report.append("=" * 80)

    # --- Save File ---
    with open(
        output_directory / "report.txt",
        "w",
        encoding="utf-8",
    ) as f:

        f.write("\n".join(report))

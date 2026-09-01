"""
Generate a business friendly Markdown summary to reports/{dataset}/business_summary.md
"""

from __future__ import annotations

from pathlib import Path

from dirty_data_profiling.config.constants import (
    BUSINESS_IMPACT,
    CLEANING_RULES,
    DBT_RECOMMENDATIONS,
)
from dirty_data_profiling.profiler.dirty_data_profiler import (
    ProfileResult,
    generate_business_summary,
)


def write_business_summary(
    result: ProfileResult,
    output_directory: Path,
) -> None:
    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    business_summary = generate_business_summary(
        result.stats,
        result.category_counter,
    )

    lines = []

    # --- Title ---
    lines.append(f"# {result.dataset.replace('_', ' ').title()} Dataset")
    lines.append("")

    # --- Executive Summary ---
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(business_summary)
    lines.append("")

    # --- Dataset Health ---
    lines.append("## Dataset Health")
    lines.append("")

    lines.append("| Metric | Value |")
    lines.append("|--------|------:|")
    lines.append(f"| Total Rows | {result.stats.total_rows:,} |")
    lines.append(f"| Clean Rows | {result.stats.clean_rows:,} |")
    lines.append(f"| Dirty Rows | {result.stats.dirty_rows:,} |")
    lines.append(f"| Dirty Ratio | {result.stats.dirty_ratio:.2%} |")
    lines.append(f"| Health Score | {result.stats.health_score} / 100 |")
    lines.append("")

    # --- Major Issues ---
    lines.append("## Major Data Quality Issues")
    lines.append("")

    if not result.category_counter:
        lines.append("No data quality issues were detected")
    else:
        for category, count in result.category_counter.most_common():
            impact = BUSINESS_IMPACT.get(
                category,
                BUSINESS_IMPACT["Other"],
            )

            cleaning = CLEANING_RULES.get(
                category,
                "Manual review required.",
            )

            recommendation = DBT_RECOMMENDATIONS.get(
                category,
                "Manual investigation.",
            )

            lines.append(f"### {category}")
            lines.append("")

            lines.append(f"**Occurrences:** {count}")
            lines.append("")

            lines.append("**Business Impact**")
            lines.append("")
            lines.append(impact)
            lines.append("")

            lines.append("**Recommended Cleaning Strategy**")
            lines.append("")
            lines.append(cleaning)
            lines.append("")

            lines.append("**Suggested dbt Implementation**")
            lines.append("")
            lines.append(f"`{recommendation}`")
            lines.append("")

    # --- Conclusion ---
    lines.append("## Conclusion")
    lines.append("")
    lines.append(
        "The identified data quality issues support the need for the "
        "subsequent dbt transformation and validation pipeline. "
        "Implementing the recommended cleaning strategies will improve "
        "data reliability and provide a stronger foundation for "
        "analytics, reporting and downstream machine learning models."
    )

    output_file = output_directory / "business_summary.md"

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as file:
        file.write("\n".join(lines))

"""
Generate executive level reports across every dataset.
"""

import json
from pathlib import Path

import pandas as pd

# ---------------------------
# Helper Function
# ---------------------------


def _summary_dataframe(results):
    rows = []
    for r in results:
        rows.append(
            {
                "dataset": r.dataset,
                "total_rows": r.stats.total_rows,
                "dirty_rows": r.stats.dirty_rows,
                "dirty_ratio": r.stats.dirty_ratio,
                "health_score": r.stats.health_score,
                "total_errors": sum(r.error_counter.values()),
                "top_error": (
                    r.error_counter.most_common(1)[0][0] if r.error_counter else None
                ),
            }
        )

    df = pd.DataFrame(rows)
    df = df.sort_values(
        "dirty_ratio",
        ascending=False,
    )
    return df


# ---------------------------
# Main Function
# ---------------------------


def write_global_reports(
    results,
    reports_directory: Path,
):
    reports_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary = _summary_dataframe(results)

    # --- Summary ---
    summary.to_csv(
        reports_directory / "summary_report.csv",
        index=False,
    )

    # --- Dataset Ranking ---
    rankings = summary.copy()
    rankings["rank"] = (
        rankings["dirty_ratio"]
        .rank(
            method="dense",
            ascending=False,
        )
        .astype(int)
    )
    rankings.to_csv(
        reports_directory / "dataset_rankings.csv",
        index=False,
    )

    # --- Dashboard JSON ---
    dashboard = {
        "datasets_profiled": len(summary),
        "average_health_score": round(
            summary["health_score"].mean(),
            2,
        ),
        "average_dirty_ratio": round(
            summary["dirty_ratio"].mean(),
            4,
        ),
        "worst_dataset": summary.iloc[0]["dataset"],
        "best_dataset": summary.iloc[-1]["dataset"],
        "total_errors": int(summary["total_errors"].sum()),
        "highest_error_dataset": summary.loc[summary["total_errors"].idxmax()][
            "dataset"
        ],
    }

    with open(
        reports_directory / "summary_dashboard.json",
        "w",
        encoding="utf8",
    ) as f:
        json.dump(
            dashboard,
            f,
            indent=4,
        )

    # --- Executive Markdown ---
    md = []

    md.append("# MegaMart Data Quality Executive Summary\n")

    md.append(f"A total of **{len(summary)} datasets** " "were analysed.\n")

    md.append(
        f"The average data quality score was "
        f"**{dashboard['average_health_score']}**.\n"
    )

    md.append(
        f"The dataset requiring the greatest "
        f"cleaning effort is "
        f"**{dashboard['worst_dataset']}**.\n"
    )

    md.append(
        f"A total of **{dashboard['total_errors']}** "
        "data quality issues were detected.\n"
    )

    md.append(
        "The identified issues provide the basis "
        "for the subsequent dbt cleaning pipeline."
    )

    with open(
        reports_directory / "overall_business_summary.md",
        "w",
        encoding="utf8",
    ) as f:
        f.write("\n".join(md))

from pathlib import Path

import pandas as pd

from data_ingestion.config.bigquery_config import TABLES
from dirty_data_profiling.config.constants import REPORTS_DIR
from dirty_data_profiling.profiler.dirty_data_profiler import (
    build_summary_dict,
    profile_dataset,
)
from dirty_data_profiling.reporting.global_writer import (
    write_global_reports,
)
from dirty_data_profiling.reporting.report_writer import (
    write_all_dataset_reports,
)


def run_profiling():

    summaries = []

    print("=" * 60)
    print("MegaMart Dirty Data Profiler")
    print("=" * 60)

    print(f"\nOUTPUT DIRECTORY: {REPORTS_DIR}")
    print("\nGENERATING PROFILING REPORTS:")

    for table, config in TABLES.items():

        file_path = Path(config["csv"])

        if not file_path.exists():
            print(f"Missing: {file_path}")
            continue

        try:

            summary = profile_dataset(dataset_name=table, file_path=file_path)

            summaries.append(summary)

        except Exception as e:

            print(f"Failed profiling {file_path}")
            print(e)

    write_all_dataset_reports(summaries, REPORTS_DIR)
    write_global_reports(summaries, REPORTS_DIR)

    # Save overall summary
    summary_df = pd.DataFrame([build_summary_dict(result) for result in summaries])
    summary_df = summary_df.sort_values(
        by="dirty_ratio",
        ascending=False,
    )
    output_path = Path(REPORTS_DIR) / "summary_report.csv"
    summary_df.to_csv(output_path, index=False)

    print("\nSUMMARY:")
    print(summary_df)

    print("=" * 60)
    print("✓ All Dirty Tables Profiled Successfully")
    print("=" * 60)


if __name__ == "__main__":
    run_profiling()

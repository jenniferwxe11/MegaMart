from pathlib import Path

import pandas as pd

from dirty_data_profiling.config.constants import DIRTY_DIR, FILES, REPORTS_DIR
from dirty_data_profiling.utils.dirty_data_profiler import profile_dataset


def run_profiling():

    summaries = []

    print("=" * 60)
    print("MegaMart Dirty Data Profiler")
    print("=" * 60)

    print(f"\nOUTPUT DIRECTORY: {REPORTS_DIR}")
    print("\nGENERATING PROFILING REPORTS:")

    for filename in FILES:

        file_path = Path(DIRTY_DIR) / filename

        if not file_path.exists():
            print(f"Missing: {filename}")
            continue

        try:

            summary = profile_dataset(file_path=file_path, reports_dir=REPORTS_DIR)

            summaries.append(summary)

        except Exception as e:

            print(f"Failed profiling {filename}")
            print(e)

    # Save overall summary
    summary_df = pd.DataFrame(summaries)

    summary_df = summary_df.sort_values(by="dirty_ratio", ascending=False)

    output_path = Path(REPORTS_DIR) / "summary_report.csv"

    summary_df.to_csv(output_path, index=False)

    print("\nSUMMARY:")

    print(summary_df)

    print("\n")
    print("=" * 60)
    print("✓ All Dirty Tables Profiled Successfully")
    print("=" * 60)


if __name__ == "__main__":
    run_profiling()

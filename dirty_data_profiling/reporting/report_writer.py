"""
Orchestrates generation of all dataset level reports.
"""

from pathlib import Path

from dirty_data_profiling.reporting.csv_writer import write_profile_workbook
from dirty_data_profiling.reporting.json_writer import write_metrics_json
from dirty_data_profiling.reporting.markdown_writer import write_business_summary
from dirty_data_profiling.reporting.txt_writer import write_text_report


def write_dataset_reports(
    result,
    reports_directory: Path,
):
    """
    Generate every report for a single dataset.
    """
    dataset_directory = reports_directory / result.dataset
    dataset_directory.mkdir(
        parents=True,
        exist_ok=True,
    )
    write_profile_workbook(result, dataset_directory)
    write_metrics_json(result, dataset_directory)
    write_business_summary(result, dataset_directory)
    write_text_report(result, dataset_directory)


def write_all_dataset_reports(
    results,
    reports_directory: Path,
):
    """
    Generate reports for every dataset.
    """
    for result in results:
        write_dataset_reports(
            result,
            reports_directory,
        )

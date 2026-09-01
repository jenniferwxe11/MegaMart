"""
Write profiling metrics to reports/{dataset}/metrics.json
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from dirty_data_profiling.profiler.dirty_data_profiler import (
    ProfileResult,
    build_dataset_kpis,
    generate_business_summary,
)


def json_converter(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    raise TypeError(f"{type(obj)} is not JSON serializable")


def write_metrics_json(
    result: ProfileResult,
    output_directory: Path,
) -> None:
    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    metrics = {
        "dataset": result.dataset,
        "overview": {
            "total_rows": result.stats.total_rows,
            "dirty_rows": result.stats.dirty_rows,
            "clean_rows": result.stats.clean_rows,
            "dirty_ratio": result.stats.dirty_ratio,
            "health_score": result.stats.health_score,
        },
        "kpis": build_dataset_kpis(
            stats=result.stats,
            errors=result.error_counter,
            categories=result.category_counter,
            severity=result.severity_counter,
        ),
        "error_counter": dict(result.error_counter),
        "category_counter": dict(result.category_counter),
        "severity_counter": dict(result.severity_counter),
        "numeric_profile": result.numeric_profile,
        "outliers": result.outlier_results,
        "business_summary": generate_business_summary(
            result.stats,
            result.category_counter,
        ),
    }

    output_file = output_directory / "metrics.json"

    with open(output_file, "w") as f:
        json.dump(
            metrics,
            f,
            indent=4,
            default=json_converter,
        )

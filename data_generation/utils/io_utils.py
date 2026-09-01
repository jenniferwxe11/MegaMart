import os
from pathlib import Path

import pandas as pd

from data_generation.config.constants import RAW_DIR, REGIONS_TO_AREAS


def save(df, filename):
    path = os.path.join(RAW_DIR, filename)
    df.to_csv(path, index=False)
    print(f"  ✓ {filename}  ({len(df):,} rows)")


def export_region_area_seed() -> None:
    """
    Export the region area mapping as a dbt seed.
    """
    output_path = Path("dbt/seeds/region_area_mapping.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = [
        {"region": region, "area": area}
        for region, areas in REGIONS_TO_AREAS.items()
        for area in areas
    ]

    (
        pd.DataFrame(rows)
        .sort_values(["region", "area"])
        .to_csv(output_path, index=False)
    )

    print(f"  ✓ region_area_mapping.csv exported to {output_path}")

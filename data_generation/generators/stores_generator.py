import random
from typing import Any

import pandas as pd

from data_generation.config.generation_config import NUM_STORES
from data_generation.config.stores_config import (
    MALL_TO_AREA,
    STORE_TYPE,
)
from data_generation.context.generation_context import GenerationContext
from data_generation.registry import register
from data_generation.services.region_areas.region_area_service import (
    get_random_region_area,
    get_region_from_area,
)
from data_generation.utils.io_utils import save


@register("stores_generator")
def stores_generator(ctx: GenerationContext):
    # ---------------------------
    # Storage
    # ---------------------------

    stores: list[dict[str, Any]] = []
    available_malls = MALL_TO_AREA.copy()

    # ---------------------------
    # Generation
    # ---------------------------

    for i in range(1, NUM_STORES + 1):
        store_id = f"STOR{i:03d}"

        # Ensure a realistic mix of store types
        store_type = random.choices(
            list(STORE_TYPE.keys()), weights=list(STORE_TYPE.values()), k=1
        )[0]

        if store_type in ("Mall", "Flagship"):
            mall = random.choice(list(available_malls.keys()))
            area = available_malls[mall]
            region = get_region_from_area(ctx, area)
            if store_type == "Mall":
                store_name = f"MegaMart {mall}"
            elif store_type == "Flagship":
                store_name = f"MegaMart {mall} - Flagship Store"
            del available_malls[mall]

        elif store_type == "Neighbourhood":
            block_no = random.randint(100, 999)
            region, area = get_random_region_area(ctx)
            store_name = f"MegaMart Blk {block_no} {area} Street"

        else:
            raise ValueError(f"Unknown store_type: {store_type}")

        # Store Record
        stores.append(
            {
                "store_id": store_id,
                "store_name": store_name,
                "area": area,
                "region": region,
                "store_type": store_type,
            }
        )

        i += 1

    # Online Store Record
    stores.append(
        {
            "store_id": f"STOR{NUM_STORES + 1:03d}",
            "store_name": "MegaMart Online",
            "area": "Nationwide",
            "region": "Nationwide",
            "store_type": "Online",
        }
    )

    # ---------------------------
    # Export to CSV
    # ---------------------------

    save(pd.DataFrame(stores), "stores_raw.csv")

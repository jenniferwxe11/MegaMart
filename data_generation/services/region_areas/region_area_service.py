import random

from data_generation.config.constants import REGIONS_TO_AREAS


def get_random_region_area(ctx):
    """
    Retrieves a random region and area
    """
    region = random.choice(ctx.region_areas.regions)
    areas = REGIONS_TO_AREAS.get(region)

    if not areas:
        raise ValueError(f"No areas found for region {region}")

    area = random.choice(areas)

    return region, area


def get_region_from_area(ctx, area):
    """
    Retrieves region from chosen area.
    """
    return ctx.region_areas.area_region_map.get(area)

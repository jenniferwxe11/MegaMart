import random


def get_random_region_area(ctx):
    """
    Retrieves a random region and area
    """
    region = random.choice(list(ctx.region_areas.region_area_map.keys()))
    area = random.choice(ctx.region_areas.region_area_map[region])
    return region, area


def get_region_from_area(ctx, area):
    """
    Retrieves region from chosen area.
    """
    return ctx.region_areas.area_region_map.get(area)

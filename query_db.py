import json
import argparse
import os

import numpy as np
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='query-db')
    parser.add_argument('-w', '--world-file', required=True)
    parser.add_argument('--longitude', required=True, type=float)
    parser.add_argument('--latitude', required=True, type=float)
    args = parser.parse_args()

    point = Point(args.longitude, args.latitude)

    #
    # Open world file and look if our point is inside a polygon.
    # Each polygon in the world file will point to a region specific file
    # This will save all matched regions in an array
    #

    with open(args.world_file, 'r') as file:
        world = json.load(file)

    regions = []
    for data, region, admin_levels in world:
        polygon = Polygon(data)
        with np.errstate(invalid="ignore"):
            if polygon.contains(point):
                regions.append((region, admin_levels))

    #
    # Loop over the matched regions
    #

    print(regions)

    response = []
    for region, admin_levels in regions:
        path_dir = os.path.dirname(args.world_file)
        region_file_full = f"{path_dir}/{region}"
        region_file_simple = region_file_full.replace(".json.db", ".simplified.json.db")

        if os.path.exists(region_file_simple):
            region_file = region_file_simple
        else:
            region_file = region_file_full

        with open(region_file, 'r') as file:
            region_data = json.load(file)

        for name, level, data in region_data:
            polygon = Polygon(data)
            with np.errstate(invalid="ignore"):
                if polygon.contains(point):
                    if level == admin_levels[0]:
                        admin_level1 = name
                    elif level == admin_levels[1]:
                        admin_level2 = name
                    elif len(admin_levels) > 2 and level == admin_levels[2]:
                        admin_level3 = name

        response.append({"admin1": admin_level1, "admin2": admin_level2, "admin3": admin_level3})

    print(response)

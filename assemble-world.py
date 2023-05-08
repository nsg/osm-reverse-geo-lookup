import os
import json
import glob
import argparse

from shapely.geometry.polygon import Polygon

def process(folder):
    world_mappings = []
    for f in glob.glob(f"{folder}/*.json.db"):
        path_name = os.path.basename(f)
        polygons = json.load(open(f))

        # Collect a sorted list of admin levels
        admin_levels = []
        for polygon in polygons:
            admin_levels.append(polygon[1])
        admin_levels = list(set(admin_levels))
        admin_levels.sort()

        print(f"Process {f}, use admin_level {admin_levels[0]}")
        for polygon in polygons:
            _, l, d = polygon
            if l == admin_levels[0]:
                world_mappings.append((d, path_name, admin_levels))

    return world_mappings


def save(path, data):
    with open(path, "w") as outfile:
        outfile.write(json.dumps(data))

parser = argparse.ArgumentParser(prog='assemble-world')
parser.add_argument('input')
parser.add_argument('outputprefix')
args = parser.parse_args()

data = process(args.input)

save(f"{args.outputprefix}.json.db", data)

import json
import glob
import argparse

from shapely.geometry.polygon import Polygon

def process(folder):
    for f in glob.glob(f"{folder}/*.json.db"):
        polygons = json.load(open(f))

        # Find country admin level, this is probably 2
        admin1_level = 10
        for polygon in polygons:
            _, l, d = polygon
            if int(l) < admin1_level:
                admin1_level = int(l)

        if admin1_level == 10:
            raise Exception(f"Unable to detect admin levels from file {f}")

        world_mappings = []
        world_mappings_simplify = []
        for polygon in polygons:
            _, l, d = polygon
            if int(l) == admin1_level:
                world_mappings.append((d, f))
                world_mappings_simplify.append(list(Polygon(d).simplify(0.05).exterior.coords))

    return world_mappings, world_mappings_simplify


def save(path, data):
    with open(path, "w") as outfile:
        outfile.write(json.dumps(data))

parser = argparse.ArgumentParser(prog='assemble-world')
parser.add_argument('input')
parser.add_argument('outputprefix')
args = parser.parse_args()

data, simplified_data = process(args.input)

save(f"{args.outputprefix}.json.db", data)
save(f"{args.outputprefix}.simplified.json.db", simplified_data)

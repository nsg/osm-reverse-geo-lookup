import json
import glob
import argparse
import os

from shapely.geometry.polygon import Polygon

parser = argparse.ArgumentParser(prog='simplify')
parser.add_argument('folder')
args = parser.parse_args()

for f in glob.glob(f"{args.folder}/*.json.db"):
    path_dir = os.path.dirname(f)
    path_name = os.path.basename(f)
    path_simple = path_name.replace(".json.db", ".simplified.json.db")
    out_path = f"{path_dir}/{path_simple}"

    out = []
    data = json.load(open(f))
    for r in data:
        rs = list(Polygon(r[2]).simplify(0.05).exterior.coords)
        out.append([r[0], r[1], rs])

    with open(out_path, "w") as outfile:
        outfile.write(json.dumps(out))

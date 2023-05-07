import sys
import os
import json
import argparse

import osmium

# OSM_PBF = "sweden-latest.osm.pbf"
# DB_FILE = "sweden.db"
# OSM_PBF = "Stockholm.osm.pbf"
# DB_FILE = "stockholm.db"

def is_number(str):
    try:
        int(str)
    except ValueError:
        return False
    return True

class WayHandler(osmium.SimpleHandler):
    def __init__(self, lookup_ways):
        super().__init__()
        self.ways = {}
        self.lookup_ways = lookup_ways

    def way(self, w):
        if w.id in self.lookup_ways:
            self.ways[w.id] = []
            for node in w.nodes:
               self.ways[w.id].append(node.location)

class RelationHandler(osmium.SimpleHandler):
    def __init__(self, admin_level1, admin_level2, admin_level3):
        super().__init__()
        self.boundaries = []
        self.lookup_ways = []
        self.admin_level1 = admin_level1
        self.admin_level2 = admin_level2
        self.admin_level3 = admin_level3

    def relation(self, r):
        if r.tags.get("type") != "boundary":
            return
        
        if r.tags.get("boundary") != "administrative":
            return

        admin_level = r.tags.get("admin_level")
        if admin_level in [self.admin_level1, self.admin_level2, self.admin_level3]:
            ways = []
            for m in r.members:
                ways.append(m.ref)
                self.lookup_ways.append(m.ref)
            if r.tags.get("name:en"):
                b_name = r.tags.get("name:en")
            else:
                b_name = r.tags.get("name")
            self.boundaries.append((b_name, admin_level, ways))
            print(f"Found {b_name} admin_level {admin_level}")

class AdminLevelsHandler(osmium.SimpleHandler):
    def __init__(self, alfa, beta, gamma):
        super().__init__()
        self._alfa = alfa
        self._beta = beta
        self._gamma = gamma

        if is_number(alfa):
            self.alfa = int(alfa)
        else:
            self.alfa = None

        if is_number(beta):
            self.beta = int(beta)
        else:
            self.beta = None

        if is_number(gamma):
            self.gamma = int(gamma)
        else:
            self.gamma = None

    def relation(self, r):
        if r.tags.get("type") != "boundary":
            return
        
        if r.tags.get("boundary") != "administrative":
            return
        
        if r.tags.get("name") == self._alfa or r.tags.get("name:en") == self._alfa:
            self.alfa = r.tags.get("admin_level")

        if r.tags.get("name") == self._beta or r.tags.get("name:en") == self._beta:
            self.beta = r.tags.get("admin_level")

        if r.tags.get("name") == self._gamma or r.tags.get("name") == self._gamma:
            self.gamma = r.tags.get("admin_level")


def main(args):

    print("Looking for administrative levels ...")
    al = AdminLevelsHandler(args.alfa, args.beta, args.gamma)
    al.apply_file(args.osm_pbf)
    print(f"Top administrative level (alpha): {al.alfa} ({args.alfa})")
    print(f"Middle administrative level (beta): {al.beta} ({args.beta})")
    print(f"Lower administrative level (gamma): {al.gamma} ({args.gamma})")

    if not (al.alfa and al.beta and al.gamma):
        print("Not all administrative levels where found!")
        sys.exit(1)

    print("Looking for relations...")
    osm_b = RelationHandler(al.alfa, al.beta, al.gamma)
    osm_b.apply_file(args.osm_pbf, locations=True, idx='flex_mem')

    print(f"Processing {args.osm_pbf}")
    print(f"I have found {len(osm_b.boundaries)} boundaries refering to {len(osm_b.lookup_ways)} ways ({len(set(osm_b.lookup_ways))} unique).")
    print(f"I will scan {args.osm_pbf} to collect these ways with coordinates")

    print("Looking for ways and nodes with coordinates...")
    osm_w = WayHandler(osm_b.lookup_ways)
    osm_w.apply_file(args.osm_pbf, locations=True)

    print(f"I found {len(osm_w.ways)} unique matching ways in {args.osm_pbf}")

    coords = []

    for boundary_name, admin_level, boundary_data in osm_b.boundaries:
        """ Loop over boundaries, like Huvudsta """

        data = []
        for r in boundary_data:
            """ Loop over the boundaries relations """

            for c in osm_w.ways.get(r, []):
                """ Loop over each relations ways node locations """

                data.append((c.y / 10000000.0, c.x / 10000000.0))

        print(f"Found {boundary_name} ({admin_level})")
        coords.append((boundary_name, admin_level, data))

    with open(args.out_db, "w") as outfile:
        outfile.write(json.dumps(coords))

    print(f"Written state to {args.out_db}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='build_db',
                                     description='Build a reverse GEO DB from OSM data')
    parser.add_argument('osm_pbf')
    parser.add_argument('out_db')
    parser.add_argument('--alfa')
    parser.add_argument('--beta')
    parser.add_argument('--gamma')

    args = parser.parse_args()
    main(args)

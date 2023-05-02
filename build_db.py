import sys
import os
import json
import argparse

import osmium

# OSM_PBF = "sweden-latest.osm.pbf"
# DB_FILE = "sweden.db"
# OSM_PBF = "Stockholm.osm.pbf"
# DB_FILE = "stockholm.db"

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
        super().__init__(admin_level1, admin_level2, admin_level3)
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
            self.boundaries.append((r.tags.get("name"), admin_level, ways))
            print(f"Found {r.tags.get('name')} admin_level {admin_level}")


def main(args):

    osm_b = RelationHandler()
    osm_b.apply_file(args.osm_pbf, locations=True, idx='flex_mem')

    print(f"Processing {args.osm_pbf}")
    print(f"I have found {len(osm_b.boundaries)} boundaries refering to {len(osm_b.lookup_ways)} ways ({len(set(osm_b.lookup_ways))} unique).")
    print(f"I will scan {args.osm_pbf} to collect these ways with coordinates")

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
    parser.add_argument('-1', help="Admin level 1")
    parser.add_argument('-2', help="Admin level 2")
    parser.add_argument('-3', help="Admin level 3")

    args = parser.parse_args()
    main(args)

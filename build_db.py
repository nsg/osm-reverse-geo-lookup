import sys
import json

import osmium

# OSM_PBF = "sweden-latest.osm.pbf"
# DB_FILE = "sweden.db"
# OSM_PBF = "Stockholm.osm.pbf"
# DB_FILE = "stockholm.db"
OSM_PBF = sys.argv[1]
DB_FILE = sys.argv[2]

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
    def __init__(self):
        super().__init__()
        self.boundaries = []
        self.lookup_ways = []

    def relation(self, r):
        if r.tags.get("type") != "boundary":
            return
        
        if r.tags.get("boundary") != "administrative":
            return

        if r.tags.get("admin_level") != "7":
            return

        ways = []
        for m in r.members:
            ways.append(m.ref)
            self.lookup_ways.append(m.ref)
        self.boundaries.append((r.tags.get("name"), ways))


def main():

    osm_b = RelationHandler()
    osm_b.apply_file(OSM_PBF, locations=True, idx='flex_mem')

    print(f"Processing {OSM_PBF}")
    print(f"I have found {len(osm_b.boundaries)} boundaries refering to {len(osm_b.lookup_ways)} ways ({len(set(osm_b.lookup_ways))} unique).")
    print(f"I will scan {OSM_PBF} to collect these ways with coordinates")

    osm_w = WayHandler(osm_b.lookup_ways)
    osm_w.apply_file(OSM_PBF, locations=True)

    print(f"I found {len(osm_w.ways)} unique matching ways in {OSM_PBF}")

    coords = []

    for boundary_name, boundary_data in osm_b.boundaries:
        """ Loop over boundaries, like Huvudsta """

        data = []
        for r in boundary_data:
            """ Loop over the boundaries relations """

            for c in osm_w.ways.get(r, []):
                """ Loop over each relations ways node locations """

                data.append((c.y / 10000000.0, c.x / 10000000.0))

        print(f"Found {boundary_name}")
        coords.append((boundary_name, data))

    with open(DB_FILE, "w") as outfile:
        outfile.write(json.dumps(coords))

    print(f"Written state to {DB_FILE}")

if __name__ == '__main__':
    main()

import sys
import json

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

#DB_FILE = "stockholm.db"
DB_FILE = "sweden.db.json"

def comp(shape: list, point: tuple) -> bool:
    polygon = Polygon(shape)
    point = Point(point[0], point[1])

    return polygon.contains(point)

if __name__ == '__main__':

    point = (sys.argv[1], sys.argv[2])

    with open(DB_FILE, 'r') as file:
        db = json.load(file)

    for name, data in db:
        if comp(data, point):
            print(name)

# OSM Reverse GEO Lookup

This project parses OpenStreetMap map data to build a database for reverse geographical lookups. In short, you can use this data to turn `{"latitude": 59.3371, "longitude": 17.9142}` to `{"admin1": "Sverige", "admin2": "Stockholms län", "admin3": "Stockholms kommun"}`.

## Use the database

There is a sample implementation in `query_db.py`. If you like to implement a solution of your own you need to:

1. Use `world.json.db` to find which database file the coordinates belong to
2. Query the country specific database to lookup more granular administrative areas

The database files contains lists of lists of polygons formated like this:

```
[
    [ <name>, <admin_level>, <polygon> ], ...
]
```

`<name>` is the name, for example "Stockholms län". `<admin_level>` is an numerical value between 2 and 10. A higher value is a more specific (a more zoomed in) match. Typically expect 3-4 matches of varying levels. `<polygon>` is a list of coordinates like `[59.4537516, 11.760087], [59.4581841, 11.7599343], [59.4588745, 11.7597151], ...`

## Build the database

`build_db.py` is used to parse an extracts of OSM data. I use extracts from https://download.geofabrik.de to generate the json.db-files. `assemble-world.py` is used to generate `world.json.db`.

The "simplified" files are files with reduced polygon counts. This reduces the file sizes and speeds things up, but with the drawback of lost resolution at polygon borders. It's quite safe to try to use the simplified files first, and fall back to the larger file.

## License

The code is licensed under the MIT License.

The reverse geo database is made available under the Open Database License: http://opendatacommons.org/licenses/odbl/1.0/. Any rights in individual contents of the database are licensed under the Database Contents License: http://opendatacommons.org/licenses/dbcl/1.0/

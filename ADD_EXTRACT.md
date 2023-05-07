# Add a Extract

## 1. Identify a good extract

Go to https://download.geofabrik.de/ and browse the sub regions. Try to limit the file size below 1GB. Geofabrik is good to split larger regions in to even smaller extracts.

## 2. Find good administrative levels for the extract

Use the "Query features" button on https://www.openstreetmap.org to inspect the map. Look for "Enclosing features" like "Country Boundary", "Municipality Boundary" or any boundary that makes sense for the country in questions. The boundary **must** have `type: boundary`, `boundary: administrative` and an `admin_level` to be detected.

Identify three appropriate levels, alfa, beta and gamma. Alfa is least specific, probably the entire country (most likely `admin_level: 2`). Beta should be a region of the country and gamma is the most specific. Level 4 and 7 is common but different countries has different traditions how to number things.

When I added Norway I queried a suburb of Bergen (I have found that larger cities like Oslo has more data and it's easier to find good administrative regions with smaller cities). I got the data below and picked "Norge", "Vestland" and "Bergen".

| Place | Name | Type | Boundary | Admin Level | Picked |
| ----- | ---- | ---- | -------- | ----------- | ------ |
| Neighbourhood | Kalfarlien | - | - | - | |
| Neighbourhood | Kalfaret | multipolygon | - | - | |
| Village Boundary | Bergenhus | boundary | administrative | 9 | |
| Municipality Boundary | Bergen | boundary | administrative | 7 | gamma |
| Relation | Hordaland | multipolygon | - | - | |
| State Boundary | Vestland | boundary | administrative | 4 | beta |
| Administrative Boundary | Norway | boundary | administrative | - | |
| Country Boundary | Norway | boundary | administrative | 2 | alfa |

## 3. Add the extract

Fork the repository, modify `.github/workflows/generate-extracts.yaml` and open a PR. If you are not that familiar how to do this, feel free to open an issue instead. The above example looks like this:

```yaml
- country: "Norway"
  alfa: "Norge"
  beta: "Vestland"
  gamma: "Bergen"
  osm_source_file: "https://download.geofabrik.de/europe/norway-latest.osm.pbf"
```

`country` should be the English name of the country. `Alfa`, `beta` and `gamma` needs to refer to the tag `name` (local name, like Norge) or the tag `name:en` (english name, like Norway).

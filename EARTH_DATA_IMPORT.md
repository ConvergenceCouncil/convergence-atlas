# CONVERGENCE — Earth geographic data ingestion

This is the **data-first** production path for the Earth Atlas. The browser's OpenStreetMap and OpenTopoMap backgrounds are *reference tile services*, not geographic assets owned by this project.

## World source layers and current status

| Dataset | Preferred source | Status |
|---|---|---|
| Global country/region boundaries, coastlines, populated places | Natural Earth public-domain vector datasets | SOURCE IDENTIFIED; NOT IMPORTED |
| Global terrain elevation | Copernicus DEM / NASA SRTM where eligible; USGS 3DEP in USA | SOURCE IDENTIFIED; NOT IMPORTED |
| Roads, rail, buildings, waterways, land use | OpenStreetMap licensed extracts (Geofabrik or other authorized distributors) | SMALL LIVE CASCADIA PILOT ONLY |
| Worldwide settlements and points of interest | OSM extracts plus curated official sources | 100 CURATED ATTRACTION REFERENCES + APPROVED GUILD/RELIC/WONDER POINTS |
| Satellite/aerial imagery | Licensed imagery from authorized providers | NOT IMPORTED |
| 3D buildings and photogrammetry | Survey/scan datasets with explicit reuse rights | NOT IMPORTED |
| Ancient Relic City archaeological reconstructions | Heritage institutions and primary archaeological literature | RESEARCH ONLY; DESIGN DEFERRED |

**Important:** Do not bulk scrape the public OpenStreetMap raster tile servers or Overpass. For full-Earth datasets, download authorized regional extracts, process offline, and publish small generalized chunks to GitHub Pages. OpenStreetMap data requires ODbL compliance and attribution. A world-scale UE5 build needs a separate offline processing and streaming pipeline, not a single giant GeoJSON loaded on an iPhone.

## Importing source GeoJSON into Atlas-ready tiles

The stdlib-only `scripts/partition_geojson.py` accepts *already downloaded* GeoJSON FeatureCollections and writes spatially indexed, bounded chunks with a manifest. It does **not** download data, reconstruct geometry, or assert provenance.

Example:

```bash
python3 scripts/partition_geojson.py \
  --input source/cascadia-roads.geojson \
  --output data/imports/cascadia-roads \
  --layer roads \
  --source "OpenStreetMap contributors" \
  --license ODbL \
  --max-features 400
```

Input features must have GeoJSON geometries with WGS84 longitude/latitude coordinates. Chunks are limited by **feature count**, not guaranteed byte size. Features crossing tile boundaries are assigned to a chunk by representative coordinate; they are not clipped. Review large features and simplify geometries in a GIS before importing. For world-scale extracts, use a streaming GIS workflow (e.g., osmium + GDAL/ogr2ogr) to produce regional GeoJSON first, rather than loading a planet file into this script.

Each output folder contains `manifest.json` and `part-00001.geojson`, etc. Commit manageable output files to the repository only after validating license, attribution, and size. The Atlas can continue using its existing GeoJSON importer for individual chunks; automatic world streaming remains a future implementation task.

## Scope boundary

The priority is to import the **real Earth geographic foundation**. Do not start detailed Ancient Relic City environment design during this phase. Keep evidence and reference locations, and reserve reconstructions for the later separate project.

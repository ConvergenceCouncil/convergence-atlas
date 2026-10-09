# Regional Earth acquisition — Cascadia first

## What is implemented
- A command-line authorized HTTPS downloader for OSM PBF regional extracts.
- Download size cap, SHA-256 checksum, source/ODbL metadata, atomic file output.
- A **manual** GitHub Actions workflow that downloads a Washington State OSM extract as a temporary workflow artifact.

## What is not implemented
- No regional extract has yet been downloaded or validated in a successful workflow run.
- No OSM PBF-to-GeoJSON/vector-tile transformation is included yet.
- No elevation DEM, building geometry, or worldwide road network has been imported.
- The GitHub Pages Atlas is unchanged by running this workflow; raw extracts remain outside the published site.

## Cascadia acquisition stages
1. Washington State OSM source (Geofabrik; ODbL), then British Columbia and Oregon through appropriate authorized extract sources.
2. Process source extracts offline into roads, railways, buildings, waterways, land use, and named settlements.
3. Clip and simplify by region and zoom level; produce indexed vector tiles for the Atlas.
4. Acquire USGS 3DEP and Canadian open elevation DEMs separately, with CRS, vertical datum, resolution and license metadata.
5. Compare completeness, record gaps, and publish only suitable derivatives.

## Running
From GitHub > Actions > **Cascadia source acquisition** > Run workflow. The workflow is manual to avoid repeatedly downloading large datasets and consuming storage quotas. The raw artifact expires after three days.

Official example source: https://download.geofabrik.de/north-america/us/washington-latest.osm.pbf

**Legal and production note:** OpenStreetMap source data is subject to ODbL; attribution and other conditions apply. A raw extract is geographic vector data, not elevation or satellite imagery. Do not embed raw global datasets in the phone-facing web page.

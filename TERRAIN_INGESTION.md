# CONVERGENCE Terrain Ingestion — Global to Local

## Status (2026-10-08)
**No raw global DEM rasters have been downloaded or imported into the repository.** The Atlas currently displays third-party terrain and imagery tiles, which are references, not game-ready heightmaps. This document defines the licensed acquisition and processing path.

## Terrain source priority
1. **Global overview:** NASA SRTM where available, Copernicus DEM GLO-30 where terms permit the intended use, and other openly usable global DEM sources. Coverage and licenses differ by region, resolution, and distributor.
2. **United States high detail:** USGS 3DEP elevation data (including lidar-derived DEMs where available), with metadata and resolution retained.
3. **Other countries:** national mapping agencies and authorized open-data portals; verify reuse, redistribution, attribution, and commercial-game compatibility per dataset.
4. **High-fidelity landmarks:** authorized lidar/photogrammetry, published archaeological surveys and measured plans; do not treat satellite imagery as elevation data.

## Data requirements
Each downloaded DEM tile must retain: source institution, dataset identifier, acquisition date, native resolution, vertical datum, horizontal CRS, license/usage terms, bounding box, no-data value, and checksum. Store provenance in a manifest. Reproject to a common CRS only during processing; preserve originals separately.

## Processing pipeline
- Download through authorized distribution endpoints, respecting quotas and access rules.
- Validate checksums, metadata, geographic bounds and licensing.
- Build a multiresolution elevation pyramid with GDAL/rasterio or equivalent.
- Derive hillshade and slope visualizations for the browser.
- Export region-sized, normalized heightfields for later Unreal Engine landscape work; account for UE landscape height quantization, vertical scaling, origin rebasing, seams and world partition.
- Keep raster tiles outside the GitHub Pages source repository when size requires object storage; the repository should contain manifests, code and lightweight previews.

## Terrain import ledger
| Layer | Current state | Notes |
|---|---|---|
| Global DEM raster | Not imported | Source selection and download required |
| Cascadia regional DEM | Not imported | Prioritize USGS 3DEP and Canadian open elevation sources |
| Seattle Center local DEM | Not imported | Source and spatial extent not yet audited |
| Satellite imagery | Third-party live basemap only | Not downloaded; usage rights remain with providers |
| Topographic contours | Third-party live basemap only | Not imported as elevation geometry |

## Licensing boundary
Do not scrape protected imagery or copy restricted datasets. Licensed viewing access is not permission to redistribute raw data or bake it into commercial game assets. Use official download services, open licenses or separately negotiated rights.

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

## Bounded DEM export prototype (2026-10-09)

The committed `scripts/export_terrarium_dem.py` can reconstruct a local GeoTIFF from a **small bounded selection** of Mapzen/AWS Terrarium PNG elevation tiles. It records source URLs, tile SHA-256 hashes, requested and actual geographic bounds, and output checksum. This is an initial raster acquisition route, **not** a validated production DEM or a globally imported terrain library.

Run on a machine with Python and the required packages:

```bash
python -m pip install numpy requests rasterio pillow
python scripts/export_terrarium_dem.py --bbox -122.45 47.50 -122.20 47.72 --zoom 11 --output data/local/seattle-dem.tif
```

The script limits each request to 64 tiles to prevent accidental bulk downloads. It outputs a geographic EPSG:4326 float32 raster. The original terrain source may blend elevation datasets with differing vertical datums and resolutions; **do not treat it as survey-grade data**. Verify original provider licensing and redistribution terms before use in a commercial release. GeoTIFFs should remain out of the GitHub Pages source tree until storage, versioning, and licensing are settled.

Next: execute the export on a runner, inspect GeoTIFF dimensions/CRS, compare known elevations, assess seams and no-data, and design an approved multi-region source ledger before converting any data to UE5 landscape heightfields.

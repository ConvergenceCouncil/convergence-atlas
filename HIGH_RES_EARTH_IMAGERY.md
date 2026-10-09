# CONVERGENCE Earth Atlas — High-Resolution Imagery Standard

## Goal
Make the Atlas visually crisp at all useful viewing distances while keeping geographic and geological fidelity. Do not claim imagery resolution beyond the source's native ground sample distance (GSD).

## Source priority
1. **Local/US pilot:** properly licensed USGS aerial orthophotography (NAIP where available), USGS 3DEP elevation/LiDAR; preserve capture year, GSD, vertical datum, and citation.
2. **Regional/global:** legally usable Sentinel/Copernicus and Landsat imagery; these are not substitutes for sub-meter local orthophotos.
3. **Reference and streamed preview:** Esri World Imagery, with attribution and its provider's applicable access/caching terms. Streaming does not authorize scraping or packaging imagery for UE5.
4. **Close-up reconstruction:** licensed overlapping aerial/street photographs with known georeferencing and photogrammetry metadata; no bulk harvesting from sites that prohibit it.

## Image processing requirements
- Maintain a catalog by footprint, EPSG/CRS, source, capture date, GSD (meters/pixel), license, attribution, and checksum.
- Orthorectify imagery to the elevation model; use camera calibration for photogrammetry.
- Build tiled pyramids with proper resampling, seam-aware mosaics, color balancing, and explicit no-data handling.
- Prefer native pixels and multiresolution LOD; overzooming, sharpening, and AI enhancement do **not** create verified geographic detail.
- Keep 16-bit DEMs distinct from imagery textures; ground imagery does not create mesh geometry.
- Check seasonal differences, shadows, cloud cover, and mismatched capture years.
- Use phone-friendly progressive loading and cap concurrent requests; never ship millions of full-resolution photographs to a single browser session.

## Geography-first rollout
1. Seattle pilot: imagery provenance, actual available GSD, elevation alignment, and source-license review.
2. Cascadia: adjacent georeferenced imagery tiles and seam checks.
3. Worldwide: progressively fill catalog by coverage and quality; local high-resolution data is uneven.
4. CONVERGENCE fictional world-state modifications remain separate overlays on an immutable real-world baseline.

## Current implementation
The Atlas 3D Terrain viewer streams Esri World Imagery and public Terrarium elevation. Its **High-detail imagery** switch removes hillshade and shows terrain at natural vertical exaggeration. This is a display improvement, **not** a new high-resolution imagery dataset or photogrammetry reconstruction. Aerial photo ingestion, photogrammetry, and higher-resolution local source replacement are pending.

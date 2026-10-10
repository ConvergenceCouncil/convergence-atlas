# CONVERGENCE Earth — world asset progress

Updated 10 October 2026.

The saved World Atlas, original atlas page and ten-tab geographic workbook were read before this work. The approved 82-site Guild network, civilian jurisdiction, permanent Gate-less Santiago and immutable real-Earth baseline remain the planning foundation.

## Available work

- **Seattle Center terrain pilot:** approximately 804 × 742 meters of sourced ground shape. A 505 × 505 16-bit landscape heightmap includes UTM Zone 10N bounds, UE5 X/Y/Z scales and actor elevation offset. Blender and GLB previews are generated from the same data. Source-grid resampling does not create additional geographic detail.
- **Knossos Throne Room review:** source MD5 `d73acfdb906ca7ecda4452936050a57f` verified in GitHub builds. The geometry-preserving pipeline resizes the packed source texture and enforces a 2048-pixel/60-MB review budget. It rejects a changed triangle count before automatic publication. The published GLB is 17,319,384 bytes with all 260678 source triangles and a 2048 × 2048 texture. This is one source sector, not the entire reconstructed city or palace.
- **Earth vectors:** nine files / 1642 features validate. One empty Loire geometry was excluded with its original index and reason preserved; no replacement geometry invented.
- **Atlas access:** terrain and architecture reviews are linked from Earth Progress. Knossos also has a review link in its globe marker description.

## Remaining production checks

Seattle: verify vertical datum and source elevation, replace coarse data where appropriate, check adjacent seams, import into UE5, then add sourced roads/buildings and approved Guild architecture. Broad source-tile offshore depths remain suspect and are excluded from this land pilot.

Knossos: compare against architectural references, establish scale and entry placement, validate connected walkable floors and collision, measure iPhone performance, and test UE5 import. Source rights metadata differs between Zenodo (CC BY 4.0) and SearchCulture (CC BY-SA 4.0); attribution and ShareAlike remain with the review derivative.

Neither pilot is approved gameplay architecture. `data/architectural-models.json` remains the production approval boundary. Planet-wide detailed interiors, streets, foliage and continuous gameplay traversal remain unfinished.

## Reproducibility

`tools/build_terrain_review.py` rebuilds the terrain Blender scene and GLB from the committed heightmap and metadata. `tools/optimize_architecture.py` loads packed textures before resizing, preserving geometry when `--ratio 1` is used. `tools/validate_review_glb.py` checks actual embedded texture dimensions, triangle count and transfer budget. The workflow saves only validated model outputs to the repository.

Local unit tests and globe registry checks pass, with the Rasterio-specific local test skipped where that dependency is absent. GitHub's terrain smoke workflow independently passed raster CRS, heightmap bit-depth and metric-scale checks. Browser/iPhone and UE5 runtime testing are not represented as completed.

Verified delivery build: https://github.com/ConvergenceCouncil/convergence-atlas/actions/runs/38092330462

# CONVERGENCE Earth — world asset progress

Updated 11 October 2026.

The saved World Atlas, original atlas page and ten-tab geographic workbook were read before this work. The approved 82-site Guild network, civilian jurisdiction, permanent Gate-less Santiago and immutable real-Earth baseline remain the planning foundation.

## Available work

- **Seattle Center terrain pilot:** approximately 804 × 742 meters of sourced ground shape. A 505 × 505 16-bit landscape heightmap includes UTM Zone 10N bounds, UE5 X/Y/Z scales and actor elevation offset. Blender and GLB previews are generated from the same data. Source-grid resampling does not create additional geographic detail.
- **Knossos Throne Room review:** source MD5 `d73acfdb906ca7ecda4452936050a57f` verified in GitHub builds. The geometry-preserving pipeline resizes the packed source texture and enforces a 4096-pixel/60-MB review budget. It rejects a changed triangle count before automatic publication. The published GLB is 20,062,732 bytes with all 260678 source triangles and a 4096 × 4096 texture. This is one source sector, not the entire reconstructed city or palace.
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

## Seattle roads and foliage pilot

The globe now has a bounded Seattle Center ground-detail layer sourced from OpenStreetMap: 2,902 mapped road/path ways and 1,737 mapped tree locations, exported 11 October 2026. Nearby ground corridors distinguish roads from pedestrian paths and use mapped widths when available; otherwise widths are estimates. Bridges, tunnels and elevated ways are excluded from the ground overlay. Generic original broadleaf GLB proxies use mapped tree locations and heights where available, otherwise an 8m estimate. They are not species reconstructions or surveyed canopy shapes.

Phone rendering is limited to the nearest 100 road ways and 120 trees. The layer loads only near Seattle Center; trees stop above 1.4km camera clearance and roads stop above 5km. Attribution and ODbL provenance are included with the cached GeoJSON. No collision or continuous walking/navigation mesh has been added. Code, data and asset checks pass; actual iPhone FPS and visual ground alignment still require device verification because the available browser has WebGL disabled.

### Ground-detail refinement pass

Added two original generic broadleaf silhouettes with smooth canopy shading (42,304 and 42,296 bytes, 1,000 triangles each), selected deterministically by mapped tree ID. These are visual variety, not inferred species. Road colors now honor mapped asphalt, concrete, gravel and unpaved surfaces; unknown surfaces retain class defaults. Terrain/building detail uses camera clearance above available terrain height, falling back to ellipsoid height when terrain is unavailable. Phone feature budgets and mapped positions remain unchanged. Regression tests and Blender previews pass; real device frame rate and final surveyed alignment remain unverified.

### Ground coverage and movement refinement

Road selection now measures proximity to full line segments rather than endpoints, and reserves up to 25% of the existing road budget for nearby main/residential streets. This avoids tiny footpath sections crowding streets out of a dense view. Nearby ground detail responds during camera movement, throttled to 350ms and 30m movement, with a small retention preference to reduce feature churn. Limits remain 100 road ways/120 trees on phones. Lifecycle cleanup and stale-download guards are regression-tested. Selection was checked against the actual Seattle export; this is not an iPhone frame-rate measurement.

### Progressive zoom transitions

Nearby tree budgets now reduce gradually between 600m and 1,400m camera clearance instead of removing the full layer at one cutoff. Road budgets reduce between 1,500m and 5,000m. Closest ground views retain 100 road ways and 120 trees on phones. Both tree and road budget changes refresh even when the view focus stays still, and retention prioritizes nearer mapped features. Monotonic budget tests and selection checks across the actual Seattle dataset pass. This is gradual geometry thinning, not transparency blending; actual phone visual smoothness remains to be checked.

### Globe presentation refinement

Removed country polygon fill and limited country outlines to camera heights at or above 150km, keeping local imagery unobscured by the atlas overlay. Settled status notices fade after seven seconds; loading and error notices remain visible, with full messages retained in the menu. Panels and building details respect phone safe-area insets; the explore button has a 44px minimum touch target. Escape closes the menu and building inspector. Regression checks verify status lifecycle and overlay visibility, with existing ground/detail tests passing. This does not certify new imagery resolution or actual iPhone rendering performance.

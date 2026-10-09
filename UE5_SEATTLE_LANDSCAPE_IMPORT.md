# CONVERGENCE — Seattle UE5 Landscape Import Pilot

**Status:** Automated Seattle raster export, 16-bit PNG conversion, metric UTM Zone 10N projection, and scale-metadata validation have passed in GitHub Actions. **No UE5 in-editor import or seam test has been performed.**

## Get the files
1. Open the latest successful **Terrain DEM export smoke test** in GitHub Actions.
2. Download the `seattle-dem-smoke` artifact (requires GitHub sign-in).
3. Extract `seattle-metric-ue5.png` and `seattle-metric-ue5.json`. Keep the original `seattle-dem.tif` and `seattle-dem.manifest.json` for provenance.

## UE5 Landscape import
1. Open a **test level**, not the canonical CONVERGENCE Earth.
2. Select **Landscape** mode → **Import from File**.
3. Choose `seattle-metric-ue5.png`. Verify the image imports as **16-bit grayscale** at **505 × 505 vertices**.
4. Set landscape **X Scale** to `unreal_x_scale_percent`, **Y Scale** to `unreal_y_scale_percent`, and **Z Scale** to `unreal_z_scale_percent` from `seattle-metric-ue5.json`.
5. Set actor Z position in centimeters to `unreal_actor_z_offset_cm` (a prototype elevation reference, not a verified sea-level datum).
6. Verify that the landscape's horizontal extent equals the projected bounds recorded in `metric_bounds_projected` (meters).
7. Capture screenshots and measure terrain dimensions. Do not infer UE5 validation from the automated PNG checks.

## Important limitations
- **This is a small cropped sample**, not all Seattle or Cascadia. The metric converter conservatively crops 20% from each side of the projected bounding rectangle to avoid uncovered pixels.
- The DEM is reconstructed from public AWS Terrarium elevation tiles; source precision and vertical datum are not survey-grade or independently confirmed.
- UTM coordinates are absolute projected coordinates; for World Partition, use an explicit regional origin/georeferencing strategy and keep coordinates in the metadata. **Do not** place huge UTM easting/northing values directly into UE actor transforms.
- The sample is not seam-matched with adjacent landscapes. Regional terrain tiling, shared edge vertices, water/shoreline masks, high-detail USGS 3DEP replacement, and licensing review are pending.
- No Convergence destruction or world changes belong in the immutable Earth baseline.

## Next production steps
- Add reproducible per-region terrain manifests with projected bounds and regional origins.
- Implement overlap-aware adjacent landscape tiles and seam validation.
- Replace prototype elevation with vetted USGS 3DEP source data for the Seattle pilot.
- Import the sample into UE5 and verify geometry, scaling, and performance on actual hardware.

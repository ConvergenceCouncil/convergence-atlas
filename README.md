# CONVERGENCE Earth Atlas

Mobile-first geographic reference for the CONVERGENCE game project.

- [3D Earth](https://convergencecouncil.github.io/convergence-atlas/globe.html): satellite imagery, optional elevation and streamed buildings, searchable Guilds, Modern Wonders, Ancient Relic Cities and additional landmarks.
- [2D Atlas](https://convergencecouncil.github.io/convergence-atlas/): geographic reference and research layers.
- [Earth production progress](https://convergencecouncil.github.io/convergence-atlas/earth-progress.html): implementation states and remaining work.

## Using the globe

Open **Explore locations**, search a place, select it and choose **Go to location**. Aerial, Building and Ground set the camera height above sampled terrain; Orbit circles the selected reference point. Terrain, building, imagery and quality controls share the same collapsible menu. Phones default to balanced detail; high detail is available explicitly.

Markers can also select destinations. Coordinates are reference points, not surveyed Guild building placement or dungeon entrances. A Ground view is a camera preset, not walkable gameplay.

The viewer requires WebGL and internet access. Provider connections have bounded waits; one missing destination file does not discard the other lists. Visible status messages report engine, imagery and building failures. Use the 2D Atlas if the engine cannot initialize.

## Coverage and provenance

Imagery: Esri / GIS providers and USGS continental-US aerial tiles. Terrain: Re:Earth / Mapterhorn. Buildings: Overture and OpenStreetMap. Country context: Natural Earth. Provider attribution remains visible in the globe.

Streamed and extruded buildings are geographic geometry, not detailed landmark reconstructions. `data/architectural-models.json` currently contains **no approved architectural assets**. Licensed high-fidelity landmark models, interiors, vegetation and UE5 traversal remain production work. Do not interpret the globe as a completed worldwide game.

## Verification

Run from the repository root:

```sh
python3 -m unittest discover -s tests
node tests/globe_registry.test.cjs
python3 scripts/validate_earth.py --output /tmp/earth-inventory.json
```

The registry behavior test covers partial source outages, duplicate landmarks, invalid coordinates, search and marker selection. Browser/iPhone rendering still requires device QA. All nine Earth vector files validate. One empty Loire record was excluded with its original index and reason retained in the dataset metadata.

GitHub Pages serves the root of `main` when configured in repository settings. A published update may take time to appear; reload if an older version is cached.

## World asset pilots

[Seattle terrain](terrain-pilot.html): sourced land crop, metric UE5 heightmap and Blender-derived review GLB. [Knossos review](knossos-room-review.html): geometry-preserving Throne Room model with source attribution, texture budget checks and automatic verified-asset publication. Both require scale, collision and device QA before gameplay approval.

All nine Earth vector files validate after excluding one empty Loire record, with its original index and reason preserved.

# CONVERGENCE Earth Atlas

Mobile-first geographic prototype for the CONVERGENCE game project.

## Current working baseline
- `index.html` contains a lightweight Leaflet/OpenStreetMap Seattle map with visible loading and tile-error messages.
- Seattle Center is shown as an **approximate geographic reference**, not a verified Guild site.
- The 82-site Guild registry, 3D viewer, audited site locations, terrain and UE5 gameplay are **not yet included in this GitHub baseline**.

## Open on an iPhone
This repository is currently **private**. GitHub Pages on a free account generally requires a public repository. To publish a free public site, first review the files for information you are comfortable making public, then change repository visibility to public and enable Pages at **Settings → Pages → Deploy from a branch → main / (root)**. After publication, the site should appear at `https://convergencecouncil.github.io/convergence-atlas/`.

The map uses internet-hosted Leaflet assets and OpenStreetMap tiles; internet access is required. If it appears blank, use Safari and read the visible status message.

## Roadmap
1. Verify this minimal site displays in Safari.
2. Add the approved Guild registry without guessing precise coordinates.
3. Restore GeoJSON overlays, exports and the experimental 3D viewer.
4. Build data-backed Cascadia terrain and UE5 handoff assets.

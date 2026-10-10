# ARC-03 Knossos — UE5 Vertical Slice Implementation

This is the implementation path for turning the first Knossos room cluster into something playable, not merely viewable.

## Scope

Pilot route: **Throne Room → Grand Staircase → Queen's Megaron**.

Do not attempt the whole palace first. The acceptance target is one continuous route with reliable scale, collision, lighting, navigation and room transitions.

## 1. Source intake

1. Acquire one official room GLB from the Zenodo Knossos record with `tools/fetch_knossos.py`.
2. Preserve the downloaded file as the immutable source master.
3. Run `tools/audit_architecture.py` and retain the JSON output beside the source.
4. Verify the asset's actual license and redistribution rights before committing binary geometry to the repository or shipping it.
5. Check dimensions against archaeological/reference material. Scene units from a GLB are not automatically authoritative real-world dimensions.

## 2. Review mesh

Use `tools/optimize_architecture.py` only for the browser review copy. It is not the production master.

Target for each room during the first pass:

- <= 1.5M triangles for the review mesh
- <= 2048 px on ordinary textures
- preserve frescoes, stairs, door openings, railings, floor edges and silhouette-critical stonework
- no destructive decimation on thin architectural elements

Open the resulting GLB in `interior-lab.html`. Walk the complete route at human eye height before accepting the room for UE5 import.

## 3. UE5 content structure

Use this content layout:

```text
/Game/CONVERGENCE/World/RelicCities/Knossos/
  Geometry/
    SourceReference/
    StaticMeshes/
    Collision/
  Materials/
    Master/
    Instances/
    Textures/
  Blueprints/
  Navigation/
  Lighting/
  Data/
```

Suggested production names:

```text
SM_KNO_ThroneRoom_Architecture
SM_KNO_GrandStaircase_Architecture
SM_KNO_QueensMegaron_Architecture
BP_KNO_InteriorRoute_Pilot
DA_KNO_InteriorRoute_Pilot
```

## 4. Import contract

- UE5 world units: centimeters.
- Convert glTF Y-up orientation correctly on import; do not rotate every child mesh manually after assembly.
- Establish one stable root transform for the room cluster.
- Keep the playable interior near a local origin rather than placing mesh vertices at raw geographic coordinates.
- Enable Nanite for dense opaque architectural meshes after confirming materials and collision behavior.
- Do not use Nanite as a substitute for removing accidental duplicate geometry or corrupted scans.

## 5. Player collision

Pilot capsule target:

- radius: 42 cm
- half-height: 96 cm
- minimum intended doorway width: 95 cm
- minimum intended passage height: 210 cm
- max normal step height: 45 cm
- max walkable slope: 44 degrees

For the first playable pass, Complex Collision as Simple is acceptable on static architecture if performance remains acceptable. Replace it with deliberate simple/custom collision before production lock.

The acceptance test is physical traversal. The protagonist must be able to enter every pilot room, turn around inside it, leave it, and ascend/descend the Grand Staircase without teleporting, snagging on scan noise or walking through walls.

## 6. Navigation and room graph

Create named route markers:

```text
CV_SPAWN_ENTRY
CV_PORTAL_THRONE_ROOM
CV_PORTAL_GRAND_STAIRCASE
CV_PORTAL_QUEENS_MEGARON
```

These markers become the stable interface between the historical geometry and CONVERGENCE gameplay systems. Contracts, NPC pathing, World Pulse events, Relic interactions and save-state logic should refer to these markers or room IDs rather than raw mesh names.

Represent the pilot route as three connected room IDs in a data asset. Do not hard-code progression into the static mesh actor.

## 7. Materials

Preserve original source textures for reference, but build UE5 material instances around shared master materials when possible.

Initial material families:

- painted plaster / fresco
- dressed stone
- rough stone
- timber
- ceramic / decorative surface

Do not add fictional Relic effects to the historical base material pass. CONVERGENCE alterations should be layered separately so we can distinguish reconstruction from post-Convergence art direction.

## 8. Lighting

First playable target:

- Lumen for the vertical slice
- one controlled exterior sun/sky setup
- local practical/fill lighting only where needed for legibility
- no baked-lighting dependency during early iteration

The room should remain readable without flattening all contrast. Historical atmosphere and gameplay readability must both survive.

## 9. Historical reconstruction QA

Every reconstructed element belongs to one of three internal confidence states:

- **documented** — supported directly by surviving fabric or strong archaeological evidence
- **reconstructed** — scholarly interpretation with reasonable support
- **speculative** — useful to complete a traversable game environment but not established fact

These states do not need to appear to players, but production must preserve the distinction.

## 10. Definition of implementable

The Knossos pilot is ready for gameplay implementation when all of the following are true:

1. Three-room route exists as actual geometry.
2. Scale has been checked.
3. Source rights have been checked.
4. Materials render correctly.
5. Player collision works end to end.
6. Stair traversal works both directions.
7. Entry and room markers are placed.
8. A NavMesh can cover the intended NPC route.
9. The environment opens correctly in the browser review build and UE5.
10. No source mesh or optimization result is being misrepresented as historically definitive.

At that point we can begin adding CONVERGENCE-specific gameplay, Relic-state changes, NPC behavior and World Pulse events without rebuilding the architectural foundation.

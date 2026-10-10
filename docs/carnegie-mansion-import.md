# CONVERGENCE — Carnegie Mansion import

Source: [Cooper Hewitt Smithsonian mansion model](https://www.cooperhewitt.org/open-source-at-cooper-hewitt/mansionmodel/). The **full FBX set**, not the printable STL, includes textured exteriors and interiors by floor. The museum states the model is **CC0**.

## Preparation

1. Download the complete FBX asset package from the Smithsonian's 3D portal.
2. Extract the FBX files and their original texture folders together.
3. Install Blender locally (FBX import and glTF export are built in).
4. Convert **each floor and exterior separately** using:

```bash
blender -b -P tools/convert_fbx_to_glb.py -- "input/main-floor.fbx" "output/main-floor.glb"
python3 tools/audit_architecture.py "output/main-floor.glb"
```

5. Review the converted GLB in [Interior Lab](../interior-lab.html) using the file picker. Compare floors with the exterior before joining; coordinate transforms, meter scale, mesh orientation and missing surfaces require manual verification.
6. Verify actual stairs, doors, collision, navigation, texture fidelity and mobile performance before registering the asset in `data/architectural-models.json`.

**Status:** source identified and conversion script committed; no Smithsonian geometry downloaded, converted, or approved yet. Do not mark a model as fully traversable from mesh names or triangle counts alone.

**Limitations:** The conversion script requires installed Blender and source files; it does not reconstruct absent geometry, create collision meshes or prove walkability. Large scans need decimation/LODs before mobile deployment. Attribution is recommended by the museum.

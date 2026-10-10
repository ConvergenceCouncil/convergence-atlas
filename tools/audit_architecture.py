#!/usr/bin/env python3
"""Inspect a downloaded glTF 2.0 architectural asset before Atlas approval.

Usage:
  python3 tools/audit_architecture.py path/to/building.gltf
  python3 tools/audit_architecture.py path/to/building.glb

No third-party dependencies. This is structural QA, not proof of traversal or rights.
"""
import json
import math
import pathlib
import struct
import sys


def load(path):
    data = path.read_bytes()
    if path.suffix.lower() == ".glb":
        if data[:4] != b"glTF" or len(data) < 20:
            raise ValueError("Invalid GLB header")
        version, total = struct.unpack_from("<II", data, 4)
        if version != 2 or total != len(data):
            raise ValueError("GLB version or size mismatch")
        offset = 12
        while offset + 8 <= len(data):
            size, kind = struct.unpack_from("<II", data, offset)
            offset += 8
            if offset + size > len(data):
                raise ValueError("GLB chunk overflow")
            if kind == 0x4E4F534A:
                return json.loads(data[offset : offset + size])
            offset += size
        raise ValueError("GLB has no JSON chunk")
    return json.loads(data.decode("utf-8"))


def mat_identity():
    return [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]


def mat_mul(a, b):
    out = [0.0] * 16
    for col in range(4):
        for row in range(4):
            out[col * 4 + row] = sum(a[k * 4 + row] * b[col * 4 + k] for k in range(4))
    return out


def node_matrix(node):
    if isinstance(node.get("matrix"), list) and len(node["matrix"]) == 16:
        return [float(x) for x in node["matrix"]]
    t = node.get("translation", [0, 0, 0])
    s = node.get("scale", [1, 1, 1])
    x, y, z, w = node.get("rotation", [0, 0, 0, 1])
    xx, yy, zz = x * x, y * y, z * z
    xy, xz, yz = x * y, x * z, y * z
    wx, wy, wz = w * x, w * y, w * z
    r = [
        1 - 2 * (yy + zz), 2 * (xy + wz), 2 * (xz - wy), 0,
        2 * (xy - wz), 1 - 2 * (xx + zz), 2 * (yz + wx), 0,
        2 * (xz + wy), 2 * (yz - wx), 1 - 2 * (xx + yy), 0,
        0, 0, 0, 1,
    ]
    sm = [s[0], 0, 0, 0, 0, s[1], 0, 0, 0, 0, s[2], 0, 0, 0, 0, 1]
    tm = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, t[0], t[1], t[2], 1]
    return mat_mul(tm, mat_mul(r, sm))


def transform_point(m, p):
    x, y, z = p
    return [
        m[0] * x + m[4] * y + m[8] * z + m[12],
        m[1] * x + m[5] * y + m[9] * z + m[13],
        m[2] * x + m[6] * y + m[10] * z + m[14],
    ]


def accessor_bounds(g, accessor_index):
    accessors = g.get("accessors", [])
    if not isinstance(accessor_index, int) or accessor_index >= len(accessors):
        return None
    a = accessors[accessor_index]
    lo, hi = a.get("min"), a.get("max")
    if not (isinstance(lo, list) and isinstance(hi, list) and len(lo) >= 3 and len(hi) >= 3):
        return None
    return [float(v) for v in lo[:3]], [float(v) for v in hi[:3]]


def bbox_corners(lo, hi):
    return [[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]


def main():
    path = pathlib.Path(sys.argv[1])
    g = load(path)
    if str(g.get("asset", {}).get("version", "")).split(".")[0] != "2":
        raise ValueError("Not glTF 2.x")

    nodes = g.get("nodes", [])
    meshes = g.get("meshes", [])
    materials = g.get("materials", [])
    accessors = g.get("accessors", [])
    names = [str(n.get("name", "")) for n in nodes]
    markers = {
        k: [n for n in names if k in n.lower()]
        for k in ("floor", "stair", "door", "room", "collision", "navmesh", "entrance")
    }

    tris = 0
    primitive_count = 0
    for mesh in meshes:
        for p in mesh.get("primitives", []):
            primitive_count += 1
            if p.get("mode", 4) != 4:
                continue
            ix = p.get("indices")
            pos = p.get("attributes", {}).get("POSITION")
            if isinstance(ix, int) and ix < len(accessors):
                tris += accessors[ix].get("count", 0) // 3
            elif isinstance(pos, int) and pos < len(accessors):
                tris += accessors[pos].get("count", 0) // 3

    roots = []
    scenes = g.get("scenes", [])
    scene_index = g.get("scene", 0)
    if scenes and isinstance(scene_index, int) and scene_index < len(scenes):
        roots = scenes[scene_index].get("nodes", [])
    if not roots:
        child_ids = {c for n in nodes for c in n.get("children", []) if isinstance(c, int)}
        roots = [i for i in range(len(nodes)) if i not in child_ids]

    world_lo = [math.inf, math.inf, math.inf]
    world_hi = [-math.inf, -math.inf, -math.inf]
    bounded_mesh_nodes = 0

    def visit(index, parent):
        nonlocal bounded_mesh_nodes
        if not isinstance(index, int) or index >= len(nodes):
            return
        node = nodes[index]
        world = mat_mul(parent, node_matrix(node))
        mesh_index = node.get("mesh")
        if isinstance(mesh_index, int) and mesh_index < len(meshes):
            found = False
            for p in meshes[mesh_index].get("primitives", []):
                b = accessor_bounds(g, p.get("attributes", {}).get("POSITION"))
                if not b:
                    continue
                found = True
                for point in bbox_corners(*b):
                    q = transform_point(world, point)
                    for axis in range(3):
                        world_lo[axis] = min(world_lo[axis], q[axis])
                        world_hi[axis] = max(world_hi[axis], q[axis])
            if found:
                bounded_mesh_nodes += 1
        for child in node.get("children", []):
            visit(child, world)

    for root in roots:
        visit(root, mat_identity())

    dimensions = None
    bounds = None
    if all(math.isfinite(v) for v in world_lo + world_hi):
        bounds = {"min": [round(v, 4) for v in world_lo], "max": [round(v, 4) for v in world_hi]}
        dimensions = [round(world_hi[i] - world_lo[i], 4) for i in range(3)]

    images = g.get("images", [])
    textures = g.get("textures", [])
    report = {
        "file": str(path),
        "file_size_MB": round(path.stat().st_size / 1_000_000, 2),
        "asset_generator": g.get("asset", {}).get("generator"),
        "nodes": len(nodes),
        "meshes": len(meshes),
        "mesh_names_sample": [str(m.get("name", "")) for m in meshes[:25]],
        "primitives": primitive_count,
        "triangles_estimate": tris,
        "materials": len(materials),
        "material_names_sample": [str(m.get("name", "")) for m in materials[:25]],
        "textures": len(textures),
        "images": len(images),
        "extensions_used": g.get("extensionsUsed", []),
        "extensions_required": g.get("extensionsRequired", []),
        "markers": markers,
        "scene_bounds_estimate": bounds,
        "scene_dimensions_estimate": dimensions,
        "scene_dimension_note": "Uses glTF accessor bounds and node transforms; units are glTF scene units and are not proof of real-world scale.",
        "bounded_mesh_nodes": bounded_mesh_nodes,
        "external_files": [
            x.get("uri")
            for x in g.get("buffers", []) + images
            if x.get("uri") and not x["uri"].startswith("data:")
        ],
        "pass": "STRUCTURE_ONLY",
        "not_verified": [
            "interior completeness",
            "room connectivity",
            "walkable floor surfaces",
            "stairs and doors clearance",
            "collision",
            "real-world dimensions",
            "historical reconstruction accuracy",
            "licensing/redistribution rights",
            "mobile frame rate",
        ],
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: audit_architecture.py model.gltf|model.glb")
    main()

#!/usr/bin/env python3
"""Validate committed Earth baseline GeoJSON and emit an honest inventory."""
import argparse
import json
import math
from pathlib import Path

def walk_coords(v):
    if isinstance(v, list):
        if len(v) >= 2 and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v[:2]):
            lon, lat = v[:2]
            if not (math.isfinite(lon) and math.isfinite(lat) and -180 <= lon <= 180 and -90 <= lat <= 90):
                raise ValueError("Invalid WGS84 coordinate")
            yield (lon, lat)
        else:
            for x in v:
                yield from walk_coords(x)

def check_geom(g):
    if not isinstance(g, dict):
        raise ValueError("Missing geometry")
    t = g.get("type")
    if t == "GeometryCollection":
        for sub in g.get("geometries", []):
            yield from check_geom(sub)
    elif t in {"Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon"}:
        yield from walk_coords(g.get("coordinates"))
    else:
        raise ValueError(f"Unsupported geometry type: {t}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", default="data/earth")
    p.add_argument("--output", default="earth-inventory.json")
    args = p.parse_args()
    files = sorted(Path(args.root).glob("*.geojson"))
    if not files:
        raise SystemExit("No Earth baseline files found")
    inventory = {"schema": "convergence-earth-inventory-v1", "files": [], "total_features": 0, "notes": "Inventory of committed vector features only; no DEM or building coverage implied."}
    errors = []
    for path in files:
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
            if d.get("type") != "FeatureCollection" or not isinstance(d.get("features"), list):
                raise ValueError("Expected GeoJSON FeatureCollection")
            n = 0
            bbox = [180, 90, -180, -90]
            for feature in d["features"]:
                if feature.get("type") != "Feature":
                    raise ValueError("Non-feature entry")
                coords = list(check_geom(feature.get("geometry")))
                if not coords:
                    raise ValueError("Empty feature geometry")
                for lon, lat in coords:
                    bbox = [min(bbox[0], lon), min(bbox[1], lat), max(bbox[2], lon), max(bbox[3], lat)]
                n += 1
            inventory["files"].append({"file": str(path), "features": n, "bytes": path.stat().st_size, "bbox": bbox if n else None})
            inventory["total_features"] += n
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as e:
            errors.append(f"{path}: {e}")
    Path(args.output).write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    print(f"Validated {len(inventory['files'])}/{len(files)} files; {inventory['total_features']} features")
    for err in errors:
        print("ERROR:", err)
    if errors:
        raise SystemExit(1)

if __name__ == "__main__":
    main()

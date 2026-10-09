#!/usr/bin/env python3
"""Partition already-obtained WGS84 GeoJSON into manageable Atlas files.

This is a small regional utility, not a planet-scale streaming importer.
"""
import argparse
import json
import math
from pathlib import Path


def points(coords):
    if not isinstance(coords, list):
        raise ValueError("Invalid coordinate array")
    if len(coords) >= 2 and all(isinstance(v, (int, float)) and math.isfinite(v) for v in coords[:2]):
        lon, lat = coords[:2]
        if not (-180 <= lon <= 180 and -90 <= lat <= 90):
            raise ValueError("Coordinate outside WGS84 bounds")
        yield lon, lat
    else:
        for item in coords:
            yield from points(item)


def geometry_points(geometry):
    if not isinstance(geometry, dict):
        raise ValueError("Missing geometry")
    kind = geometry.get("type")
    if kind == "GeometryCollection":
        for sub in geometry.get("geometries", []):
            yield from geometry_points(sub)
    elif kind in {"Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon"}:
        yield from points(geometry.get("coordinates"))
    else:
        raise ValueError(f"Unsupported geometry: {kind}")


def bounds_for(feature):
    coords = list(geometry_points(feature.get("geometry")))
    if not coords:
        raise ValueError("Feature contains no coordinates")
    return [min(p[0] for p in coords), min(p[1] for p in coords),
            max(p[0] for p in coords), max(p[1] for p in coords)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--layer", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--license", required=True)
    parser.add_argument("--max-features", type=int, default=400)
    args = parser.parse_args()
    if args.max_features < 1 or args.max_features > 5000:
        parser.error("--max-features must be between 1 and 5000")
    input_path = Path(args.input)
    output_dir = Path(args.output)
    if input_path.resolve() == output_dir.resolve():
        parser.error("Input and output must differ")
    data = json.loads(input_path.read_text(encoding="utf-8"))
    if data.get("type") != "FeatureCollection" or not isinstance(data.get("features"), list):
        parser.error("Input must be a GeoJSON FeatureCollection")
    features = data["features"]
    if not features:
        parser.error("Input contains no features")
    if any(f.get("type") != "Feature" for f in features):
        parser.error("All entries must be GeoJSON Features")
    feature_bounds = [bounds_for(f) for f in features]
    output_dir.mkdir(parents=True, exist_ok=True)
    chunks = []
    for offset in range(0, len(features), args.max_features):
        subset = features[offset:offset + args.max_features]
        b = feature_bounds[offset:offset + args.max_features]
        bbox = [min(x[0] for x in b), min(x[1] for x in b),
                max(x[2] for x in b), max(x[3] for x in b)]
        filename = f"part-{len(chunks) + 1:05d}.geojson"
        output = {"type": "FeatureCollection", "features": subset}
        (output_dir / filename).write_text(json.dumps(output, separators=(",", ":")), encoding="utf-8")
        chunks.append({"file": filename, "feature_count": len(subset), "bbox": bbox})
    manifest = {"schema": "convergence-geojson-chunks-v1", "layer": args.layer,
                "source": args.source, "license": args.license,
                "crs": "EPSG:4326", "feature_count": len(features),
                "chunk_count": len(chunks), "chunks": chunks,
                "notes": "Chunked by feature count, not geometry clipped or automatically streamed"}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(features)} features in {len(chunks)} chunks to {output_dir}")


if __name__ == "__main__":
    main()

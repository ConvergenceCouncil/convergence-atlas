#!/usr/bin/env python3
"""Gate publication of the bounded Seattle OpenStreetMap browser preview."""
import argparse
import json
import math
from pathlib import Path

def coordinates(value):
    if isinstance(value, list):
        if len(value)>=2 and all(isinstance(x,(int,float)) and not isinstance(x,bool) for x in value[:2]):
            yield value[0],value[1]
        else:
            for child in value:
                yield from coordinates(child)

def validate(path, maximum_features=2500, maximum_bytes=4_000_000):
    file=Path(path)
    if not file.exists() or file.stat().st_size>maximum_bytes:
        raise ValueError("Preview missing or larger than the mobile limit")
    data=json.loads(file.read_text(encoding="utf-8"))
    features=data.get("features")
    if data.get("type")!="FeatureCollection" or not isinstance(features,list) or not 1<=len(features)<=maximum_features:
        raise ValueError("Invalid or empty bounded FeatureCollection")
    if (data.get("metadata") or {}).get("license")!="ODbL 1.0":
        raise ValueError("Missing expected OpenStreetMap license metadata")
    total_coordinates=0
    for i,feature in enumerate(features):
        if feature.get("type")!="Feature":
            raise ValueError(f"Invalid feature {i}")
        geom=feature.get("geometry") or {}
        if geom.get("type")=="GeometryCollection":
            raise ValueError("GeometryCollection unsupported in mobile pilot")
        found=0
        for lon,lat in coordinates(geom.get("coordinates")):
            if not (math.isfinite(lon) and math.isfinite(lat) and -122.6<=lon<=-122.0 and 47.3<=lat<=47.9):
                raise ValueError(f"Feature {i} outside Seattle pilot safety envelope")
            found+=1
        if not found:
            raise ValueError(f"Empty geometry in feature {i}")
        total_coordinates+=found
    print(f"PASS: {len(features)} Seattle features, {total_coordinates} coordinates, {file.stat().st_size} bytes")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("path")
    args=parser.parse_args()
    validate(args.path)

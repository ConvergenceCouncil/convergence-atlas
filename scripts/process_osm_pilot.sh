#!/usr/bin/env bash
# Process a bounded real-Earth OSM pilot from an authorized PBF extract.
set -euo pipefail
: "${SOURCE_PBF:?Set SOURCE_PBF to downloaded .osm.pbf}"
: "${OUTPUT_DIR:=staging/processed}"
: "${BBOX:=-122.46,47.48,-122.22,47.74}"
: "${MAX_FEATURES:=10000}"
[[ -f "$SOURCE_PBF" ]] || { echo "Missing source: $SOURCE_PBF" >&2; exit 1; }
[[ "$MAX_FEATURES" =~ ^[0-9]+$ ]] && ((MAX_FEATURES>=1 && MAX_FEATURES<=50000)) || { echo "Invalid MAX_FEATURES" >&2; exit 1; }
IFS=',' read -r west south east north <<< "$BBOX"
[[ -n "$west" && -n "$south" && -n "$east" && -n "$north" ]] || { echo "Invalid BBOX" >&2; exit 1; }
command -v ogr2ogr >/dev/null || { echo "Install GDAL ogr2ogr" >&2; exit 1; }
mkdir -p "$OUTPUT_DIR"
# GeoJSONSeq keeps processing output bounded. Layers reflect GDAL's OSM driver schema.
for layer in lines multipolygons points; do
  echo "Processing $layer within $BBOX (cap $MAX_FEATURES)"
  ogr2ogr -f GeoJSONSeq "$OUTPUT_DIR/$layer.geojsonl" "$SOURCE_PBF" "$layer" \
    -spat "$west" "$south" "$east" "$north" \
    -limit "$MAX_FEATURES" -lco RS=NO -skipfailures
  gzip -f "$OUTPUT_DIR/$layer.geojsonl"
done
python3 - "$OUTPUT_DIR" "$BBOX" "$MAX_FEATURES" <<'PY'
import json, pathlib, sys
root=pathlib.Path(sys.argv[1])
manifest={"schema":"convergence-osm-pilot-v1","bbox_wgs84":list(map(float,sys.argv[2].split(","))),"max_features_per_layer":int(sys.argv[3]),"source":"OpenStreetMap contributors / authorized regional extract","license":"ODbL 1.0","layers":{},"notes":"Bounded exploratory extracts; features can be truncated at cap. Not comprehensive, not terrain elevation, not production vector tiles."}
import gzip
for name in ("lines","multipolygons","points"):
    path=root/f"{name}.geojsonl.gz"
    with gzip.open(path,"rt",encoding="utf-8") as f:
        count=sum(1 for line in f if line.strip())
    manifest["layers"][name]={"file":path.name,"features":count,"possibly_truncated":count>=int(sys.argv[3])}
(root/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(json.dumps(manifest,indent=2))
PY

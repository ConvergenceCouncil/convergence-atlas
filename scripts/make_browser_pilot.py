#!/usr/bin/env python3
"""Build a capped GeoJSON preview from GDAL GeoJSONSeq regional extracts."""
import argparse,gzip,json
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument("--input",required=True)
p.add_argument("--output",required=True)
p.add_argument("--max-features",type=int,default=2500)
p.add_argument("--max-bytes",type=int,default=4000000)
a=p.parse_args()
if a.max_features<1 or a.max_bytes<1000: p.error("Invalid limits")
features=[]
for layer in ("lines","multipolygons","points"):
    path=Path(a.input)/(layer+".geojsonl.gz")
    if not path.exists(): continue
    with gzip.open(path,"rt",encoding="utf-8") as f:
        for line in f:
            if len(features)>=a.max_features: break
            obj=json.loads(line)
            if obj.get("type")!="Feature" or not obj.get("geometry"): continue
            props=obj.get("properties") or {}
            obj["properties"]={k:props.get(k) for k in ("name","highway","railway","waterway","building","landuse") if props.get(k) is not None}
            obj["properties"]["source_layer"]=layer
            features.append(obj)
data={"type":"FeatureCollection","metadata":{"source":"OpenStreetMap contributors","license":"ODbL 1.0","coverage":"bounded Seattle pilot; sampled and potentially truncated","complete":False},"features":features}
def encode():return json.dumps(data,separators=(",",":"),ensure_ascii=False).encode("utf-8")
blob=encode()
while len(blob)>a.max_bytes and features:
    features=features[:max(0,int(len(features)*.8))]
    data["features"]=features
    blob=encode()
target=Path(a.output)
target.parent.mkdir(parents=True,exist_ok=True)
target.write_bytes(blob)
print("Preview features:",len(features),"bytes:",len(blob))

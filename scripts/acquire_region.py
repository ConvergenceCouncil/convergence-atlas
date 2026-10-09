#!/usr/bin/env python3
"""Acquire an authorized regional OpenStreetMap extract with provenance and checksums.

This downloader does not scrape map tile services or the Overpass API.
It deliberately requires an explicit HTTPS URL and license acknowledgment.
"""
import argparse
import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--url",required=True,help="Official HTTPS extract download URL")
    p.add_argument("--output",required=True,help="Destination .osm.pbf path")
    p.add_argument("--source",required=True)
    p.add_argument("--license",required=True)
    p.add_argument("--region",required=True)
    p.add_argument("--max-gb",type=float,default=5)
    p.add_argument("--accept-license",action="store_true",required=True)
    args=p.parse_args()
    parsed=urlparse(args.url)
    if parsed.scheme!="https" or not parsed.hostname or parsed.username or parsed.password:
        p.error("URL must be HTTPS with a valid hostname and no embedded credentials")
    if not args.output.endswith(".osm.pbf"):
        p.error("Output must end in .osm.pbf")
    if args.max_gb<=0:
        p.error("--max-gb must be positive")
    limit=int(args.max_gb*1024**3)
    target=Path(args.output)
    target.parent.mkdir(parents=True,exist_ok=True)
    temp=target.with_suffix(target.suffix+".partial")
    digest=hashlib.sha256()
    size=0
    try:
        request=urllib.request.Request(args.url,headers={"User-Agent":"CONVERGENCE-Earth-Atlas/1.0 (authorized dataset ingestion)"})
        with urllib.request.urlopen(request,timeout=90) as response, temp.open("wb") as out:
            declared=response.headers.get("Content-Length")
            if declared and int(declared)>limit:
                raise ValueError("Download exceeds configured size limit")
            while True:
                chunk=response.read(1024*1024)
                if not chunk: break
                size+=len(chunk)
                if size>limit: raise ValueError("Download exceeds configured size limit")
                digest.update(chunk)
                out.write(chunk)
        temp.replace(target)
    finally:
        if temp.exists(): temp.unlink()
    manifest={"schema":"convergence-source-download-v1","region":args.region,"source":args.source,"license":args.license,"url":args.url,"retrieved_utc":datetime.now(timezone.utc).isoformat(),"path":str(target),"bytes":size,"sha256":digest.hexdigest(),"format":"osm.pbf","status":"downloaded_unprocessed","notes":"Raw extract is not a terrain DEM or game-ready mesh. Review ODbL obligations before publication."}
    metadata=target.with_suffix(target.suffix+".source.json")
    metadata.write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print(f"Downloaded {size:,} bytes to {target}; SHA-256 {digest.hexdigest()}")

if __name__=="__main__":
    main()

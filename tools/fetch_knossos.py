#!/usr/bin/env python3
"""Discover and optionally download Knossos room assets from Zenodo's official API.

Usage:
  python3 tools/fetch_knossos.py --list
  python3 tools/fetch_knossos.py --download "Throne Room" --out assets/knossos
  python3 tools/fetch_knossos.py --download "Grand Staircase" --out assets/knossos

Downloads require a large amount of disk space. Does not assert asset rights or gameplay readiness.
"""
import argparse, hashlib, json, pathlib, urllib.request, urllib.parse
API="https://zenodo.org/api/records/7752061"
def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"CONVERGENCE-asset-research/1.0","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:return json.load(r)
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--list",action="store_true")
    p.add_argument("--download",metavar="NAME_FRAGMENT")
    p.add_argument("--out",default="assets/knossos")
    args=p.parse_args()
    record=get_json(API)
    files=record.get("files",[])
    print("Record:",record.get("id"),"Title:",record.get("metadata",{}).get("title"))
    print("Record license metadata:",json.dumps(record.get("metadata",{}).get("license"),ensure_ascii=False))
    matches=[f for f in files if not args.download or args.download.lower() in f.get("key","").lower()]
    for f in matches:
        print(json.dumps({"name":f.get("key"),"size_MB":round(f.get("size",0)/1e6,1),"checksum":f.get("checksum"),"url":f.get("links",{}).get("self")},ensure_ascii=False))
    if not args.download:return
    if len(matches)!=1:raise SystemExit("Expected exactly one matching file; refine --download (matches: %d)"%len(matches))
    item=matches[0];url=item.get("links",{}).get("self")
    if not url or not url.startswith("https://"):raise SystemExit("Missing HTTPS download URL")
    dest=pathlib.Path(args.out);dest.mkdir(parents=True,exist_ok=True)
    name=pathlib.PurePosixPath(item["key"]).name
    target=dest/name
    if target.exists():raise SystemExit("File already exists; will not overwrite: "+str(target))
    partial=target.with_name(target.name+".part")
    req=urllib.request.Request(url,headers={"User-Agent":"CONVERGENCE-asset-research/1.0"})
    try:
        with urllib.request.urlopen(req,timeout=120) as src,open(partial,"wb") as dst:
            digest=hashlib.md5()
            while True:
                block=src.read(1024*1024)
                if not block:break
                dst.write(block);digest.update(block)
        checksum=item.get("checksum","")
        if checksum.startswith("md5:") and digest.hexdigest()!=checksum.split(":",1)[1]:
            raise ValueError("Checksum mismatch: downloaded asset was not saved")
        if item.get("size") and partial.stat().st_size!=item["size"]:
            raise ValueError("Size mismatch")
        partial.rename(target)
    except Exception:
        partial.unlink(missing_ok=True)
        raise
    print("Downloaded:",target,"bytes:",target.stat().st_size)
    print("Next: python3 tools/audit_architecture.py",str(target))
    print("Do not publish without checking source license, mobile performance and collision.")
if __name__=="__main__":main()

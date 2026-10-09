#!/usr/bin/env python3
"""Create a bounded, attributed DEM GeoTIFF from AWS Terrarium elevation tiles.

Dependencies: pip install requests numpy rasterio pillow
Example: python scripts/export_terrarium_dem.py --bbox -122.45 47.50 -122.20 47.72 --zoom 11 --output seattle-dem.tif
"""
import argparse, hashlib, io, json, math, pathlib, datetime
import numpy as np
import requests
import rasterio
from rasterio.transform import from_bounds
from PIL import Image

MAX_TILES = 64
def tile_x(lon,z): return (lon+180)/360*(2**z)
def tile_y(lat,z):
    lat=max(-85.05112878,min(85.05112878,lat))
    return (1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*(2**z)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bbox',nargs=4,type=float,required=True,metavar=('WEST','SOUTH','EAST','NORTH'))
    p.add_argument('--zoom',type=int,default=11)
    p.add_argument('--output',type=pathlib.Path,required=True)
    a=p.parse_args()
    west,south,east,north=a.bbox
    if not (-180<=west<east<=180 and -85<=south<north<=85):p.error('invalid bbox')
    if not 0<=a.zoom<=13:p.error('zoom must be 0..13')
    n=2**a.zoom
    x0=max(0,int(math.floor(tile_x(west,a.zoom))));x1=min(n-1,int(math.floor(tile_x(east,a.zoom))))
    y0=max(0,int(math.floor(tile_y(north,a.zoom))));y1=min(n-1,int(math.floor(tile_y(south,a.zoom))))
    count=(x1-x0+1)*(y1-y0+1)
    if count>MAX_TILES:p.error(f'{count} tiles exceeds safety cap of {MAX_TILES}; reduce bbox or zoom')
    pixels=np.empty(((y1-y0+1)*256,(x1-x0+1)*256),dtype=np.float32)
    session=requests.Session();session.headers['User-Agent']='CONVERGENCE-Earth-Atlas-DEM-research/1.0'
    checksums=[]
    for y in range(y0,y1+1):
        for x in range(x0,x1+1):
            url=f'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{a.zoom}/{x}/{y}.png'
            response=session.get(url,timeout=45);response.raise_for_status()
            raw=response.content
            rgb=np.asarray(Image.open(io.BytesIO(raw)).convert('RGB'),dtype=np.float32)
            pixels[(y-y0)*256:(y-y0+1)*256,(x-x0)*256:(x-x0+1)*256]=rgb[:,:,0]*256+rgb[:,:,1]+rgb[:,:,2]/256-32768
            checksums.append({'z':a.zoom,'x':x,'y':y,'sha256':hashlib.sha256(raw).hexdigest()})
    def longitude(x):return x/n*360-180
    def latitude(y):return math.degrees(math.atan(math.sinh(math.pi*(1-2*y/n))))
    bounds=(longitude(x0),latitude(y1+1),longitude(x1+1),latitude(y0))
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with rasterio.open(a.output,'w',driver='GTiff',height=pixels.shape[0],width=pixels.shape[1],count=1,dtype='float32',crs='EPSG:4326',transform=from_bounds(*bounds,pixels.shape[1],pixels.shape[0]),compress='deflate',predictor=3) as dst:dst.write(pixels,1)
    manifest={'dataset':'Mapzen terrain tiles on AWS (Terrarium encoding)','source':'https://registry.opendata.aws/terrain-tiles/','url_template':'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png','retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'requested_bbox_wsen':a.bbox,'output_bounds_wsen':bounds,'zoom':a.zoom,'tile_count':count,'crs':'EPSG:4326','elevation_units':'meters','vertical_datum':'source dataset mixed/unspecified; verify before precise engineering use','license_note':'Check source dataset terms and attribution before redistribution or commercial asset use','tiles':checksums,'output_sha256':hashlib.sha256(a.output.read_bytes()).hexdigest()}
    a.output.with_suffix('.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'Created {a.output} ({pixels.shape[1]}x{pixels.shape[0]}, {count} tiles)')

if __name__=='__main__':main()

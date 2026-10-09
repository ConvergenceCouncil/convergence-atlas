#!/usr/bin/env python3
"""Reproject a DEM into a metric CRS and export a square UE5 heightmap.

Example: python scripts/dem_to_ue5_metric.py --input output/seattle-dem.tif --output output/seattle-metric-ue5.png --epsg 32610 --size 505
"""
import argparse,hashlib,json,pathlib
import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform,reproject,Resampling
from rasterio.transform import array_bounds
from PIL import Image

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--input',type=pathlib.Path,required=True)
 p.add_argument('--output',type=pathlib.Path,required=True)
 p.add_argument('--epsg',type=int,default=32610,help='Metric projected EPSG; Seattle UTM zone 10N = 32610')
 p.add_argument('--size',type=int,default=505)
 a=p.parse_args()
 if a.size<64 or (a.size-1)%63:p.error('size must be 63*N+1')
 with rasterio.open(a.input) as src:
  if src.count!=1:p.error('DEM must have one band')
  crs=rasterio.crs.CRS.from_epsg(a.epsg)
  if not crs.is_projected:p.error('target CRS must be projected')
  transform,width,height=calculate_default_transform(src.crs,crs,src.width,src.height,*src.bounds)
  # Fit projected rectangular extent into a square vertex grid. Keep X and Y
  # scales separate to preserve real geographic distances without blank corners.
  west,south,east,north=array_bounds(height,width,transform)
  metric_bounds=(west,south,east,north)
  dst_transform=rasterio.transform.from_bounds(*metric_bounds,a.size,a.size)
  target=np.full((a.size,a.size),np.nan,dtype=np.float32)
  reproject(source=rasterio.band(src,1),destination=target,src_transform=src.transform,src_crs=src.crs,dst_transform=dst_transform,dst_crs=crs,src_nodata=src.nodata,dst_nodata=np.nan,resampling=Resampling.bilinear)
 if not np.isfinite(target).all():
  p.error('projected extent contains uncovered pixels; expand DEM coverage or handle no-data explicitly')
 minimum=float(target.min());maximum=float(target.max())
 pad=max(1,(maximum-minimum)*.02);low=minimum-pad;high=maximum+pad
 encoded=np.clip(np.rint((target-low)/(high-low)*65535),0,65535).astype(np.uint16)
 a.output.parent.mkdir(parents=True,exist_ok=True)
 Image.fromarray(encoded).save(a.output)
 zscale=(high-low)*100*128/65535
 meta={'input':str(a.input),'output':str(a.output),'crs':str(crs),'size':[a.size,a.size],
 'metric_bounds_projected':metric_bounds,'horizontal_meters_per_vertex_x':(east-west)/(a.size-1),'horizontal_meters_per_vertex_y':(north-south)/(a.size-1),
 'unreal_x_scale_percent':(east-west)/(a.size-1)*100,'unreal_y_scale_percent':(north-south)/(a.size-1)*100,'unreal_z_scale_percent':zscale,
 'unreal_actor_z_offset_cm':(low+high)*50,
 'min_elevation_m':minimum,'max_elevation_m':maximum,
 'vertical_datum_note':'Source vertical datum must be checked before precision placement',
 'png_sha256':hashlib.sha256(a.output.read_bytes()).hexdigest()}
 a.output.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
 print('Created metric UE5 heightmap:',a.output,'meters/vertex:',meta['horizontal_meters_per_vertex_x'])

if __name__=='__main__':main()

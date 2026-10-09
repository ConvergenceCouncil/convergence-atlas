#!/usr/bin/env python3
"""Convert a geographic DEM into a UE5-compatible 16-bit grayscale landscape heightmap.

Example:
 python scripts/dem_to_ue5.py --input output/seattle-dem.tif --output output/seattle-ue5.png
The output is a geographic prototype; for production, reproject to a metric CRS first.
"""
import argparse, hashlib, json, math, pathlib
import numpy as np
import rasterio
from rasterio.enums import Resampling
from PIL import Image

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',required=True,type=pathlib.Path)
    p.add_argument('--output',required=True,type=pathlib.Path)
    p.add_argument('--size',type=int,default=505,help='UE5 landscape vertices per side; default 505 = 8*63+1')
    a=p.parse_args()
    if a.size<64 or (a.size-1)%63!=0: p.error('size must equal 63*N+1 (e.g. 253, 505, 1009)')
    with rasterio.open(a.input) as src:
        if src.count!=1:p.error('DEM must contain exactly one band')
        data=src.read(1,out_shape=(a.size,a.size),resampling=Resampling.bilinear,masked=True)
        if np.ma.is_masked(data) and np.any(np.ma.getmaskarray(data)):p.error('DEM contains no-data pixels; fill explicitly before exporting')
        values=np.asarray(data,dtype=np.float64)
        if not np.isfinite(values).all():p.error('DEM contains non-finite values')
        bounds=[src.bounds.left,src.bounds.bottom,src.bounds.right,src.bounds.top]
        crs=str(src.crs)
    minimum=float(values.min());maximum=float(values.max())
    # Add a modest guard band, preventing cliffs from clipping at the exact data extrema.
    padding=max(1.0,(maximum-minimum)*0.02)
    low=minimum-padding;high=maximum+padding
    raw=np.clip(np.rint((values-low)/(high-low)*65535),0,65535).astype('<u2')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    Image.fromarray(raw).save(a.output)
    # UE Landscape: centimeters = (raw - 32768) * ZScale / 128.
    z_scale=(high-low)*100*128/65535
    center_m=(low+high)/2
    metadata={'input':str(a.input),'output':str(a.output),'dimensions_px':[a.size,a.size],
      'pixel_format':'unsigned 16-bit grayscale PNG','original_crs':crs,'original_bounds_wsen':bounds,
      'source_min_m':minimum,'source_max_m':maximum,'encoded_low_m':low,'encoded_high_m':high,
      'unreal_z_scale_percent':z_scale,'unreal_actor_z_offset_cm':center_m*100,
      'unreal_height_formula_cm':'(pixel_value - 32768) * ZScale / 128 + actor_z_offset_cm',
      'horizontal_warning':'Geographic raster spacing is angular, not meters. Reproject into local projected metric CRS and calculate X/Y scale before game use.',
      'vertical_warning':'Verify source vertical datum and sea-level reference before combining DEMs.',
      'png_sha256':hashlib.sha256(a.output.read_bytes()).hexdigest()}
    a.output.with_suffix('.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(f'Wrote {a.output} ({a.size}x{a.size}); elevation {minimum:.2f}..{maximum:.2f} m; UE Z scale {z_scale:.4f}%')

if __name__=='__main__':main()

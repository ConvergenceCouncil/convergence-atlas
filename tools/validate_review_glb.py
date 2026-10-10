#!/usr/bin/env python3
"""Reject review GLBs that exceed texture/transfer budgets or lose scan faces."""
import argparse,hashlib,io,json,pathlib,struct
from PIL import Image

def verify(path,triangles=260678,texture_max=2048,max_bytes=60_000_000):
 data=path.read_bytes()
 if len(data)>max_bytes:raise ValueError('Review transfer budget exceeded')
 if data[:4]!=b'glTF' or struct.unpack_from('<II',data,4)!=(2,len(data)):raise ValueError('Invalid GLB header')
 offset=12;doc=None;binary=None
 while offset+8<=len(data):
  length,kind=struct.unpack_from('<II',data,offset);offset+=8
  if offset+length>len(data):raise ValueError('Chunk overflow')
  chunk=data[offset:offset+length];offset+=length
  if kind==0x4e4f534a:doc=json.loads(chunk)
  elif kind==0x004e4942:binary=chunk
 if not doc or binary is None:raise ValueError('Missing GLB chunks')
 if doc.get('extensionsRequired'):raise ValueError('Unexpected required compression extension')
 faces=0
 for mesh in doc.get('meshes',[]):
  for p in mesh['primitives']:
   if p.get('mode',4)!=4:raise ValueError('Expected triangle primitives')
   if 'indices' not in p:raise ValueError('Expected indexed mesh')
   faces+=doc['accessors'][p['indices']]['count']//3
 if faces!=triangles:raise ValueError(f'Geometry count changed: {faces} != {triangles}')
 images=[]
 for image in doc.get('images',[]):
  if 'bufferView' not in image:raise ValueError('Expected self-contained texture')
  view=doc['bufferViews'][image['bufferView']];start=view.get('byteOffset',0)
  with Image.open(io.BytesIO(binary[start:start+view['byteLength']])) as decoded:
   size=list(decoded.size)
   if max(size)>texture_max:raise ValueError(f'Texture budget exceeded: {size}')
   images.append(size)
 if not images:raise ValueError('Missing source texture')
 return {'file':path.name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'triangles':faces,'textureSizes':images,'geometryDecimated':False,'transferTarget60MBPassed':True,'runtimeOnIPhoneVerified':False,'status':'review-only'}

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('file',type=pathlib.Path);p.add_argument('--triangles',type=int,default=260678);p.add_argument('--texture-max',type=int,default=2048);a=p.parse_args();print(json.dumps(verify(a.file,a.triangles,a.texture_max),indent=2))

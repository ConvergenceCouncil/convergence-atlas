#!/usr/bin/env python3
"""Inspect a downloaded glTF 2.0 architectural asset before Atlas approval.
Usage: python3 tools/audit_architecture.py path/to/building.gltf
       python3 tools/audit_architecture.py path/to/building.glb
No third-party dependencies. This is metadata/geometry structure QA, NOT proof of traversal.
"""
import json, struct, sys, pathlib, collections
def load(path):
    data=path.read_bytes()
    if path.suffix.lower()=='.glb':
        if data[:4]!=b'glTF' or len(data)<20: raise ValueError('Invalid GLB header')
        version,total=struct.unpack_from('<II',data,4)
        if version!=2 or total!=len(data): raise ValueError('GLB version or size mismatch')
        offset=12
        while offset+8<=len(data):
            size,kind=struct.unpack_from('<II',data,offset);offset+=8
            if offset+size>len(data): raise ValueError('GLB chunk overflow')
            if kind==0x4e4f534a:return json.loads(data[offset:offset+size])
            offset+=size
        raise ValueError('GLB has no JSON chunk')
    return json.loads(data.decode('utf-8'))
def main():
    path=pathlib.Path(sys.argv[1]); g=load(path)
    if str(g.get('asset',{}).get('version','')).split('.')[0]!='2':raise ValueError('Not glTF 2.x')
    nodes=g.get('nodes',[]); meshes=g.get('meshes',[]); materials=g.get('materials',[])
    names=[str(n.get('name','')) for n in nodes]
    markers={k:[n for n in names if k in n.lower()] for k in ('floor','stair','door','room','collision','navmesh','entrance')}
    tris=0
    for mesh in meshes:
        for p in mesh.get('primitives',[]):
            mode=p.get('mode',4)
            if mode!=4:continue
            acc=g.get('accessors',[])
            ix=p.get('indices'); pos=p.get('attributes',{}).get('POSITION')
            if isinstance(ix,int) and ix<len(acc):tris+=acc[ix].get('count',0)//3
            elif isinstance(pos,int) and pos<len(acc):tris+=acc[pos].get('count',0)//3
    images=g.get('images',[]);textures=g.get('textures',[])
    report={'file':str(path),'nodes':len(nodes),'meshes':len(meshes),'triangles_estimate':tris,
        'materials':len(materials),'textures':len(textures),'images':len(images),
        'markers':markers,'external_files':[x.get('uri') for x in g.get('buffers',[])+images if x.get('uri') and not x['uri'].startswith('data:')],
        'pass':'STRUCTURE_ONLY','not_verified':['interior completeness','room connectivity','walkable floor surfaces','stairs and doors clearance','collision','real-world dimensions','licensing','mobile frame rate']}
    print(json.dumps(report,indent=2))
if __name__=='__main__':
    if len(sys.argv)!=2:sys.exit('Usage: audit_architecture.py model.gltf|model.glb')
    main()

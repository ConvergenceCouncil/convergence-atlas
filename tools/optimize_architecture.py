#!/usr/bin/env python3
"""Create a review-only mobile GLB from a downloaded architectural GLB.

Usage:
 blender -b -P tools/optimize_architecture.py -- input.glb output-mobile.glb --ratio 0.35 --texture-max 2048

WARNING: automated decimation can damage thin walls, doorways, stairs, frescoes and collision.
Never replace a source master. Compare output against original before use.
"""
import bpy, sys, os, json, math
from pathlib import Path
argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if len(argv)<2:raise SystemExit(__doc__)
source,output=map(os.path.abspath,argv[:2])
if not os.path.isfile(source) or not source.lower().endswith('.glb'):raise SystemExit('Input must be an existing GLB')
if not output.lower().endswith('.glb') or source==output:raise SystemExit('Output must be a different .glb file')
ratio=.35;texmax=2048
for i,a in enumerate(argv[2:],2):
 if a=='--ratio':ratio=float(argv[i+1])
 if a=='--texture-max':texmax=int(argv[i+1])
if not (0.05<=ratio<=1):raise SystemExit('ratio must be 0.05..1')
if not (256<=texmax<=8192):raise SystemExit('texture-max must be 256..8192')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=source)
meshes=[o for o in bpy.data.objects if o.type=='MESH']
if not meshes:raise SystemExit('No meshes in source GLB')
before=sum(len(o.data.polygons) for o in meshes)
changed=[]
for obj in meshes:
 if len(obj.data.polygons)<200:continue
 # Preserve obvious thin structural objects from automatic decimation.
 if any(k in obj.name.lower() for k in ('stair','door','floor','collision','navmesh','railing')):
  continue
 bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
 modifier=obj.modifiers.new('CONVERGENCE preview reduction','DECIMATE');modifier.ratio=ratio
 try:
  bpy.ops.object.modifier_apply(modifier=modifier.name);changed.append(obj.name)
 except RuntimeError:
  obj.modifiers.remove(modifier)
resized=[]
for image in bpy.data.images:
 if image.source not in {'FILE','GENERATED'} or not image.has_data:continue
 w,h=image.size
 if max(w,h)>texmax:
  scale=texmax/max(w,h)
  image.scale(max(1,int(w*scale)),max(1,int(h*scale)))
  resized.append(image.name)
after=sum(len(o.data.polygons) for o in meshes)
Path(output).parent.mkdir(parents=True,exist_ok=True)
bpy.ops.export_scene.gltf(filepath=output,export_format='GLB',export_materials='EXPORT')
print(json.dumps({'source':source,'output':output,'mesh_count':len(meshes),'triangles_before_estimate':before,'triangles_after_estimate':after,'reduced_objects':len(changed),'resized_images':resized,'warning':'Visual preview only; geometry and traversal QA required'},indent=2))

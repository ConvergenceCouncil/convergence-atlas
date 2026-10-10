#!/usr/bin/env python3
"""Blender background conversion: blender -b -P tools/convert_fbx_to_glb.py -- input.fbx output.glb
Uses Blender's FBX import and glTF exporter. Source textures must be accessible.
"""
import bpy,sys,os,json
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if len(args)!=2:raise SystemExit('Usage: blender -b -P tools/convert_fbx_to_glb.py -- input.fbx output.glb')
src,dst=map(os.path.abspath,args)
if not os.path.isfile(src):raise SystemExit('Missing FBX: '+src)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=src,use_image_search=True)
meshes=[o for o in bpy.data.objects if o.type=='MESH']
if not meshes:raise SystemExit('FBX contains no mesh objects')
for obj in meshes:
    if obj.scale[:]!= (1,1,1):
        bpy.context.view_layer.objects.active=obj
        obj.select_set(True)
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        obj.select_set(False)
missing=[]
for image in bpy.data.images:
    if image.source=='FILE' and not image.packed_file:
        path=bpy.path.abspath(image.filepath)
        if not os.path.isfile(path):missing.append({'name':image.name,'path':path})
if missing:
    print(json.dumps({'missing_textures':missing},indent=2))
    raise SystemExit('Missing source textures. Aborting rather than silently exporting untextured architecture.')
os.makedirs(os.path.dirname(dst),exist_ok=True)
bpy.ops.export_scene.gltf(filepath=dst,export_format='GLB',export_apply=True,export_materials='EXPORT')
print(json.dumps({'source':src,'output':dst,'mesh_count':len(meshes),'objects':len(bpy.data.objects),'textures':len(bpy.data.images)},indent=2))

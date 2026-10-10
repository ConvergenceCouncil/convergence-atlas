import bpy,json,math,sys
from pathlib import Path
from PIL import Image
import numpy as np
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if len(args)!=1:raise SystemExit('Usage: blender -b --python-exit-code 1 -P tools/build_terrain_review.py -- DIRECTORY_WITH_HEIGHTMAP_AND_JSON')
root=Path(args[0]).resolve()
meta=json.loads((root/'seattle-center-ue5.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True)
arr=np.asarray(Image.open(root/'seattle-center-ue5.png').convert('F').resize((129,129),Image.Resampling.BILINEAR),dtype=float)
height=(arr-32768)*meta['unreal_z_scale_percent']/128/100+meta['unreal_actor_z_offset_cm']/100
bounds=meta['metric_bounds_projected'];width=bounds[2]-bounds[0];depth=bounds[3]-bounds[1]
verts=[(x/128*width-width/2,depth/2-y/128*depth,float(height[y,x])) for y in range(129) for x in range(129)]
faces=[(y*129+x,y*129+x+129,y*129+x+130,y*129+x+1) for y in range(128) for x in range(128)]
mesh=bpy.data.meshes.new('Seattle_Center_DEM_Review');mesh.from_pydata(verts,[],faces);mesh.update();obj=bpy.data.objects.new('Seattle_Center_Sourced_Terrain_Review',mesh);bpy.context.collection.objects.link(obj)
mat=bpy.data.materials.new('Elevation review surface');mat.diffuse_color=(.24,.39,.33,1);mat.use_nodes=True;bsdf=mat.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=(.24,.39,.33,1);bsdf.inputs['Roughness'].default_value=.95;obj.data.materials.append(mat)
obj['source']='Mapzen Terrain Tiles on AWS; bounded Seattle Center sample';obj['coordinate_system']='EPSG:32610; local origin at extent center, meters';obj['elevation_datum']='Unverified; no terrain deformation or buildings added';obj['detail_note']='129x129 preview resamples source; no new geographic detail implied'
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
bpy.ops.export_scene.gltf(filepath=str(root/'seattle-center-terrain-review.glb'),export_format='GLB')
bpy.ops.object.camera_add(location=(width*.95,-depth*.95,650));cam=bpy.context.object;target=Vector((0,0,30));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.clip_end=10000;cam.data.type='ORTHO';cam.data.ortho_scale=max(width,depth)*1.45;bpy.context.scene.camera=cam
bpy.ops.object.light_add(type='SUN',location=(0,0,1000));bpy.context.object.rotation_euler=(math.radians(25),math.radians(-20),math.radians(-30));bpy.context.object.data.energy=3
scene=bpy.context.scene;scene.world=bpy.data.worlds.new('Review world');scene.world.color=(.14,.18,.24);scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=16;scene.cycles.use_denoising=False;scene.render.resolution_x=960;scene.render.resolution_y=720;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.render.filepath=str(root/'seattle-center-terrain-review.png')
bpy.ops.wm.save_as_mainfile(filepath=str(root/'seattle-center-terrain-review.blend'),compress=True)
bpy.ops.render.render(write_still=True)
print('Terrain review created; source elevation, geographic scale and local origin retained.')

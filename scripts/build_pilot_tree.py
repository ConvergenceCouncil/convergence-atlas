"""Original generic broadleaf proxy, 8m tall. Not a species reconstruction."""
import sys
# Debian Blender may need system extension modules when embedded in a managed runtime.
for extra in ('/usr/lib/python3.12/lib-dynload','/usr/lib/python3/dist-packages'):
    if pathlib_check := __import__('os').path.isdir(extra): sys.path.append(extra)
import bpy, math, random, pathlib
from mathutils import Vector
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
rng=random.Random(82)
def material(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=.94
    return m
bark=material('Warm bark',(.16,.11,.067))
greens=[material('Leaf tone '+str(i),c) for i,c in enumerate([(.085,.18,.065),(.12,.25,.085),(.17,.31,.11),(.22,.36,.14)])]
def branch(a,b,r):
    a,b=Vector(a),Vector(b);bpy.ops.mesh.primitive_cone_add(vertices=8,radius1=r,radius2=r*.35,depth=(b-a).length,location=(a+b)/2)
    o=bpy.context.object;o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();o.data.materials.append(bark)
branch((0,0,0),(0,0,5.8),.22)
for i in range(9):
    angle=i*2.399;rad=1.1+(.55 if i<6 else 0);z=4.5+(i%3)*.8
    x,y=math.cos(angle)*rad,math.sin(angle)*rad
    branch((0,0,2.6+(i%3)*.7),(x,y,z),.075)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=(x,y,z+.55))
    o=bpy.context.object;o.scale=(1.5,1.35,1.75)
    for v in o.data.vertices: v.co*=rng.uniform(.86,1.14)
    for m in greens:o.data.materials.append(m)
    for p in o.data.polygons:p.material_index=rng.randrange(4);p.use_smooth=True
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
bpy.ops.object.join();o=bpy.context.object
max_z=max((o.matrix_world@v.co).z for v in o.data.vertices)
o.scale=(8/max_z,)*3;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
bpy.context.scene.cursor.location=(0,0,0);bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
path=pathlib.Path(__file__).resolve().parents[1]/'assets/pilot-broadleaf.glb'
bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_yup=True)
print('TREE_TRIANGLES',sum(len(p.vertices)-2 for p in o.data.polygons),'HEIGHT_METERS',8,'BYTES',path.stat().st_size)

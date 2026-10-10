import io,json,os,pathlib,shutil,struct,subprocess,tempfile,unittest
class TextureResizeTest(unittest.TestCase):
 @unittest.skipUnless(shutil.which('blender'),'Blender integration requires toolkit')
 def test_packed_texture_resized_without_changing_mesh(self):
  try:from PIL import Image
  except ImportError:self.skipTest('Pillow required')
  repo=pathlib.Path(__file__).resolve().parents[1]
  with tempfile.TemporaryDirectory() as directory:
   root=pathlib.Path(directory);source=root/'source.glb';output=root/'review.glb';setup=root/'setup.py'
   setup.write_text("import bpy\nbpy.ops.wm.read_factory_settings(use_empty=True)\nbpy.ops.mesh.primitive_cube_add()\nobj=bpy.context.object\nmat=bpy.data.materials.new('Textured');mat.use_nodes=True\nim=bpy.data.images.new('Packed source',width=512,height=512);im.generated_color=(.2,.4,.6,1);im.pack()\nnode=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=im\nmat.node_tree.links.new(node.outputs['Color'],mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color']);obj.data.materials.append(mat)\nbpy.ops.export_scene.gltf(filepath="+repr(str(source))+",export_format='GLB')\n")
   env=dict(os.environ);env['PATH']='/usr/bin:/bin:'+env.get('PATH','')
   def run(script,*args):subprocess.run(['blender','-b','--python-exit-code','1','-P',str(script),*args],env=env,check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
   run(setup);run(repo/'tools/optimize_architecture.py','--',str(source),str(output),'--ratio','1','--texture-max','256','--image-format','JPEG')
   data=output.read_bytes();length,kind=struct.unpack_from('<II',data,12);doc=json.loads(data[20:20+length]);start=28+length;view=doc['bufferViews'][doc['images'][0]['bufferView']];start+=view.get('byteOffset',0)
   with Image.open(io.BytesIO(data[start:start+view['byteLength']])) as image:self.assertEqual(image.size,(256,256))
   index=doc['meshes'][0]['primitives'][0]['indices'];self.assertEqual(doc['accessors'][index]['count']//3,12)

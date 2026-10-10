import importlib.util,io,json,pathlib,struct,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
try:from PIL import Image
except ImportError:Image=None
@unittest.skipUnless(Image,'Pillow required')
class ReviewBudgetTests(unittest.TestCase):
 def test_rejects_oversize_texture_and_changed_face_count(self):
  spec=importlib.util.spec_from_file_location('review',ROOT/'tools/validate_review_glb.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  image=io.BytesIO();Image.new('RGB',(512,512)).save(image,format='PNG');binary=image.getvalue();binary+=b'\0'*(-len(binary)%4)
  doc={'accessors':[{'count':36}],'meshes':[{'primitives':[{'indices':0}]}],'bufferViews':[{'byteLength':len(image.getvalue())}],'images':[{'bufferView':0}]};raw=json.dumps(doc).encode();raw+=b' '*(-len(raw)%4);data=b'glTF'+struct.pack('<II',2,28+len(raw)+len(binary))+struct.pack('<II',len(raw),0x4e4f534a)+raw+struct.pack('<II',len(binary),0x004e4942)+binary
  with tempfile.TemporaryDirectory() as temp:
   path=pathlib.Path(temp)/'review.glb';path.write_bytes(data)
   with self.assertRaisesRegex(ValueError,'Texture budget'):module.verify(path,12,256)
   with self.assertRaisesRegex(ValueError,'Geometry count'):module.verify(path,13,512)
   self.assertEqual(module.verify(path,12,512)['textureSizes'],[[512,512]])

import json,pathlib,subprocess,sys,tempfile,unittest
class EarthBaselineTests(unittest.TestCase):
 def test_all_committed_vectors_validate(self):
  root=pathlib.Path(__file__).resolve().parents[1]
  with tempfile.TemporaryDirectory() as directory:
   output=pathlib.Path(directory)/'inventory.json'
   subprocess.run([sys.executable,str(root/'scripts/validate_earth.py'),'--output',str(output)],cwd=root,check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
   inventory=json.loads(output.read_text());self.assertEqual(len(inventory['files']),9)

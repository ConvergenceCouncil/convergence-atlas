import pathlib,subprocess,sys,unittest
class EarthBaselineTests(unittest.TestCase):
 def test_all_committed_vectors_validate(self):
  root=pathlib.Path(__file__).resolve().parents[1]
  subprocess.run([sys.executable,str(root/'scripts/validate_earth.py')],cwd=root,check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)

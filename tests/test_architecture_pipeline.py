import json,struct,tempfile,unittest
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('audit',ROOT/'tools/audit_architecture.py');audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
class ArchitecturePipelineTests(unittest.TestCase):
 def test_rejects_negative_accessor_index(self):
  self.assertIsNone(audit.accessor_bounds({'accessors':[{'min':[0,0,0],'max':[1,1,1]}]},-1))
 def test_rejects_nonfinite_bounds(self):
  with self.assertRaises(ValueError):audit.accessor_bounds({'accessors':[{'min':[0,0,float('nan')],'max':[1,1,1]}]},0)
 def test_optimizer_supports_texture_only_jpeg_copy(self):
  source=(ROOT/'tools/optimize_architecture.py').read_text()
  self.assertIn('--image-format',source)
  self.assertIn('export_image_format=',source)
if __name__=='__main__':unittest.main()

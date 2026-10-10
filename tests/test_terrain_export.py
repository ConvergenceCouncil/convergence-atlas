import importlib.util,math,pathlib,tempfile,unittest
class TerrainExportTests(unittest.TestCase):
 def test_native_mercator_pixel_grid(self):
  try:import numpy as np,rasterio,requests
  except ImportError:self.skipTest('Terrain dependencies required')
  script=pathlib.Path(__file__).resolve().parents[1]/'scripts/export_terrarium_dem.py';spec=importlib.util.spec_from_file_location('export',script);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  with tempfile.TemporaryDirectory() as temp:
   path=pathlib.Path(temp)/'tile.tif';module.write_mosaic(path,np.zeros((256,256),dtype=np.float32),0,0,0)
   with rasterio.open(path) as ds:
    self.assertEqual(ds.crs.to_epsg(),3857);self.assertAlmostEqual(ds.bounds.left,-math.pi*6378137);self.assertAlmostEqual(ds.transform.a,-ds.transform.e)

import unittest,sys,pathlib
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from seattle_ground import convert
class ExportTests(unittest.TestCase):
    def test_clipping_estimates_and_deduplication(self):
        tree={'type':'node','id':1,'lat':47.62,'lon':-122.35,'tags':{'natural':'tree'}}
        road={'type':'way','id':2,'tags':{'highway':'footway'},'geometry':[{'lat':47.62,'lon':-122.35},{'lat':47.621,'lon':-122.35},{'lat':47.63,'lon':-122.35},{'lat':47.622,'lon':-122.35}]}
        data=convert({'elements':[tree,tree,road]})
        self.assertEqual(data['metadata']['counts'],{'road':1,'tree':1})
        self.assertEqual(len(data['features'][1]['geometry']['coordinates'][0]),2)
        self.assertEqual(len(data['features'][1]['geometry']['coordinates']),1)
        self.assertTrue(data['features'][0]['properties']['height_estimated'])
    def test_empty_or_error_export_rejected(self):
        for data in ({'elements':[]},{'remark':'timeout'}):
            with self.assertRaises(ValueError): convert(data)
if __name__=='__main__':unittest.main()

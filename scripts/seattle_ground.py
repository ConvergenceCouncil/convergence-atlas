"""Small, reproducible OSM export; never publish an empty/error response."""
import json, math, pathlib, urllib.request, urllib.parse, datetime
BBOX = [-122.357, 47.615, -122.341, 47.626]
QUERY = '[out:json][timeout:60];(way[highway](47.615,-122.357,47.626,-122.341);node[natural=tree](47.615,-122.357,47.626,-122.341););out geom;'
ROAD_WIDTH = {'primary':12,'secondary':10,'tertiary':8,'residential':7,'unclassified':7,'service':4,'pedestrian':4,'footway':2,'path':2,'cycleway':2.5,'steps':2,'living_street':5}
def number(value):
    try:
        n = float(value)
        return n if math.isfinite(n) else None
    except (TypeError, ValueError): return None
def inside(lon, lat):
    return lon is not None and lat is not None and BBOX[0] <= lon <= BBOX[2] and BBOX[1] <= lat <= BBOX[3]
def convert(data):
    if data.get('remark'): raise ValueError(data['remark'])
    features = []; seen = set()
    for e in data.get('elements', []):
        tags = e.get('tags', {}); identity = str(e.get('type'))+'/'+str(e.get('id'))
        if identity in seen: continue
        seen.add(identity)
        p = {'osm_id':identity, 'name':tags.get('name',''), 'source':'OpenStreetMap'}
        if e.get('type') == 'node' and tags.get('natural') == 'tree':
            lon,lat=number(e.get('lon')),number(e.get('lat'))
            if not inside(lon,lat): continue
            measured=number(tags.get('height'))
            p.update(kind='tree', height_m=max(2,min(35,measured or 8)), height_estimated=not bool(measured and 2<=measured<=35), species=tags.get('species','unknown'), geometry_status='generic visual proxy at mapped location')
            geom={'type':'Point','coordinates':[lon,lat]}
        elif e.get('type') == 'way' and tags.get('highway') in ROAD_WIDTH:
            if tags.get('bridge') in ('yes','viaduct') or tags.get('tunnel')=='yes' or number(tags.get('layer')) not in (None,0): continue
            points=[[number(x.get('lon')),number(x.get('lat'))] for x in e.get('geometry',[])]
            # Only contiguous in-bounds segments: never bridge clipped gaps.
            segments=[]; segment=[]
            for point in points+[ [None,None] ]:
                if inside(*point): segment.append(point)
                else:
                    if len(segment)>1: segments.append(segment)
                    segment=[]
            if not segments: continue
            width=number(tags.get('width')); highway=tags['highway']
            p.update(kind='road',highway=highway,width_m=max(1,min(24,width or ROAD_WIDTH[highway])),width_estimated=not bool(width and 1<=width<=24),surface=tags.get('surface','unknown'))
            geom={'type':'MultiLineString','coordinates':segments}
        else: continue
        features.append({'type':'Feature','id':identity,'properties':p,'geometry':geom})
    counts={kind:sum(f['properties']['kind']==kind for f in features) for kind in ('road','tree')}
    if not all(counts.values()): raise ValueError('Pilot needs both mapped roads and trees: '+str(counts))
    if len(features)>10000: raise ValueError('Unexpectedly large export: '+str(counts))
    return {'type':'FeatureCollection','bbox':BBOX,'metadata':{'source':'© OpenStreetMap contributors','license':'ODbL-1.0','source_url':'https://www.openstreetmap.org/copyright','query':QUERY,'exported_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'counts':counts,'limitations':'Incomplete mapped coverage. Unmapped trees are not invented. Road widths and tree heights are estimated where absent; no drivable geometry or collision.'},'features':features}
def main():
    errors=[]
    for endpoint in ('https://overpass-api.de/api/interpreter','https://overpass.kumi.systems/api/interpreter','https://overpass.private.coffee/api/interpreter'):
        try:
            request=urllib.request.Request(endpoint,data=urllib.parse.urlencode({'data':QUERY}).encode(),headers={'User-Agent':'ConvergenceAtlas/1.0 (Seattle ground pilot)'})
            with urllib.request.urlopen(request,timeout=100) as response: raw=json.load(response)
            result=convert(raw); result['metadata']['endpoint']=endpoint
            path=pathlib.Path('data/seattle-ground-pilot.geojson');path.parent.mkdir(exist_ok=True)
            path.write_text(json.dumps(result,separators=(',',':'))+'\n')
            print(result['metadata']);return
        except Exception as error: errors.append(str(error));print(endpoint,str(error))
    raise RuntimeError('No validated export; existing cache preserved: '+str(errors))
if __name__=='__main__': main()

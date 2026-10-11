const assert=require('node:assert/strict');
const {detailBudget,selectFeatures,distanceMeters}=require('../ground-detail.js');
assert.deepEqual(detailBudget(10000,true),{roads:0,trees:0});
assert.equal(detailBudget(2000,true).trees,0);
const features=Array.from({length:300},(_,i)=>({id:'node/'+i,properties:{kind:'tree'},geometry:{coordinates:[-122.349+i*.00001,47.6205]}}));
assert.equal(selectFeatures(features,[-122.349,47.6205],90,true).length,120);
assert.equal(selectFeatures(features,[0,0],90,true).length,0);
assert.equal(selectFeatures(features,[-122.349,47.6205],90,true)[0].id,'node/0');
assert.ok(distanceMeters([0,0],[0,1])>111000);
console.log('Ground budgets, proximity selection and culling passed');

const {surfaceColor,treeAppearance}=require('../ground-detail.js');
assert.equal(surfaceColor({highway:'cycleway',surface:'asphalt'}),'#45494c');
assert.notEqual(surfaceColor({surface:'concrete'}),surfaceColor({surface:'dirt'}));
assert.deepEqual(treeAppearance('node/123'),treeAppearance('node/123'));
assert.notEqual(treeAppearance('node/123').uri,treeAppearance('node/124').uri);
const road=(id,highway,coordinates)=>({id,properties:{kind:'road',highway},geometry:{type:'MultiLineString',coordinates:[coordinates]}});
const tinyPaths=Array.from({length:110},(_,i)=>road('way/'+i,'footway',[[-122.349+i*.000001,47.62051],[-122.349+i*.000001,47.62052]]));
const crossingStreet=road('way/main','primary',[[-122.359,47.6205],[-122.339,47.6205]]);
const roadSelection=selectFeatures([...tinyPaths,crossingStreet],[-122.349,47.6205],90,true);
assert.equal(roadSelection.length,100);
assert.ok(roadSelection.some(f=>f.id==='way/main'),'A main street crossing the view must survive dense footpaths');

const {featureDistance}=require('../ground-detail.js');
assert.ok(featureDistance(crossingStreet,[-122.349,47.6205])<.01);
const stable=selectFeatures(features,[-122.349,47.6205],90,true,new Set(['node/125']));
assert.ok(stable.some(f=>f.id==='node/125'));
assert.equal(stable.length,120);

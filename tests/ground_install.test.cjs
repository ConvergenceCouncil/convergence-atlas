const assert=require('node:assert/strict');
const {install}=require('../ground-detail.js');
global.document={createElement:()=>({style:{}}),getElementById:()=>({appendChild(){}})};
let focus=[-122.349,47.6205],altitude=90,moveEnd,changed,removed=0,fetches=0,layer;
let resolve;
global.fetch=()=>{fetches++;return new Promise(r=>resolve=r);};
class Source{constructor(){this.show=true;this.items=[];this.entities={add:e=>(this.items.push(e),e),remove:e=>this.items.splice(this.items.indexOf(e),1)};}}
const Cesium={Credit:class{},Cartesian2:class{},CustomDataSource:Source,Cartographic:{fromCartesian:p=>p},Math:{toDegrees:x=>x},Cartesian3:{fromDegrees:(...x)=>x,fromDegreesArray:x=>x},Transforms:{headingPitchRollQuaternion:()=>({})},HeadingPitchRoll:class{},Color:{fromCssColorString:()=>({withAlpha:()=>({})})},HeightReference:{CLAMP_TO_GROUND:1},ClassificationType:{TERRAIN:1},CornerType:{ROUNDED:1},ShadowMode:{DISABLED:0},DistanceDisplayCondition:class{}};
const viewer={cesiumWidget:{creditDisplay:{addStaticCredit(){}}},camera:{get positionCartographic(){return {height:altitude};},getPickRay:()=>({}),moveEnd:{addEventListener:f=>{moveEnd=f;return ()=>removed++;}},changed:{addEventListener:f=>{changed=f;return ()=>removed++;}}},scene:{canvas:{clientWidth:390,clientHeight:844},globe:{getHeight:()=>0,pick:()=>({longitude:focus[0],latitude:focus[1]})},requestRender(){}},dataSources:{add:async l=>{layer=l;},remove:l=>{assert.equal(l,layer);removed++;}}};
const feature={id:'node/1',properties:{kind:'tree',height_m:8},geometry:{coordinates:focus}};
(async()=>{
 const api=install(viewer,Cesium,true);assert.equal(fetches,1);
 // Leaving the area before download completes must never reveal stale geometry.
 focus=[0,0];resolve({ok:true,json:async()=>({metadata:{counts:{tree:1}},features:[feature]})});
 await new Promise(r=>setImmediate(r));assert.equal(layer,undefined);
 focus=[-122.349,47.6205];await api.refresh();assert.equal(layer.items.length,1);
 await api.refresh();assert.equal(layer.items.length,1);
 altitude=2000;await api.refresh();assert.equal(layer.items.length,0);
 altitude=10000;await api.refresh();assert.equal(layer.show,false);
 assert.equal(fetches,1);
 altitude=90;changed();await new Promise(r=>setImmediate(r));assert.equal(layer.show,true);
 api.destroy();assert.equal(removed,3);await api.refresh();assert.equal(fetches,1);
 console.log('Install: stale loads, caching, reuse, altitude culling passed');
})().catch(e=>{console.error(e);process.exitCode=1;});

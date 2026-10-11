const assert=require('node:assert/strict');
const {install}=require('../ground-detail.js');
global.document={createElement:()=>({style:{}}),getElementById:()=>({appendChild(){}})};
let focus=[-122.349,47.6205],altitude=90,moveEnd,changed,removed=0,fetches=0,layer;
let resolve;
global.fetch=()=>{fetches++;return new Promise(r=>resolve=r);};
let notifications=0,depth=0,pending=false,failAdd=false;
function changedCollection(){if(depth)pending=true;else notifications++;}
class Source{constructor(){this.show=true;this.items=[];this.entities={suspendEvents:()=>depth++,resumeEvents:()=>{assert.ok(depth>0);if(--depth===0&&pending){pending=false;notifications++;}},add:e=>{if(failAdd)throw Error('Synthetic add failure');this.items.push(e);changedCollection();return e;},remove:e=>{this.items.splice(this.items.indexOf(e),1);changedCollection();}};}}
const Cesium={Credit:class{},Cartesian2:class{},CustomDataSource:Source,Cartographic:{fromCartesian:p=>p},Math:{toDegrees:x=>x},Cartesian3:{fromDegrees:(...x)=>x,fromDegreesArray:x=>x},Transforms:{headingPitchRollQuaternion:()=>({})},HeadingPitchRoll:class{},Color:{fromCssColorString:()=>({withAlpha:()=>({})})},HeightReference:{CLAMP_TO_GROUND:1},ClassificationType:{TERRAIN:1},CornerType:{ROUNDED:1},ShadowMode:{DISABLED:0},DistanceDisplayCondition:class{}};
const viewer={cesiumWidget:{creditDisplay:{addStaticCredit(){}}},camera:{get positionCartographic(){return {height:altitude};},getPickRay:()=>({}),moveEnd:{addEventListener:f=>{moveEnd=f;return ()=>removed++;}},changed:{addEventListener:f=>{changed=f;return ()=>removed++;}}},scene:{canvas:{clientWidth:390,clientHeight:844},globe:{getHeight:()=>0,pick:()=>({longitude:focus[0],latitude:focus[1]})},requestRender(){}},dataSources:{add:async l=>{layer=l;},remove:l=>{assert.equal(l,layer);removed++;}}};
 const feature={id:'node/1',properties:{kind:'tree',height_m:8},geometry:{coordinates:focus}};
(async()=>{
 const api=install(viewer,Cesium,true);assert.equal(fetches,1);
 // Leaving the area before download completes must never reveal stale geometry.
 const features=Array.from({length:120},(_,i)=>({...feature,id:'node/'+i}));
 focus=[0,0];resolve({ok:true,json:async()=>({metadata:{counts:{tree:120}},features})});
 await new Promise(r=>setImmediate(r));assert.equal(layer,undefined);
 focus=[-122.349,47.6205];await api.refresh();assert.equal(layer.items.length,120);
 assert.equal(notifications,1,'120 additions should notify Cesium once');assert.equal(depth,0);
 await api.refresh();assert.equal(layer.items.length,120);assert.equal(notifications,1,'Reused entities need no collection notification');
 altitude=2000;await api.refresh();assert.equal(layer.items.length,0);assert.equal(notifications,2,'120 removals should notify Cesium once');
 altitude=90;failAdd=true;await assert.rejects(api.refresh(),/Synthetic add failure/);assert.equal(depth,0,'Errors must release the event suspension');failAdd=false;
 altitude=10000;await api.refresh();assert.equal(layer.show,false);
 assert.equal(fetches,1);
 altitude=90;changed();await new Promise(r=>setImmediate(r));assert.equal(layer.show,true);
 api.destroy();assert.equal(removed,3);await api.refresh();assert.equal(fetches,1);
 console.log('Install: stale loads, caching, reuse, altitude culling passed');
})().catch(e=>{console.error(e);process.exitCode=1;});

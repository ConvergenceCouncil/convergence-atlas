const fs=require('fs'),vm=require('vm'),assert=require('assert'),path=require('path');
const html=fs.readFileSync(path.join(__dirname,'../globe.html'),'utf8');
const helpers=html.slice(html.indexOf('function globeDetailPolicy'),html.indexOf('function applyQuality'));
const ctx={};vm.createContext(ctx);vm.runInContext(helpers,ctx);
for(const height of [90,800,4500]){const o=ctx.inspectionOffset(height);assert.ok(Math.abs(o.range*Math.sin(Math.abs(o.pitchDegrees)*Math.PI/180)-height)<.0001);}
const near=ctx.globeDetailPolicy(800,false,true,390,844,3),far=ctx.globeDetailPolicy(500000,false,true,390,844,3);
assert(near.resolution>far.resolution);assert(near.buildings<far.buildings);
for(const [w,h] of [[390,844],[844,390],[2000,1500]]){const p=ctx.globeDetailPolicy(90,true,true,w,h,3);assert(w*h*p.resolution**2<=2400001);}
console.log('PASS: inspection height offsets, zoom detail and resized phone pixel budget');

assert.equal(ctx.cameraClearance(3000,2900),100);
assert.equal(ctx.cameraClearance(100,undefined),100);
assert.equal(ctx.cameraClearance(20,30),0);
for(const high of [false,true]){
 const street=ctx.terrainCacheBudget('street',high,false),nearby=ctx.terrainCacheBudget('near',high,false);
 assert.equal(street,nearby,'Desktop cache must retain the same capacity across street/near transitions');
 assert.ok(street>ctx.terrainCacheBudget('street',high,true));
 assert.ok(street<=512);
}
assert.equal(ctx.terrainCacheBudget('street',true,true),220);
assert.equal(ctx.terrainCacheBudget('near',true,true),140);
assert.equal(ctx.terrainCacheBudget('far',true,true),65);
assert.ok(html.includes('viewer.scene.globe.tileCacheSize=terrainCacheBudget(next,high,mobile)'));
const callbacks={},globe={getHeight:()=>0};
const integration={quality:'high',mobile:false,innerWidth:1920,innerHeight:1080,window:{devicePixelRatio:1},globalBuildings:{},document:{getElementById:()=>({})},viewer:{scene:{globe},camera:{positionCartographic:{height:90},changed:{addEventListener:f=>callbacks.changed=f},moveEnd:{addEventListener:f=>callbacks.end=f}}}};
vm.createContext(integration);vm.runInContext(helpers, integration);
vm.runInContext(html.slice(html.indexOf("let currentLod='';"),html.indexOf("document.getElementById('quality').onclick")),integration);
assert.equal(typeof callbacks.end,'function','Settled camera must apply final detail');
callbacks.end();assert.equal(globe.tileCacheSize,512);assert.equal(integration.globalBuildings.maximumScreenSpaceError,3.75);
integration.viewer.camera.positionCartographic.height=4500;callbacks.end();assert.equal(globe.tileCacheSize,512);

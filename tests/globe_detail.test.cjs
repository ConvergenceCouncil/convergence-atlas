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

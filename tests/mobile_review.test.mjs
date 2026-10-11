import {test} from 'node:test';
import assert from 'node:assert/strict';
import {FrameGate,mobileProfile} from '../js/mobile-review.mjs';
test('30 FPS pacing stays near target over 60 Hz callbacks',()=>{const g=new FrameGate(30);let renders=0;for(let n=0;n<600;n++)if(g.allow(n*1000/60,false,true))renders++;assert.ok(renders>=299&&renders<=301,`rendered ${renders} times in ten seconds`)});
test('hidden and idle frames pause, resume immediately',()=>{const g=new FrameGate(30);assert.equal(g.allow(0,false,true),true);assert.equal(g.allow(10,false,true),false);assert.equal(g.allow(15,true,true),false);assert.equal(g.allow(16,false,true),true);assert.equal(g.allow(17,false,false),false);assert.equal(g.allow(18,false,true),true)});
test('phone pixel budget survives landscape resize',()=>{for(const [w,h] of [[390,844],[844,390],[1400,1000]]){const p=mobileProfile(true,3,w,h);assert.ok(w*h*p.pixelRatio**2<=900001);assert.equal(p.antialias,false)}});

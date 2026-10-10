import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mobileProfile,FrameGate} from '../js/mobile-review.mjs';
test('touch renderer bounds pixels even on a high density display',()=>{const p=mobileProfile(true,3,1000,1000);assert.equal(p.fps,30);assert.ok(p.pixelRatio*p.pixelRatio*1000000<=900000);assert.equal(p.antialias,false)});
test('hidden frames and idle scenes do not render; active frames respect 30 FPS',()=>{const g=new FrameGate(30);assert.equal(g.allow(0,true,true),false);assert.equal(g.allow(0,false,false),false);assert.equal(g.allow(0,false,true),true);assert.equal(g.allow(16,false,true),false);assert.equal(g.allow(34,false,true),true);});

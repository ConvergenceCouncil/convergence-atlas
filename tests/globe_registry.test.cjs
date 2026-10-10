const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const html=fs.readFileSync('globe.html','utf8');
const code=html.slice(html.indexOf('const sources='),html.indexOf('// Terrain-aware inspection'));
class Element{constructor(){this.children=[];this.value='';}appendChild(e){this.children.push(e);}replaceChildren(...e){this.children=e;}addEventListener(_,fn){this.oninput=fn;}}
const select=new Element(),search=new Element();
const fixtures=new Map([
 ['data/approved-guild-registry.json',{sites:[{id:'G1',location:'Seattle',map_reference:{latitude:47,longitude:-122}}]}],
 ['data/ancient-relic-cities.geojson',{features:[{geometry:{coordinates:[29,31]},properties:{id:'A1',name:'Alexandria'}},{geometry:{coordinates:[25.16,35.30]},properties:{id:'ARC-03',name:'Knossos'}}]}],
 ['data/tourist-attractions.geojson',{features:[{geometry:{coordinates:[2,48]},properties:{id:'T1',name:'Louvre'}}]}],
 ['data/tourist-attractions-expansion.geojson',{features:[{geometry:{coordinates:[2,48]},properties:{id:'T2',name:'Louvre'}},{geometry:{coordinates:[200,95]},properties:{name:'Invalid'}}]}]
]);
const entities=[];
const context={Promise,console:{warn(){}},getJSON:async path=>{if(!fixtures.has(path))throw Error('Offline');return fixtures.get(path);},destinations:[],destinationSelect:select,document:{getElementById:()=>search,createElement:()=>new Element()},Option:class{constructor(text,value){this.text=text;this.value=value;}},viewer:{entities:{add:e=>{entities.push(e);return e;}},selectedEntityChanged:{addEventListener(fn){this.fn=fn;}}},Cesium:{Cartesian3:{fromDegrees:(...args)=>args},Color:{CYAN:1,ORANGE:2,GOLD:3,BLACK:4},HeightReference:{CLAMP_TO_GROUND:1},DistanceDisplayCondition:class{}},status:{},currentTarget:null};
(async()=>{await vm.runInNewContext('(async()=>{'+code+'})()',context);assert.equal(context.destinations.length,4);assert.equal(entities.length,4);assert.match(context.status.textContent,/Some location sources/);assert.match(entities.find(e=>e.name==='Knossos').description,/knossos-room-review\.html/);search.value='louvre';search.oninput();assert.equal(select.children.length,2);assert.equal(select.children[1].children[0].text,'Louvre');context.viewer.selectedEntityChanged.fn(entities[0]);assert.equal(context.currentTarget.name,'G1 · Seattle');console.log('PASS: partial outage, invalid coordinates, deduplication, search and marker selection');})().catch(e=>{console.error(e);process.exitCode=1;});

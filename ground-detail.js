/* Mapped Seattle pilot; generic tree proxies, no invented locations. */
(function(root){'use strict';
function distanceMeters(a,b){const r=Math.PI/180,h=Math.sin((a[1]-b[1])*r/2)**2+Math.cos(a[1]*r)*Math.cos(b[1]*r)*Math.sin((a[0]-b[0])*r/2)**2;return 12742000*Math.asin(Math.sqrt(Math.min(1,h)));}
function detailBudget(altitude,mobile){return {roads:altitude<5000?(mobile?100:180):0,trees:altitude<1400?(mobile?120:240):0};}
function selectFeatures(features,focus,altitude,mobile){
 const budget=detailBudget(altitude,mobile),selected=[];
 for(const kind of ['road','tree']){
  if(!budget[kind+'s'])continue;
  const ranked=features.filter(f=>f.properties.kind===kind).map(f=>{
   const coords=kind==='tree'?[f.geometry.coordinates]:f.geometry.coordinates.flat();
   return {f,distance:Math.min(...coords.map(p=>distanceMeters(p,focus)))};
  }).filter(x=>x.distance<(kind==='tree'?1600:3500)).sort((a,b)=>a.distance-b.distance||String(a.f.id).localeCompare(String(b.f.id)));
  selected.push(...ranked.slice(0,budget[kind+'s']).map(x=>x.f));
 }return selected;
}
function install(viewer,Cesium,mobile){
 let data=null,loading=null,layer=null,lastFocus=null,lastAltitude=0,retryAfter=0;
 const rows=new Map();
 const info=document.createElement('div');info.id='ground-detail-status';info.style.cssText='font-size:11px;line-height:1.5;color:#c6d2bf';document.getElementById('panel-content').appendChild(info);
 viewer.cesiumWidget.creditDisplay.addStaticCredit(new Cesium.Credit('Roads and tree locations © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a> · ODbL',true));
 function focusPoint(){
  const canvas=viewer.scene.canvas,ray=viewer.camera.getPickRay(new Cesium.Cartesian2(canvas.clientWidth/2,canvas.clientHeight/2));
  const p=ray&&viewer.scene.globe.pick(ray,viewer.scene),c=p?Cesium.Cartographic.fromCartesian(p):viewer.camera.positionCartographic;
  return [Cesium.Math.toDegrees(c.longitude),Cesium.Math.toDegrees(c.latitude)];
 }
 async function update(force=false){
  const c=viewer.camera.positionCartographic,ground=viewer.scene.globe.getHeight(c)||0,altitude=Math.max(0,c.height-ground),focus=focusPoint();
  if(altitude>=5000||distanceMeters(focus,[-122.349,47.6205])>4000){if(layer)layer.show=false;lastFocus=null;info.textContent='Roads & foliage: Seattle Center pilot · zoom closer to load';return;}
  if(!data){
   if(loading||Date.now()<retryAfter)return;
   info.textContent='Loading mapped Seattle ground detail…';
   loading=fetch('data/seattle-ground-pilot.geojson',{signal:AbortSignal.timeout(12000)}).then(r=>{if(!r.ok)throw Error('HTTP '+r.status);return r.json();});
   try{data=await loading;if(!Array.isArray(data.features)||!data.metadata?.counts)throw Error('Invalid ground data');}
   catch(e){data=null;retryAfter=Date.now()+30000;info.textContent='Seattle ground detail unavailable; terrain and buildings remain usable.';console.warn('Ground pilot',e);return;}
   finally{loading=null;}return update(true);
  }
  if(!force&&lastFocus&&distanceMeters(focus,lastFocus)<100&&detailBudget(altitude,mobile).trees===detailBudget(lastAltitude,mobile).trees)return;
  lastFocus=focus;lastAltitude=altitude;
  if(!layer){layer=new Cesium.CustomDataSource('Seattle mapped ground pilot');await viewer.dataSources.add(layer);return update(true);}
  const selected=selectFeatures(data.features,focus,altitude,mobile),wanted=new Set(selected.map(f=>String(f.id)));
  for(const [id,entities] of rows){if(!wanted.has(id)){entities.forEach(e=>layer.entities.remove(e));rows.delete(id);}}
  for(const f of selected){
   const id=String(f.id),p=f.properties;if(rows.has(id))continue;const entities=[];
   if(p.kind==='road'){
    const pedestrian=['footway','path','pedestrian','cycleway','steps'].includes(p.highway),color=Cesium.Color.fromCssColorString(pedestrian?'#b7aa8c':'#42464a').withAlpha(.87);
    f.geometry.coordinates.forEach((coords,index)=>entities.push(layer.entities.add({id:'ground-'+id+'-'+index,name:p.name||p.highway+' · mapped road',properties:p,corridor:{positions:Cesium.Cartesian3.fromDegreesArray(coords.flat()),width:p.width_m,cornerType:Cesium.CornerType.ROUNDED,material:color,heightReference:Cesium.HeightReference.CLAMP_TO_GROUND,classificationType:Cesium.ClassificationType.TERRAIN,zIndex:2,outline:false,distanceDisplayCondition:new Cesium.DistanceDisplayCondition(0,6000)}})));
   }else{
    const coords=f.geometry.coordinates,hash=Number(id.split('/')[1])||0,position=Cesium.Cartesian3.fromDegrees(coords[0],coords[1]);
    entities.push(layer.entities.add({id:'ground-'+id,name:p.name||'Mapped tree · generic foliage proxy',position,properties:p,orientation:Cesium.Transforms.headingPitchRollQuaternion(position,new Cesium.HeadingPitchRoll((hash%360)*Math.PI/180,0,0)),model:{uri:'assets/pilot-broadleaf.glb',scale:p.height_m/8,minimumPixelSize:0,heightReference:Cesium.HeightReference.CLAMP_TO_GROUND,shadows:Cesium.ShadowMode.DISABLED,distanceDisplayCondition:new Cesium.DistanceDisplayCondition(0,1700)}}));
   }rows.set(id,entities);
  }
  layer.show=true;const trees=selected.filter(f=>f.properties.kind==='tree').length;
  info.textContent=selected.length-trees+' mapped road ways · '+trees+' nearby tree proxies · widths/heights estimated where absent';viewer.scene.requestRender();
 }
 viewer.camera.moveEnd.addEventListener(()=>update().catch(e=>console.warn('Ground detail update',e)));
 update().catch(e=>console.warn(e));return {refresh:()=>update(true)};
}
const api={distanceMeters,detailBudget,selectFeatures,install};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.ConvergenceGroundDetail=api;
})(typeof window!=='undefined'?window:globalThis);

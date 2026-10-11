/* Mapped Seattle pilot; generic tree proxies, no invented locations. */
(function(root){'use strict';
function distanceMeters(a,b){const r=Math.PI/180,h=Math.sin((a[1]-b[1])*r/2)**2+Math.cos(a[1]*r)*Math.cos(b[1]*r)*Math.sin((a[0]-b[0])*r/2)**2;return 12742000*Math.asin(Math.sqrt(Math.min(1,h)));}
function detailBudget(altitude,mobile){
 const fade=(start,end)=>Math.max(0,Math.min(1,(end-altitude)/(end-start)));
 return {roads:Math.round((mobile?100:180)*fade(1500,5000)),trees:Math.round((mobile?120:240)*fade(600,1400))};
}
function surfaceColor(properties){
 const surface=String(properties.surface||'').toLowerCase();
 if(['asphalt','paved'].includes(surface))return '#45494c';
 if(['concrete','concrete:plates','paving_stones'].includes(surface))return '#aaa79e';
 if(['gravel','fine_gravel','compacted','pebblestone'].includes(surface))return '#9b9079';
 if(['dirt','earth','ground','sand','unpaved'].includes(surface))return '#8c785b';
 return ['footway','path','pedestrian','steps'].includes(properties.highway)?'#b7aa8c':'#42464a';
}
function treeAppearance(id){
 const hash=Number(String(id).split('/')[1])||0;
 return {uri:hash%3===0?'assets/pilot-upright-v2.glb':'assets/pilot-broadleaf-v2.glb',heading:(hash%360)*Math.PI/180};
}
function featureDistance(feature,focus){
 if(feature.properties.kind==='tree')return distanceMeters(feature.geometry.coordinates,focus);
 // Local metric projection is appropriate for this bounded Seattle pilot.
 const xScale=111195*Math.cos(focus[1]*Math.PI/180),yScale=111195;
 let nearest=Infinity;
 for(const line of feature.geometry.coordinates){
  for(let i=1;i<line.length;i++){
   const a=line[i-1],b=line[i],ax=(a[0]-focus[0])*xScale,ay=(a[1]-focus[1])*yScale,dx=(b[0]-a[0])*xScale,dy=(b[1]-a[1])*yScale;
   const length=dx*dx+dy*dy,t=length?Math.max(0,Math.min(1,-(ax*dx+ay*dy)/length)):0;
   nearest=Math.min(nearest,Math.hypot(ax+t*dx,ay+t*dy));
  }
 }return nearest;
}
function selectFeatures(features,focus,altitude,mobile,retained=new Set()){
 const budget=detailBudget(altitude,mobile),selected=[];
 for(const kind of ['road','tree']){
  if(!budget[kind+'s'])continue;
  const ranked=features.filter(f=>f.properties.kind===kind).map(f=>{
   const distance=featureDistance(f,focus);
   return {f,distance,score:distance-(retained.has(String(f.id))?(kind==='tree'?20:40):0)};
  }).filter(x=>x.distance<(kind==='tree'?1600:3500)).sort((a,b)=>a.score-b.score||String(a.f.id).localeCompare(String(b.f.id)));
  const cap=budget[kind+'s'];
  const main=kind==='road'?ranked.filter(x=>['primary','secondary','tertiary','residential','unclassified','living_street'].includes(x.f.properties.highway)).slice(0,Math.ceil(cap*.25)):[];
  const ids=new Set(main.map(x=>String(x.f.id)));
  const result=[...main,...ranked.filter(x=>!ids.has(String(x.f.id))).slice(0,cap-main.length)];
  selected.push(...result.map(x=>x.f));
 }return selected;
}
function install(viewer,Cesium,mobile){
 let data=null,loading=null,layer=null,lastFocus=null,lastAltitude=0,retryAfter=0,lastMovementUpdate=0,disposed=false;
 const rows=new Map();
 const info=document.createElement('div');info.id='ground-detail-status';info.style.cssText='font-size:11px;line-height:1.5;color:#c6d2bf';document.getElementById('panel-content').appendChild(info);
 viewer.cesiumWidget.creditDisplay.addStaticCredit(new Cesium.Credit('Roads and tree locations © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a> · ODbL',true));
 function focusPoint(){
  const canvas=viewer.scene.canvas,ray=viewer.camera.getPickRay(new Cesium.Cartesian2(canvas.clientWidth/2,canvas.clientHeight/2));
  const p=ray&&viewer.scene.globe.pick(ray,viewer.scene),c=p?Cesium.Cartographic.fromCartesian(p):viewer.camera.positionCartographic;
  return [Cesium.Math.toDegrees(c.longitude),Cesium.Math.toDegrees(c.latitude)];
 }
 async function update(force=false){
  if(disposed)return;
  const c=viewer.camera.positionCartographic,ground=viewer.scene.globe.getHeight(c)||0,altitude=Math.max(0,c.height-ground),focus=focusPoint();
  if(altitude>=5000||distanceMeters(focus,[-122.349,47.6205])>4000){if(layer&&layer.show){layer.show=false;viewer.scene.requestRender();}lastFocus=null;info.textContent='Roads & foliage: Seattle Center pilot · zoom closer to load';return;}
  if(!data){
   if(loading||Date.now()<retryAfter)return;
   info.textContent='Loading mapped Seattle ground detail…';
   loading=fetch('data/seattle-ground-pilot.geojson',{signal:AbortSignal.timeout(12000)}).then(r=>{if(!r.ok)throw Error('HTTP '+r.status);return r.json();});
   try{data=await loading;if(!Array.isArray(data.features)||!data.metadata?.counts)throw Error('Invalid ground data');}
   catch(e){data=null;retryAfter=Date.now()+30000;info.textContent='Seattle ground detail unavailable; terrain and buildings remain usable.';console.warn('Ground pilot',e);return;}
   finally{loading=null;}if(disposed)return;return update(true);
  }
  const budget=detailBudget(altitude,mobile),previousBudget=detailBudget(lastAltitude,mobile);
  if(!force&&lastFocus&&distanceMeters(focus,lastFocus)<30&&budget.trees===previousBudget.trees&&budget.roads===previousBudget.roads)return;
  lastFocus=focus;lastAltitude=altitude;
  if(!layer){layer=new Cesium.CustomDataSource('Seattle mapped ground pilot');await viewer.dataSources.add(layer);if(disposed){viewer.dataSources.remove(layer,true);return;}return update(true);}
  const selected=selectFeatures(data.features,focus,altitude,mobile,new Set(rows.keys())),wanted=new Set(selected.map(f=>String(f.id)));
  for(const [id,entities] of rows){if(!wanted.has(id)){entities.forEach(e=>layer.entities.remove(e));rows.delete(id);}}
  for(const f of selected){
   const id=String(f.id),p=f.properties;if(rows.has(id))continue;const entities=[];
   if(p.kind==='road'){
    const color=Cesium.Color.fromCssColorString(surfaceColor(p)).withAlpha(.87);
    f.geometry.coordinates.forEach((coords,index)=>entities.push(layer.entities.add({id:'ground-'+id+'-'+index,name:p.name||p.highway+' · mapped road',properties:p,corridor:{positions:Cesium.Cartesian3.fromDegreesArray(coords.flat()),width:p.width_m,cornerType:Cesium.CornerType.ROUNDED,material:color,heightReference:Cesium.HeightReference.CLAMP_TO_GROUND,classificationType:Cesium.ClassificationType.TERRAIN,zIndex:2,outline:false,distanceDisplayCondition:new Cesium.DistanceDisplayCondition(0,6000)}})));
   }else{
    const coords=f.geometry.coordinates,appearance=treeAppearance(id),position=Cesium.Cartesian3.fromDegrees(coords[0],coords[1]);
    entities.push(layer.entities.add({id:'ground-'+id,name:p.name||'Mapped tree · generic foliage proxy',position,properties:p,orientation:Cesium.Transforms.headingPitchRollQuaternion(position,new Cesium.HeadingPitchRoll(appearance.heading,0,0)),model:{uri:appearance.uri,scale:p.height_m/8,minimumPixelSize:0,heightReference:Cesium.HeightReference.CLAMP_TO_GROUND,shadows:Cesium.ShadowMode.DISABLED,distanceDisplayCondition:new Cesium.DistanceDisplayCondition(0,1700)}}));
   }rows.set(id,entities);
  }
  layer.show=true;const trees=selected.filter(f=>f.properties.kind==='tree').length;
  info.textContent=selected.length-trees+' mapped road ways · '+trees+' nearby tree proxies · widths/heights estimated where absent';viewer.scene.requestRender();
 }
 const refresh=()=>update().catch(e=>console.warn('Ground detail update',e));
 const onMovement=()=>{const now=Date.now();if(now-lastMovementUpdate<350)return;lastMovementUpdate=now;refresh();};
 const removeEnd=viewer.camera.moveEnd.addEventListener(refresh);
 const removeChanged=viewer.camera.changed?.addEventListener(onMovement);
 update().catch(e=>console.warn(e));return {refresh:()=>update(true),destroy:()=>{disposed=true;removeEnd?.();removeChanged?.();if(layer)viewer.dataSources.remove(layer,true);rows.clear();info.remove?.();}};
}
const api={distanceMeters,featureDistance,detailBudget,surfaceColor,treeAppearance,selectFeatures,install};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.ConvergenceGroundDetail=api;
})(typeof window!=='undefined'?window:globalThis);

/* Small presentation policies shared by the globe and regression checks. */
(function(root){'use strict';
function statusIsPersistent(message){return /loading|fetching|connecting|unavailable|unable|timed out|could not|failed|error|choose a destination/i.test(message);}
function showCountryOverlay(clearance){return Number.isFinite(clearance)&&clearance>=150000;}
function installStatus(source,banner){
 let timer=null;
 function sync(){
  clearTimeout(timer);banner.textContent=source.textContent;banner.classList.remove('quiet');
  if(!statusIsPersistent(source.textContent))timer=setTimeout(()=>banner.classList.add('quiet'),7000);
 }
 const observer=new MutationObserver(sync);observer.observe(source,{childList:true,characterData:true,subtree:true});sync();
 return ()=>{clearTimeout(timer);observer.disconnect();};
}
const api={statusIsPersistent,showCountryOverlay,installStatus};
if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.ConvergenceGlobeUI=api;
})(typeof window!=='undefined'?window:globalThis);

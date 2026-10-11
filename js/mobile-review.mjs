// Rendering policy, not a device performance certification.
export function mobileProfile(touch,dpr,width,height){
 return {fps:touch?30:60,antialias:true,pixelRatio:Math.min(dpr,2,Math.sqrt((2400000)/Math.max(1,width*height)))};
}
export class FrameGate{
 constructor(fps){this.interval=1000/fps;this.next=null;}
 allow(now,hidden,active){
  if(hidden||!active){this.next=null;return false;}
  if(this.next===null){this.next=now+this.interval;return true;}
  if(now+0.01<this.next)return false;
  this.next+=this.interval;
  if(this.next<=now)this.next=now+this.interval;
  return true;
 }
}

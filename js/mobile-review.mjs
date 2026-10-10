// Rendering policy, not a device performance certification.
export function mobileProfile(touch,dpr,width,height){
 return {fps:touch?30:60,antialias:!touch,pixelRatio:Math.min(dpr,touch?1:1.5,Math.sqrt((touch?900000:2400000)/Math.max(1,width*height)))};
}
export class FrameGate{
 constructor(fps){this.interval=1000/fps;this.last=-Infinity;}
 allow(now,hidden,active){if(hidden||!active||now-this.last<this.interval)return false;this.last=now;return true;}
}

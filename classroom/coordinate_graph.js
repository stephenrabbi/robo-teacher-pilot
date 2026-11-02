/* Accurate coordinate layouts and learner-controlled plotting; no network calls. */
(function(root){
  'use strict';
  function coordinateLayout(items){
    const points=[],seen=new Set();
    for(const item of (Array.isArray(items)?items:[]).slice(0,8)){
      const match=String(item.label||'').match(/^\s*\(?\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\)?\s*$/);
      if(!match)continue;
      const x=Number(match[1]),y=Number(match[2]);
      if(!Number.isFinite(x)||!Number.isFinite(y)||Math.abs(x)>1e12||Math.abs(y)>1e12)continue;
      const key=`${x},${y}`;if(seen.has(key))continue;seen.add(key);
      points.push({x,y,label:String.fromCharCode(65+points.length)});
    }
    if(!points.length)return null;
    const magnitude=Math.max(...points.flatMap(p=>[Math.abs(p.x),Math.abs(p.y)]));
    const target=magnitude?magnitude/4:1;
    const power=10**Math.floor(Math.log10(target));
    const fraction=target/power;
    const step=(fraction<=1?1:fraction<=2?2:fraction<=5?5:10)*power;
    const count=Math.ceil((magnitude||1)/step)+1,bound=count*step;
    const mapX=x=>180+x/bound*132,mapY=y=>180-y/bound*132;
    return {step,bound,mapX,mapY,points:points.map(p=>({...p,px:mapX(p.x),py:mapY(p.y)})),ticks:Array.from({length:count*2+1},(_,i)=>(i-count)*step)};
  }
  function renderCoordinateGraph(container,items,title='Coordinate plot'){
    const layout=coordinateLayout(items),doc=container.ownerDocument;
    container.replaceChildren();
    if(!layout){const note=doc.createElement('p');note.textContent='No readable coordinate pairs were provided. Return to the explanation and check the points.';container.appendChild(note);return;}
    const svg=doc.createElementNS('http://www.w3.org/2000/svg','svg');
    svg.setAttribute('viewBox','0 0 360 360');svg.setAttribute('role','img');svg.setAttribute('aria-label',title);svg.classList.add('coordinate-graph');
    const node=(kind,attributes,text,parent=svg)=>{const n=doc.createElementNS('http://www.w3.org/2000/svg',kind);for(const [k,v] of Object.entries(attributes))n.setAttribute(k,String(v));if(text!==undefined)n.textContent=text;parent.appendChild(n);return n;};
    const short=n=>Number(n.toPrecision(5)).toString();
    for(const value of layout.ticks){
      const x=layout.mapX(value),y=layout.mapY(value);
      node('line',{x1:x,y1:48,x2:x,y2:312,class:'graph-grid'});
      node('line',{x1:48,y1:y,x2:312,y2:y,class:'graph-grid'});
      if(value!==0){node('text',{x,y:328,'text-anchor':'middle',class:'graph-tick'},short(value));node('text',{x:40,y:y+3,'text-anchor':'end',class:'graph-tick'},short(value));}
    }
    node('line',{x1:48,y1:180,x2:320,y2:180,class:'graph-axis'});
    node('line',{x1:180,y1:312,x2:180,y2:40,class:'graph-axis'});
    node('text',{x:333,y:185,class:'graph-axis-label'},'x');node('text',{x:185,y:31,class:'graph-axis-label'},'y');node('text',{x:170,y:195,class:'graph-tick'},'0');
    const guides=node('g',{}),marks=layout.points.map(p=>{const group=node('g',{});node('circle',{cx:p.px,cy:p.py,r:5,class:'graph-point'},undefined,group);node('text',{x:p.px+8,y:p.py-8,class:'graph-point-label'},p.label,group);return group;});
    const controls=doc.createElement('div');controls.classList.add('graph-controls');
    const status=doc.createElement('p');status.setAttribute('role','status');status.setAttribute('aria-live','polite');
    const table=doc.createElement('table');table.classList.add('graph-point-table');
    const caption=doc.createElement('caption');caption.textContent='Points from this explanation';table.appendChild(caption);
    const header=doc.createElement('tr');for(const label of ['Point','x','y']){const th=doc.createElement('th');th.textContent=label;th.setAttribute('scope','col');header.appendChild(th);}table.appendChild(header);
    for(const p of layout.points){const row=doc.createElement('tr');for(const value of [p.label,p.x,p.y]){const cell=doc.createElement('td');cell.textContent=String(value);row.appendChild(cell);}table.appendChild(row);}
    let visible=layout.points.length;
    const button=(label,action)=>{const b=doc.createElement('button');b.type='button';b.textContent=label;b.addEventListener('click',action);controls.appendChild(b);return b;};
    const draw=()=>{
      marks.forEach((mark,i)=>mark.setAttribute('visibility',i<visible?'visible':'hidden'));guides.replaceChildren();
      if(visible===0)status.textContent='Start at the origin (0, 0). Plot the next point when you are ready.';
      else if(visible===layout.points.length)status.textContent='All points shown. Both axes use the same distance per unit. Points are not automatically joined.';
      else status.textContent=`${visible} of ${layout.points.length} points shown.`;
      next.disabled=visible>=layout.points.length;
    };
    button('Plot step by step',()=>{visible=0;draw();});
    const next=button('Plot next point',()=>{
      if(visible>=layout.points.length)return;
      const p=layout.points[visible++];draw();
      node('line',{x1:180,y1:180,x2:p.px,y2:180,class:'graph-guide'},undefined,guides);
      node('line',{x1:p.px,y1:180,x2:p.px,y2:p.py,class:'graph-guide'},undefined,guides);
      status.textContent=`Point ${p.label}: x = ${p.x}, y = ${p.y}. Move ${Math.abs(p.x)} ${p.x<0?'left':'right'} from the origin, then ${Math.abs(p.y)} ${p.y<0?'down':'up'}. ${visible} of ${layout.points.length} points shown.`;
    });
    button('Show all points',()=>{visible=layout.points.length;draw();});
    container.append(svg,controls,status,table);draw();
  }
  if(typeof module==='object'&&module.exports)module.exports={coordinateLayout,renderCoordinateGraph};
  else root.RoboTeacherGraphs={coordinateLayout,renderCoordinateGraph};
})(typeof window==='undefined'?globalThis:window);

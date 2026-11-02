/* Text-only shape identifiers produce bounded SVG schematics, never model HTML. */
(function(root){
 'use strict';
 const descriptions={rectangle:{title:'Rectangle',description:'Rectangle schematic with length l and width w. Not to scale.',formula:'Area = length × width = l × w'},circle:{title:'Circle',description:'Circle schematic with radius r from its centre to its edge. Not to scale.',formula:'Area = π × radius² = πr²'},triangle:{title:'Triangle',description:'Triangle schematic with base b and perpendicular height h. Not to scale.',formula:'Area = ½ × base × perpendicular height = ½bh'}};
 function renderGeometry(container,shape){
  const doc=container.ownerDocument,info=descriptions[shape];container.replaceChildren();
  if(!Object.hasOwn(descriptions,shape)){const note=doc.createElement('p');note.textContent='This shape is not available. Return to the explanation.';container.appendChild(note);return;}
  const svg=doc.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 360 340');svg.setAttribute('role','img');svg.setAttribute('aria-label',info.description);svg.classList.add('geometry-diagram');
  const node=(kind,attrs,text,parent=svg)=>{const n=doc.createElementNS('http://www.w3.org/2000/svg',kind);for(const [k,v] of Object.entries(attrs))n.setAttribute(k,String(v));if(text!==undefined)n.textContent=text;parent.appendChild(n);return n;};
  const labels=node('g',{'data-geometry-labels':'true'});
  const label=(x,y,text)=>node('text',{x,y,'text-anchor':'middle',class:'geometry-label'},text,labels);
  const line=(x1,y1,x2,y2,kind='geometry-measure')=>node('line',{x1,y1,x2,y2,class:kind},undefined,labels);
  if(shape==='rectangle'){
   node('rect',{x:60,y:75,width:240,height:155,rx:0,class:'geometry-shape'});
   label(180,260,'length l');label(180,285,'l and w are side lengths');
   line(60,245,300,245);line(315,75,315,230);label(332,160,'w');
  }else if(shape==='circle'){
   node('circle',{cx:180,cy:160,r:100,class:'geometry-shape'});
   line(180,160,280,160);node('circle',{cx:180,cy:160,r:4,class:'geometry-centre'},undefined,labels);
   label(230,149,'radius r');label(180,292,'Radius: centre to edge');
  }else{
   node('polygon',{points:'55,265 305,265 155,65',class:'geometry-shape'});
   line(155,65,155,265,'geometry-height');
   node('polyline',{points:'155,253 167,253 167,265',class:'geometry-right-angle'},undefined,labels);
   label(190,165,'height h');line(55,280,305,280);label(180,303,'base b');
  }
  // Keep measurement marks above the filled shape.
  svg.appendChild(labels);
  const controls=doc.createElement('div');controls.classList.add('graph-controls');
  const formula=doc.createElement('p');formula.setAttribute('role','status');formula.setAttribute('aria-live','polite');formula.textContent='Schematic. Not to scale. Use the measurements in your question.';
  const toggle=doc.createElement('button');toggle.type='button';toggle.textContent='Hide shape labels';toggle.setAttribute('aria-pressed','true');let shown=true;
  toggle.addEventListener('click',()=>{shown=!shown;labels.setAttribute('visibility',shown?'visible':'hidden');toggle.textContent=shown?'Hide shape labels':'Show shape labels';toggle.setAttribute('aria-pressed',String(shown));});
  const area=doc.createElement('button');area.type='button';area.textContent='Show area formula';area.addEventListener('click',()=>{formula.textContent=info.formula+'. The diagram is not to scale.';});
  controls.append(toggle,area);container.append(svg,controls,formula);
 }
 if(typeof module==='object'&&module.exports)module.exports={renderGeometry};else root.RoboTeacherGeometry={renderGeometry};
})(typeof window==='undefined'?globalThis:window);

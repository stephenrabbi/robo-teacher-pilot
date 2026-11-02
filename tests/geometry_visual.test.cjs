const test=require('node:test');
const assert=require('node:assert/strict');
const {renderGeometry}=require('../classroom/geometry_visual.js');
class Node{
 constructor(doc,kind){this.ownerDocument=doc;this.kind=kind;this.children=[];this.attributes={};this.listeners={};this.classList={add(){}};}
 appendChild(n){const index=this.children.indexOf(n);if(index>=0)this.children.splice(index,1);this.children.push(n);return n;}append(...nodes){nodes.forEach(n=>this.appendChild(n))}replaceChildren(...nodes){this.children=nodes}setAttribute(k,v){this.attributes[k]=v}addEventListener(k,f){this.listeners[k]=f}click(){this.listeners.click()}
}
function draw(shape){const doc={createElement:k=>new Node(doc,k),createElementNS:(ns,k)=>new Node(doc,k)},c=new Node(doc,'div');renderGeometry(c,shape);return c;}
for(const [shape,kind,formula] of [['rectangle','rect',/l × w/],['circle','circle',/πr²/],['triangle','polygon',/½bh/]]){
 test(shape+' renders an accessible bounded schematic and correct area relationship',()=>{
  const c=draw(shape),[svg,controls,status]=c.children;
  assert.equal(svg.attributes.role,'img');assert.match(svg.attributes['aria-label'],/Not to scale/);assert.equal(svg.attributes.viewBox,'0 0 360 340');assert.ok(svg.children.some(n=>n.kind===kind));
  controls.children[1].click();assert.match(status.textContent,formula);assert.match(status.textContent,/not to scale/);
 });
}
test('triangle height is perpendicular to its horizontal base and includes a right-angle mark',()=>{
 const svg=draw('triangle').children[0],labels=svg.children.find(n=>n.kind==='g');const height=labels.children.find(n=>n.attributes.class==='geometry-height');
 assert.equal(height.attributes.x1,height.attributes.x2);assert.equal(height.attributes.y2,'265');assert.ok(labels.children.some(n=>n.kind==='polyline'));
});
test('labels can be hidden and restored without changing the shape',()=>{
 const [svg,controls]=draw('circle').children,labels=svg.children.find(n=>n.kind==='g'),circle=svg.children.find(n=>n.kind==='circle');
 controls.children[0].click();assert.equal(labels.attributes.visibility,'hidden');controls.children[0].click();assert.equal(labels.attributes.visibility,'visible');assert.equal(circle.attributes.r,'100');
});
test('unrecognised shape identifiers render safe text instead of markup',()=>{
 for(const shape of ['<script>','__proto__',undefined]){const c=draw(shape);assert.equal(c.children[0].kind,'p');assert.match(c.children[0].textContent,/not available/);}
});

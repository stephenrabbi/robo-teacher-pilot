const test=require('node:test');
const assert=require('node:assert/strict');
const {coordinateLayout,renderCoordinateGraph}=require('../classroom/coordinate_graph.js');
const items=(...labels)=>labels.map(label=>({label,value:1}));
test('large coordinates remain distinct and within the plot',()=>{
 const g=coordinateLayout(items('20,200','40,400','-30,-300'));
 assert.notEqual(g.points[0].px,g.points[1].px);
 for(const p of g.points){assert.ok(p.px>48&&p.px<312);assert.ok(p.py>48&&p.py<312);}
});
test('negative values occupy the correct quadrants with equal unit distances',()=>{
 const g=coordinateLayout(items('(-2, -3)','(2, 3)'));
 assert.ok(g.points[0].px<180&&g.points[0].py>180);
 assert.ok(g.points[1].px>180&&g.points[1].py<180);
 assert.equal(g.mapX(1)-g.mapX(0),g.mapY(0)-g.mapY(1));
});
test('decimal coordinates remain finite and are not rounded into the same point',()=>{
 const g=coordinateLayout(items('0.001,0.002','0.002,0.003'));
 assert.notEqual(g.points[0].px,g.points[1].px);assert.ok(g.ticks.every(Number.isFinite));
});
test('invalid points are rejected and duplicates do not become extra steps',()=>{
 const g=coordinateLayout(items('0,0','0,0','<script>','NaN,4','10000000000000,1','2,3'));
 assert.equal(g.points.length,2);assert.equal(g.points[1].label,'B');assert.equal(coordinateLayout(items('bad')),null);
});
class Node{
 constructor(doc,kind){this.ownerDocument=doc;this.kind=kind;this.children=[];this.attributes={};this.listeners={};this.classList={add(){}};}
 appendChild(n){this.children.push(n);return n;}append(...nodes){nodes.forEach(n=>this.appendChild(n));}replaceChildren(...nodes){this.children=nodes;}setAttribute(k,v){this.attributes[k]=v;}addEventListener(k,fn){this.listeners[k]=fn;}click(){this.listeners.click();}
}
function container(){const doc={createElement(kind){return new Node(doc,kind)},createElementNS(ns,kind){return new Node(doc,kind)}};return new Node(doc,'div');}
test('guided plotting reveals one point at a time and provides a coordinate table',()=>{
 const c=container();renderCoordinateGraph(c,items('-1,-1','0,1','1,3'),'Lesson graph');
 const [svg,controls,status,table]=c.children;
 assert.equal(svg.attributes.role,'img');assert.equal(svg.attributes['aria-label'],'Lesson graph');assert.equal(table.children.length,5);
 const marks=svg.children.filter(n=>n.kind==='g').slice(1);
 controls.children[0].click();assert.ok(marks.every(n=>n.attributes.visibility==='hidden'));
 controls.children[1].click();assert.equal(marks[0].attributes.visibility,'visible');assert.equal(marks[1].attributes.visibility,'hidden');assert.match(status.textContent,/1 left.*1 down/);
 controls.children[2].click();assert.ok(marks.every(n=>n.attributes.visibility==='visible'));assert.equal(controls.children[1].disabled,true);
 assert.equal(svg.children.some(n=>n.kind==='polyline'),false);
});
test('empty coordinate data gives a safe explanation rather than a misleading graph',()=>{
 const c=container();renderCoordinateGraph(c,items('unreadable'));assert.equal(c.children[0].kind,'p');assert.match(c.children[0].textContent,/No readable/);
});

const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const source=fs.readFileSync('classroom/friendly_errors.js','utf8');
const start=source.indexOf('  function learnerMessage(');
const end=source.indexOf('\n  function decorate(',start);
const context={};vm.createContext(context);vm.runInContext(source.slice(start,end),context);
test('ordinary teaching numbers are never replaced with network errors',()=>{
 for(const text of ['Think of a 500 Naira note and a 200 Naira note.','500 Naira is five hundred naira.','Add 429 and 503.','Round 502 to the nearest ten.','The total is 504.','We have 429 students.'])assert.equal(context.learnerMessage(text),null,text);
});
test('explicit server and capacity failures remain friendly',()=>{
 for(const text of ['500','502','Error: 503','HTTP 504: Gateway Timeout','Internal server error','Bad gateway'])assert.equal(context.learnerMessage(text),'Something went wrong while preparing that. Please try again.',text);
 for(const text of ['429','HTTP 429: Too many requests','rate limit exceeded'])assert.equal(context.learnerMessage(text),'Robo-Teacher is busy right now. Please wait a moment, then try again.',text);
});

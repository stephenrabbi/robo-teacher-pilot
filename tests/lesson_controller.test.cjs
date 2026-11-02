const test=require('node:test');
const assert=require('node:assert/strict');
const {createLessonController}=require('../classroom/lesson_controller.js');
test('a learner question revokes an unfinished media request',()=>{
 const c=createLessonController();c.begin('lesson');const media=c.begin('media-loading');
 c.begin('question');assert.equal(c.owns(media),false);assert.equal(c.state().mode,'question');
});
test('returning to the lesson cannot revive old media work',()=>{
 const c=createLessonController();const media=c.begin('media-loading');c.begin('question');c.begin('lesson');
 assert.equal(c.owns(media),false);
});
test('latest request owns the presentation and reset revokes it',()=>{
 const c=createLessonController();const old=c.begin('media-loading');const next=c.begin('media-loading');
 assert.equal(c.owns(old),false);assert.equal(c.owns(next),true);c.begin('idle');assert.equal(c.owns(next),false);
});
test('invalid state does not revoke the current owner',()=>{
 const c=createLessonController();const t=c.begin('lesson');assert.throws(()=>c.begin('unknown'));assert.equal(c.owns(t),true);
});

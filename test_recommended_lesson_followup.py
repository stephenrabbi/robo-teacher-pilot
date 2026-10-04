"""Behaviour tests for the recommended lesson -> independent check handoff."""
from pathlib import Path
import subprocess


def test_recommended_lesson_followup_behaviour():
    script = r'''
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const source = fs.readFileSync('classroom/autonomous_planner.js', 'utf8');
const context = {Date, Boolean, setTimeout:()=>0, setInterval:()=>1, clearInterval:()=>{},
  currentLesson:null, lessonInterruption:null, currentProgress:null, sessionToken:null,
  window:{roboTeacherMasteryRecord:()=>{}}, MutationObserver:class {observe(){}},
  document:{querySelector:()=>null,getElementById:()=>null},
  renderDailyPlan:()=>{},openDailyPlan:()=>{},renderPracticeResults:()=>{}};
const node = () => ({value:'JSS2',classList:{contains:()=>true},addEventListener:()=>{},removeEventListener:()=>{}});
for(const name of ['learnerNickname','learnerClass','learnerCode','language','classroom','dailyPlanArea','chatForm','practiceButton','progressButton','changeLearnerButton','endLesson','understandingButton','checkStepUnderstanding','understandingArea','nextLessonStep']) context[name]=node();
vm.createContext(context);
vm.runInContext(source,context); // catches missing app bindings during module startup
const old={steps:['old'],index:0};
const make=()=>context.createRecommendedLessonFollowup({previousLesson:old,profile:'code-A',language:'English',startedAt:0});
const state=(lesson=old,extra={})=>({lesson,profile:'code-A',language:'English',now:1000,inChat:true,paused:false,checkReady:true,...extra});
let follow=make();
assert.equal(follow.observe(state()),'wait');
const lesson={steps:['step1','step2'],index:0};
assert.equal(follow.observe(state(lesson)),'wait');
lesson.index=1;
assert.equal(follow.observe(state(lesson,{paused:true})),'wait');
assert.equal(follow.observe(state(lesson,{checkReady:false})),'wait');
assert.equal(follow.observe(state(lesson)),'check');
assert.equal(follow.observe(state(lesson)),'check'); // stays ready until the learner chooses to check
lesson.index=0; assert.equal(follow.observe(state(lesson)),'wait');
lesson.index=1; assert.equal(follow.observe(state(lesson)),'check');
for(const change of [{profile:'code-B'},{language:'Yoruba'},{inChat:false},{now:1800001}]) {
  assert.equal(make().observe(state(lesson,change)),'cancel');
}
assert.equal(make().observe(state(old,{now:120001})),'cancel'); // failed response timeout
const repeated={steps:['old'],index:0};
assert.equal(make().observe(state(repeated)),'check'); // identical text, new lesson
follow=make(); lesson.index=0; assert.equal(follow.observe(state(lesson)),'wait');
assert.equal(follow.observe(state(repeated)),'cancel'); // replacement lesson
follow=make(); assert.equal(follow.observe(state(lesson)),'wait');
assert.equal(follow.observe(state(null)),'cancel'); // ended lesson
'''
    subprocess.run(['node','-e',script],check=True)


def test_followup_script_syntax():
    subprocess.run(['node','--check','classroom/autonomous_planner.js'],check=True)
    assert 'autonomous-plan5-followup1' in Path('classroom/daily_guidance_fix.js').read_text()

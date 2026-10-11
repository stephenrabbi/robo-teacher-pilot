// Regression checks for v2.6.1 browser continuity. Run: node --test tests/learner_continuity.test.cjs
// Executes the actual function definitions extracted from the shipped classroom script.
// No production endpoints or pupil records are accessed.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const source = fs.readFileSync(path.join(__dirname, '..', 'classroom', 'app.js'), 'utf8');
function extract(start, end) {
  const a = source.indexOf(start), b = source.indexOf(end, a + start.length);
  assert.ok(a >= 0 && b > a, 'Expected classroom functions are present');
  return source.slice(a, b);
}
function storage(initial = {}) {
  const values = new Map(Object.entries(initial));
  return {
    getItem: key => values.has(key) ? values.get(key) : null,
    setItem: (key, value) => values.set(key, String(value)),
    removeItem: key => values.delete(key),
  };
}
function snapshotHarness(localStorage, now = Date.now()) {
  const ctx = { localStorage, Date: class extends Date { static now() { return now; } } };
  vm.createContext(ctx);
  vm.runInContext(extract('function loadClassroomSnapshot(){', 'function refreshResumeLearning(){'), ctx);
  return ctx.loadClassroomSnapshot;
}
function adaptiveHarness(localStorage) {
  const ctx = { localStorage, learnerMemoryId: null, adaptiveMemory: {}, renderAdaptiveMemory() {} };
  vm.createContext(ctx);
  vm.runInContext(extract('function loadAdaptiveMemory(profileId){', 'function adaptiveSupportLevel(){'), ctx);
  return ctx;
}
test('a valid classroom snapshot resumes in the same browser within seven days', () => {
  const now = Date.now();
  const s = storage({roboTeacherClassroomSnapshot: JSON.stringify({classLevel:'JSS2', answer:'2x + 3 = 7', savedAt:now - 60000})});
  assert.equal(snapshotHarness(s, now)().answer, '2x + 3 = 7');
});
test('expired and malformed snapshots are rejected and cleared', () => {
  const now = Date.now();
  for (const value of ['{broken', JSON.stringify({classLevel:'JSS2', answer:'x=2', savedAt:now - 8*86400000}), JSON.stringify({classLevel:'INVALID', answer:'x=2', savedAt:now})]) {
    const s = storage({roboTeacherClassroomSnapshot:value});
    assert.equal(snapshotHarness(s, now)(), null);
    assert.equal(s.getItem('roboTeacherClassroomSnapshot'), null);
  }
});
test('saved browser state is not available in a separate browser storage', () => {
  const now = Date.now();
  const first = storage({roboTeacherClassroomSnapshot:JSON.stringify({classLevel:'JSS2',answer:'Worked example',savedAt:now})});
  assert.ok(snapshotHarness(first, now)());
  assert.equal(snapshotHarness(storage(), now)(), null);
});
test('adaptive memory remains separated by class and learner code', () => {
  const s = storage();
  const ctx = adaptiveHarness(s);
  ctx.loadAdaptiveMemory('JSS2:ISE-JSS2-001');
  ctx.recordLearningSignal('incorrect');
  ctx.loadAdaptiveMemory('JSS2:ISE-JSS2-002');
  assert.equal(ctx.adaptiveMemory.incorrect, 0);
  ctx.recordLearningSignal('correct');
  ctx.loadAdaptiveMemory('JSS2:ISE-JSS2-001');
  assert.equal(ctx.adaptiveMemory.incorrect, 1);
  assert.equal(ctx.adaptiveMemory.correct, 0);
  ctx.loadAdaptiveMemory('JSS3:ISE-JSS2-001');
  assert.equal(ctx.adaptiveMemory.incorrect, 0);
});
test('corrupt adaptive memory is recovered without cross-profile leakage', () => {
  const s = storage({'roboTeacherMemory:JSS2:A':'not json'});
  const ctx = adaptiveHarness(s);
  ctx.loadAdaptiveMemory('JSS2:A');
  assert.equal(ctx.adaptiveMemory.questions, 0);
  ctx.recordLearningSignal('questions');
  ctx.loadAdaptiveMemory('JSS2:A');
  assert.equal(ctx.adaptiveMemory.questions, 1);
});

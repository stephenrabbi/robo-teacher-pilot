/* Isolated per-session offline queue. Synthetic tests only, not classroom mounted. */
const sync = require('./browser_queue.cjs');
const active = new WeakMap();
function scopedKey(scope) {
  if (!scope || typeof scope !== 'object' || !/^[A-Za-z0-9_-]{1,100}$/.test(scope.school) || !/^[A-Za-z0-9_-]{1,100}$/.test(scope.subject))
    throw Error('Verified learner scope required');
  // The caller MUST derive this scope from a verified server session.
  return 'roboTeacherSyntheticQueue:v2:' + scope.school + ':' + scope.subject;
}
function wrapper(storage, scope) {
  const prefix = scopedKey(scope);
  return {
    getItem: () => storage.getItem(prefix),
    setItem: (_key, value) => storage.setItem(prefix, value),
  };
}
function queue(storage, scope, event) {
  return sync.enqueue(wrapper(storage,scope),event);
}
function pending(storage, scope) {
  return sync.read(wrapper(storage,scope)).length;
}
function flush(storage, scope, submit) {
  const key = scopedKey(scope);
  let byScope = active.get(storage);
  if (!byScope) { byScope = new Map(); active.set(storage,byScope); }
  if (byScope.has(key)) return byScope.get(key);
  const task = sync.flush(wrapper(storage,scope),submit).finally(() => {
    if (byScope.get(key) === task) byScope.delete(key);
  });
  byScope.set(key,task);
  return task;
}
module.exports = { queue, pending, flush, scopedKey };

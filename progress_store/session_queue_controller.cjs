/* Synthetic shared-device session controller. Not mounted in classroom.
 * Server must independently authenticate token and owner on each request.
 */
const scopedQueue = require('./scoped_browser_queue.cjs');
function createSessionController(storage) {
  let active = null;
  let generation = 0;
  function switchSession(session) {
    generation++;
    if (session === null) { active = null; return; }
    if (!session || typeof session.token !== 'string' || !session.token ||
      !session.scope || typeof session.scope.school !== 'string' ||
      typeof session.scope.subject !== 'string')
      throw Error('Verified session required');
    scopedQueue.scopedKey(session.scope);
    // Only the server can determine whether the credential is actually valid.
    active = {token:session.token, scope:Object.freeze({...session.scope}),generation};
  }
  function current() { return active ? {scope:{...active.scope},generation:active.generation} : null; }
  function queue(event) {
    if (!active) throw Error('No active session');
    return scopedQueue.queue(storage, active.scope, event);
  }
  async function flush(submit) {
    const session = active;
    if (!session) throw Error('No active session');
    // This guard is performed before each submission: stop the next event on switch.
    return scopedQueue.flush(storage, session.scope, async event => {
      if (active !== session || generation !== session.generation)
        throw Error('Session changed');
      return submit(event, session.token);
    });
  }
  return {switchSession,current,queue,flush};
}
module.exports = {createSessionController};

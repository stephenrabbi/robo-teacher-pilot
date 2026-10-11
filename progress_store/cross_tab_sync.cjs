/* Synthetic cross-tab synchronization guard; not wired into classroom.
 * Requires a browser Web Locks-compatible provider. Fails closed if absent.
 * Server-side event idempotency is still required.
 */
const scoped=require('./scoped_browser_queue.cjs');
function createCrossTabSync({storage,locks,scope}){
  const key=scoped.scopedKey(scope);
  if(!locks || typeof locks.request!=='function') throw Error('Cross-tab lock provider required');
  return {
    queue(event){return scoped.queue(storage,scope,event)},
    pending(){return scoped.pending(storage,scope)},
    async flush(submit){
      return locks.request('robo-teacher-sync:'+key,{mode:'exclusive'},async()=>{
        return scoped.flush(storage,scope,submit);
      });
    }
  };
}
module.exports={createCrossTabSync};

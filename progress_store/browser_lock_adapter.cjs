/* Browser Web Locks adapter for synthetic progress queue.
 * Not linked to production classroom. Requires a secure context and Web Locks support.
 */
const {createCrossTabSync}=require('./cross_tab_sync.cjs');
function createBrowserCrossTabSync({storage,scope,navigatorObject}){
  const nav=navigatorObject;
  if(!nav || !nav.locks || typeof nav.locks.request!=='function')
    throw Error('Browser Web Locks unavailable; synchronization disabled');
  return createCrossTabSync({storage,scope,locks:nav.locks});
}
module.exports={createBrowserCrossTabSync};

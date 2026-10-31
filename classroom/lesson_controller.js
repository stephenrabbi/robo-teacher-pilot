/* Presentation ownership for asynchronous lesson actions. */
(function(root){
  'use strict';
  function createLessonController(){
    let revision=0,mode='idle';
    const modes=new Set(['idle','lesson','question','media-loading','example','visual','check','paused','speech']);
    return Object.freeze({
      begin(next){
        if(!modes.has(next))throw new Error('Unknown lesson mode');
        mode=next;revision+=1;return revision;
      },
      owns(ticket){return ticket===revision;},
      state(){return Object.freeze({mode,revision});}
    });
  }
  if(typeof module==='object'&&module.exports)module.exports={createLessonController};
  else root.RoboTeacherLessonController={createLessonController};
})(typeof window==='undefined'?globalThis:window);

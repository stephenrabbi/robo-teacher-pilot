/* Presentation-only class chooser. Native select remains the single source of truth. */
(()=>{"use strict";
const select=document.getElementById("learnerClass");
const buttons=[...document.querySelectorAll("[data-class-choice]")];
if(!select||!buttons.length)return;
function sync(){for(const b of buttons){const active=b.dataset.classChoice===select.value;b.setAttribute("aria-pressed",String(active));b.classList.toggle("selected",active)}}
buttons.forEach(b=>b.addEventListener("click",()=>{select.value=b.dataset.classChoice;select.dispatchEvent(new Event("change",{bubbles:true}));sync()}));
select.addEventListener("change",sync);
document.getElementById("clearOnboarding")?.addEventListener("click",()=>queueMicrotask(sync));
sync();
})();
/* Image fallback prevents a broken hero during staged asset upload. */
for(const image of document.querySelectorAll('img[data-fallback-src]')){
  image.addEventListener('error',function(){
    const fallback=this.dataset.fallbackSrc;
    if(fallback && !this.dataset.fallbackApplied){this.dataset.fallbackApplied='true';this.src=fallback;}
  });
  if(image.complete && image.naturalWidth===0)image.dispatchEvent(new Event('error'));
}

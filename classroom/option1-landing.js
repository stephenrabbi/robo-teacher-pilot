/* Single editable source of truth for landing subjects.
   TODO: connect backend subject routing when additional curricula are implemented. */
const ROBO_SUBJECTS = [
  {name:"Maths", icon:"▦", colorKey:"maths", available:true},
  {name:"English", icon:"▤", colorKey:"english", available:false},
  {name:"Science", icon:"⚗", colorKey:"science", available:false},
  {name:"Coding", icon:"</>", colorKey:"coding", available:false},
  {name:"Social studies", icon:"◎", colorKey:"social", available:false},
  {name:"Exam prep", icon:"✧", colorKey:"exams", available:false}
];
(()=>{
"use strict";
const palette={
 maths:["#EFE9FF","#3A25A0"],english:["#FFE3EC","#9B1F4B"],
 science:["#D6F6EF","#0B6B59"],coding:["#DCEBFF","#1B58A8"],
 social:["#FFE5DD","#A8381C"],exams:["#FFF3C2","#7A5A00"]
};
let selectedSubject="maths";
const grid=document.getElementById("subjectGrid");
const nickname=document.getElementById("learnerNickname");
const form=document.querySelector("#welcome .welcome-copy");
if(!grid||!form)return;
for(const item of ROBO_SUBJECTS){
 const btn=document.createElement("button");btn.type="button";btn.className="subject-tile";
 const colors=palette[item.colorKey];btn.setAttribute("aria-disabled",String(!item.available));btn.style.background=colors[0];btn.style.color=colors[1];
 const symbol=document.createElement("span");symbol.className="subject-symbol";symbol.textContent=item.icon;
 const title=document.createElement("span");title.textContent=item.name;
 btn.append(symbol,title);
 if(!item.available){btn.disabled=true;const soon=document.createElement("small");soon.textContent="Coming soon";btn.append(soon)}
 else btn.addEventListener("click",()=>{
  selectedSubject=item.name.toLowerCase();const u=new URL(location.href);u.searchParams.set("subject",selectedSubject);
  history.replaceState(history.state,"",u);
  nickname?.focus({preventScroll:true});form.scrollIntoView({behavior:"smooth",block:"start"});
 });
 grid.append(btn);
}
document.getElementById("pitchClearButton")?.addEventListener("click",()=>document.getElementById("clearOnboarding")?.click());
const teacher=document.getElementById("newTeacherAccess");
const peekStatus=document.getElementById("peekStatus");
teacher?.addEventListener("click",()=>{document.getElementById("showTeacherLogin")?.click();form.scrollIntoView({behavior:"smooth",block:"center"})});
for(const button of document.querySelectorAll("[data-lesson-action]")){
 button.addEventListener("click",()=>{
  const mode=button.dataset.lessonAction;
  if(mode==="speak"){if("speechSynthesis" in window){speechSynthesis.cancel();speechSynthesis.speak(new SpeechSynthesisUtterance("Sunlight contains many colours. As it travels through the air, blue light scatters more than most other colours, making the sky appear blue."));if(peekStatus)peekStatus.textContent="Reading the sample lesson aloud.";}else if(peekStatus)peekStatus.textContent="Speech is unavailable in this browser.";return}
  if(mode==="snap"){if(peekStatus)peekStatus.textContent="Start learning to use the classroom camera.";form.scrollIntoView({behavior:"smooth",block:"start"});return}
  nickname?.focus({preventScroll:false});form.scrollIntoView({behavior:"smooth",block:"center"});
 });
}
const sticky=document.getElementById("mobileStartButton");
sticky?.addEventListener("click",()=>{
 const box=form.getBoundingClientRect();
 if(box.top<0||box.bottom>innerHeight-90){form.scrollIntoView({behavior:"smooth",block:"start"});nickname?.focus({preventScroll:true});return}
 document.getElementById("startLearning")?.click();
});
})();

/* Staged asset upgrade: only switch after the optimized files actually load.
   Files belong in classroom/images/ (requested names: images/hero.webp,
   images/hero-mobile.webp and images/herbert.webp). */
(()=>{
 const base="/classroom/";
 const hero=document.querySelector("#roboHeroPicture img[data-hero-src]");
 if(hero){
   const desktop=base+hero.dataset.heroSrc;
   const mobile=base+"images/hero-mobile.webp";
   const probe=new Image();
   probe.onload=()=>{
     const source=document.querySelector("#roboHeroPicture source");
     if(source)source.srcset=mobile;
     hero.src=desktop;
     hero.closest(".pitch-illustration")?.classList.add("hero-ready");
   };
   probe.src=desktop;
 }
 const founder=document.querySelector("img[data-founder-src]");
 if(founder){
   const probe=new Image();
   probe.onload=()=>{founder.src=base+founder.dataset.founderSrc;};
   probe.src=base+founder.dataset.founderSrc;
 }
})();

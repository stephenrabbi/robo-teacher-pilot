"""Static integration checks for the one-step mastery recheck browser loop."""
from pathlib import Path


def test_mastery_memory_loads_before_recheck_in_existing_enhancement_chain():
    guidance = Path("classroom/daily_guidance_fix.js").read_text()
    memory_asset = "mastery_memory.js?v=20260915-mastery-memory3"
    recheck_asset = "mastery_recheck.js?v=20260915-mastery-recheck3"
    assert memory_asset in guidance
    assert recheck_asset in guidance
    assert "data-mastery-memory" in guidance
    assert "data-mastery-recheck" in guidance
    assert "memory.addEventListener('load',loadRecheck,{once:true})" in guidance
    assert "document.head.appendChild(memory)" in guidance
    assert "if(window.roboTeacherMasteryRecord)loadRecheck()" in guidance


def test_mastery_recheck_intercepts_the_old_submit_handler_and_caps_retry_loop():
    script = Path("classroom/mastery_recheck.js").read_text()
    assert "understandingForm.addEventListener('submit'" in script
    assert "event.stopImmediatePropagation()" in script
    assert "const wasRetry = masteryRetryActive" in script
    assert "if (wasRetry)" in script
    assert "resetMasteryRetry()" in script


def test_wrong_answer_automatically_prepares_one_new_check_from_reteaching_feedback():
    script = Path("classroom/mastery_recheck.js").read_text()
    assert "fetch('/api/classroom/understanding/answer'" in script
    assert "fetch('/api/classroom/understanding/start'" in script
    assert "const retry = await prepareMasteryRetry(data.feedback, answeredCheckId)" in script
    assert "renderRetryCheck(retry)" in script
    assert "masteryRetryActive = true" in script


def test_follow_up_success_confirms_mastery_and_failure_stops_auto_retrying():
    script = Path("classroom/mastery_recheck.js").read_text()
    assert "wasRetry ? text.mastered : text.correct" in script
    assert "wasRetry ? text.masteredStatus" in script
    assert "text.needsReview" in script
    assert "text.needsReviewStatus" in script


def test_mastery_loop_has_copy_for_all_supported_classroom_languages():
    script = Path("classroom/mastery_recheck.js").read_text()
    for language in ("English", "Yoruba", "Igbo", "Hausa"):
        assert f"{language}: {{" in script

def test_new_check_resets_the_completed_submit_button_in_every_language():
    import subprocess
    script = r"""
const assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
const listeners={};
const button={disabled:true,textContent:'Correct'};
const context={
  understandingForm:{querySelector:()=>button,addEventListener:()=>{}},
  understandingButton:{addEventListener:(name,fn)=>{listeners.main=fn}},
  checkStepUnderstanding:{addEventListener:(name,fn)=>{listeners.step=fn}},
  closeUnderstandingButton:{addEventListener:()=>{}},
  language:{value:'English'},startUnderstandingCheck:async()=>{context.started=true}
};
vm.createContext(context);vm.runInContext(fs.readFileSync('classroom/mastery_recheck.js','utf8'),context);
for(const [lang,label] of [['English','Check my answer'],['Yoruba','Ṣàyẹ̀wò ìdáhùn mi'],['Igbo','Lelee azịza m'],['Hausa','Duba amsata']]){
  context.language.value=lang;
  for(const handler of [listeners.main,listeners.step]){
    button.disabled=true;button.textContent='Correct';handler();
    assert.equal(button.disabled,false);assert.equal(button.textContent,label);
  }
}
(async()=>{
  context.language.value='English';button.disabled=true;
  await context.startUnderstandingCheck();
  assert.equal(button.disabled,false);assert.equal(button.textContent,'Check my answer');
  assert.equal(context.started,true);
})().catch(error=>{throw error});
"""
    subprocess.run(['node','-e',script],check=True)


def test_delayed_answer_cannot_change_a_closed_question():
    import subprocess
    script = r"""
const assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
let submit,close,resolveResponse,started;
const ready=new Promise(r=>{started=r});
const feedback={textContent:'unchanged'};
const context={
 understandingForm:{querySelector:s=>s.startsWith('input')?{value:'0'}:{disabled:false},addEventListener:(n,f)=>{submit=f}},
 understandingButton:{addEventListener:()=>{}},checkStepUnderstanding:{addEventListener:()=>{}},
 closeUnderstandingButton:{addEventListener:(n,f)=>{close=f}},language:{value:'English'},
 understandingCheckId:'a'.repeat(32),understandingQuestion:{textContent:'2 + 2?'},
 understandingChoices:{querySelectorAll:()=>[{textContent:'3'}]},understandingFeedback:feedback,
 ensureSession:async()=> 'synthetic', fetch:()=>new Promise(r=>{resolveResponse=r;started()}),
 recordLearningSignal:()=>{throw Error('closed check changed learning signal')}
};
vm.createContext(context);vm.runInContext(fs.readFileSync('classroom/mastery_recheck.js','utf8'),context);
(async()=>{
 const pending=submit({preventDefault(){},stopImmediatePropagation(){}});
 await ready;close();
 resolveResponse({ok:true,json:async()=>({correct:false,correct_index:1,feedback:'Try again'})});
 await pending;assert.equal(feedback.textContent,'unchanged');
})().catch(e=>{console.error(e);process.exitCode=1});
"""
    subprocess.run(['node','-e',script],check=True)

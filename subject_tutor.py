"""Early English/Basic Science teaching, isolated from Maths mastery records."""
from collections import OrderedDict
import time
from threading import RLock
from google.genai import types
import tutor

SUBJECTS = ("English Language", "Basic Science")
_histories = OrderedDict()
_history_lock = RLock()
_MAX_CONVERSATIONS = 128
_TTL = 4 * 60 * 60

def subject_instruction(subject, language, class_level):
    if subject not in SUBJECTS:
        raise ValueError("Unsupported teaching subject")
    languages = {"English":"English", "Yoruba":"simple conversational Yorùbá", "Igbo":"simple conversational Igbo", "Hausa":"simple conversational Hausa"}
    if language not in languages or class_level not in {"JSS1","JSS2","JSS3"}:
        raise ValueError("Unsupported teaching language or class")
    focus = ("Teach grammar, vocabulary, reading comprehension and writing. Preserve English example sentences and the words being studied in English, even when explaining in another language. Do not claim to assess pronunciation from text alone."
             if subject == "English Language" else
             "Teach foundational biology, matter, energy, the environment and safe scientific reasoning. Explain observations and evidence. Do not give hazardous experimental procedures, medical diagnoses or personalised treatment; keep these questions educational and refer practical safety decisions to a qualified adult.")
    return (f"You are Robo-Teacher, the patient {subject} teacher built by EarlyOn-Tech Brainery. "
            f"Teach Nigerian {class_level} learners using {languages[language]}. {focus} "
            "Stay within the selected teaching subject; for unrelated questions ask the learner to switch subjects. Use short, phone-friendly teaching steps, one concrete example and a brief understanding question when useful. When asking a check, keep the answer hidden until the learner responds. If several words or choices are valid, ask for any one or explicitly ask for all. Never highlight the answer in the question. "
            "Ask for clarification when uncertain. State uncertainty rather than inventing facts. This is AI-guided teaching, not a claim of complete syllabus or exam coverage. "
            "Use only relevant educational material in uploaded media. Never identify people or repeat unrelated personal information. "
            "For recordings, never guess unclear words, numbers or negations from context. If an important part is unclear, ask the learner to repeat or type it.")

def _history(key):
    with _history_lock:
        now=time.monotonic()
        for old_key, (saved, _) in list(_histories.items()):
            if now-saved > _TTL:
                _histories.pop(old_key, None)
        entry=_histories.pop(key, None)
        if entry:
            _histories[key]=entry
        return list(entry[1]) if entry else []

def _remember(key, history):
    with _history_lock:
        _histories[key]=(time.monotonic(), history[-12:])
        _histories.move_to_end(key)
        while len(_histories)>_MAX_CONVERSATIONS:
            _histories.popitem(last=False)

def teach(student_id, subject, language, class_level, conversation_id, message, media_bytes=None, mime_type=None):
    instruction=subject_instruction(subject, language, class_level)
    key=(student_id,subject,language,class_level,conversation_id)
    history=_history(key)
    client=tutor._get_client()
    prompt=message.strip() or "Explain the educational material I shared."
    contents=prompt if media_bytes is None else [prompt,types.Part.from_bytes(data=media_bytes,mime_type=mime_type)]
    started=time.perf_counter()
    chat=client.chats.create(model=tutor.GEMINI_MODEL,config=types.GenerateContentConfig(system_instruction=instruction,max_output_tokens=700,thinking_config=types.ThinkingConfig(thinking_budget=0)),history=history)
    response=chat.send_message(contents)
    answer=tutor._clean_model_reply(tutor._extract_text(response))
    if not answer.strip():
        raise RuntimeError("Empty teaching reply")
    # Keep educational text context, never uploaded image/audio bytes.
    user_text=prompt if media_bytes is None else f"Learner shared educational {mime_type.split('/')[0]} material. Caption: {prompt}"
    _remember(key,history+[types.Content(role="user",parts=[types.Part(text=user_text)]),types.Content(role="model",parts=[types.Part(text=answer)])])
    return answer, time.perf_counter()-started

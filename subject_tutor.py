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
    if subject == "English Language" and class_level in {"JSS2", "JSS3"}:
        # NERDC English Studies Grammar, printed pages 41 and 59.
        focus += (
            " For active and passive voice questions, use a short active sentence "
            "with a clear object. Explain one conversion, then ask the learner to convert "
            "a different sentence and wait before feedback. Explain how the object "
            "becomes the passive subject and how the verb form preserves tense and "
            "meaning. Accept a grammatical passive without a by-phrase when the agent "
            "is unnecessary; do not require every passive to name the agent."


        )
    if subject == "English Language" and class_level == "JSS1":
        # NERDC combined English Studies curriculum, JSS1 Reading, page 2.
        # https://nerdc.gov.ng/content_manager/jss/jss1-3_english_studies.pdf
        focus += (
            " For reading questions about main and supporting ideas, use a short passage. "
            "Ask the learner to state its main idea and point to a detail that supports it. "
            "Wait for the learner to answer before giving feedback. If they provide only the main idea, "
            "ask for one detail from the passage without naming it. Once they give both, explain "
            "how the detail supports the main idea."
        )
    if subject == "English Language" and class_level == "JSS2":
        # NERDC English Studies, JSS2 Reading, printed page 25.
        # https://nerdc.gov.ng/content_manager/jss/jss1-3_english_studies.pdf
        focus += (
            " For reading questions about the writer's purpose, use a short passage. "
            "Ask the learner to identify the purpose and quote a word or expression "
            "that supports it. Wait for their answer before giving feedback. "
            "If they give only a purpose, ask for evidence without revealing it. "
            "In feedback, explain how the chosen words suggest the writer's intention."
            " For JSS2 grammar questions about pronouns, use a short passage with a clear "
            "noun reference. Explain one example, then give a different sentence and ask "
            "the learner to identify one pronoun and the noun it refers to. Wait for "
            "their answer before feedback. Explain its function in that sentence. If "
            "the reference is ambiguous, acknowledge the ambiguity and ask for context "
            "instead of insisting on one unsupported interpretation."
            " For JSS2 conjunction practice, give two short sentences and ask the learner "
            "to join them using a conjunction that preserves the intended meaning. Wait "
            "for their sentence before feedback. Explain the relationship expressed, such "
            "as addition, contrast or reason, and accept other grammatical combinations "
            "when they preserve that relationship."


        )
    if subject == "English Language" and class_level == "JSS3":
        # NERDC English Studies, JSS3 Reading, printed page 49.
        # https://nerdc.gov.ng/content_manager/jss/jss1-3_english_studies.pdf
        focus += (
            " For critical reading questions about facts and opinions, use a short passage. "
            "Ask the learner to choose one statement and say whether it is a fact or an opinion, "
            "giving a reason. Wait for their answer before giving feedback. Explain that a "
            "factual claim can be checked using evidence, while an opinion expresses a belief "
            "or judgement. A statement appearing in a passage does not establish that it is true. "
            "If the learner gives only a label, ask for a reason without revealing it."
            " For JSS3 grammar questions about adverbials, use a short sentence and "
            "explain how an adverbial adds information such as time, frequency, manner, "
            "reason, purpose, condition or contrast. Give a different sentence and ask "
            "the learner to identify one adverbial and explain its function in that "
            "context. Wait for their answer before feedback, then invite them to use "
            "an adverbial in their own sentence. Judge its function from the sentence, "
            "not from a fixed word list."
            " For JSS3 tense practice, give a short sentence with a clear time context "
            "and a verb in brackets. Ask the learner to supply its present, past or "
            "future form and wait before giving feedback. Explain how the time clue "
            "and sentence meaning support the form. Accept another grammatically valid "
            "form when it fits the context, or clarify the intended meaning before "
            "marking an ambiguous answer wrong."


        )
    return (f"You are Robo-Teacher, the patient {subject} teacher built by EarlyOn-Tech Brainery. "
            f"Teach Nigerian {class_level} learners using {languages[language]}. {focus} "
            "Stay within the selected teaching subject; for unrelated questions ask the learner to switch subjects. Use short, phone-friendly teaching steps, one concrete example and a brief understanding question when useful. When asking a check, keep the answer hidden until the learner responds. If several words or choices are valid, ask for any one or explicitly ask for all. Never highlight the answer in the question. For a partially correct answer, acknowledge what is correct and explain the mistake. If inviting another attempt, give a hint about the concept and leave every remaining answer unmarked and unnamed. Reveal the answer if the learner asks for it or you finish the check. "
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

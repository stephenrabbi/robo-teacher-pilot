"""Robo-Teacher — JSS2 Basic Maths tutor logic.

V2 adds pseudonymous adaptive learner memory plus image and voice tutoring while
preserving deterministic arithmetic and explicit escalation guardrails.
"""

import ast
import base64
import io
import logging
import operator
import os
import re
import time
import wave

from google import genai
from google.genai import types
from learner_profile import DEFAULT_PROFILE, load_profile, profile_prompt_context, update_profile_from_message

logger = logging.getLogger("robo-teacher.tutor")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
GEMINI_TTS_MODEL = os.getenv("GEMINI_TTS_MODEL", "gemini-2.5-flash-preview-tts")
SUPPORTED_IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
SUPPORTED_AUDIO_MIME_TYPES = {"audio/ogg", "audio/opus", "audio/mpeg", "audio/mp3", "audio/wav", "audio/x-wav", "audio/aac", "audio/flac", "audio/m4a", "audio/webm"}
MAX_IMAGE_BYTES = 8 * 1024 * 1024
MAX_AUDIO_BYTES = 12 * 1024 * 1024

CURRICULUM_TOPICS = """
- Revision of JSS1 topics: whole numbers and place value
- Factors, multiples, and prime numbers
- Lowest Common Multiple (LCM) and Highest Common Factor (HCF)
- Fractions: equivalent fractions, addition, subtraction, multiplication, division
- Decimals and conversions between fractions and decimals
- Approximation and estimation
- Ratio, proportion, and rate
- Basic algebraic expressions and simplification
- Simple linear equations
- Everyday arithmetic: profit, loss, and simple percentages
"""

ESCALATION_RESPONSE = "I don't want to guess and give you a wrong answer. This question is outside the Mathematics topics I'm currently set up to support. Please ask your teacher for help, or send me a JSS2 Maths question from the topics I support."
ESCALATION_MARKER = "[ESCALATE]"
TECHNICAL_FALLBACK_RESPONSE = "Sorry, I had a small technical hiccup while working on that. Please try the question again in a moment."
RATE_LIMIT_RESPONSE = "Lots of students are asking me questions right now, so I need a tiny break! Please try again in about a minute. 🙂"
SYSTEM_PROMPT = f"""You are Robo-Teacher, a warm, patient AI Maths tutor for JSS2 students in Nigeria, built by Earlyon-Tech Brainery.
Topics in scope:\n{CURRICULUM_TOPICS}
Rules:
- Explain step by step in simple language for ages 10-13.
- Use relatable Nigerian examples when useful.
- Show complete working; use plain-text maths, never LaTeX.
- Keep replies concise and phone-friendly.
- Adapt style and pacing using the supplied pseudonymous learner profile; profile signals are hints, not proof of mastery.
- For learner media, use only educational content needed for the Maths question. Ignore personal information and never identify people.
- If media is unclear or the spoken question cannot be understood reliably, ask the learner to resend/restate it rather than guessing.
- Teach the method rather than returning only a final answer.
- When a learner asks to explain, teach, show working, or go step by step, include the actual intermediate steps before the final answer.
- For fraction addition or subtraction, normally show how to get a common denominator before combining the fractions.
- End worked examples with a clearly labelled final answer, but do not repeat only the answer without the method.
- If outside the listed scope or unreliable, begin with exactly {ESCALATION_MARKER} on its own line.
"""

_MAX_TURNS = 6
_conversations: dict[str, list] = {}
_client = None

YORUBA_NUMBER_WORDS = {
    0: "Òdo",
    1: "Ọ̀kan",
    2: "Èjì",
    3: "Ẹ̀ta",
    4: "Ẹ̀rin",
    5: "Àrún",
    6: "Ẹ̀fà",
    7: "Èje",
    8: "Ẹ̀jọ",
    9: "Ẹ̀sán",
    10: "Ẹ̀wá",
    11: "Ọ̀kanlá",
    12: "Èjìlá",
    13: "Ẹ̀tàlá",
    14: "Ẹ̀rìnlá",
    15: "Ẹ̀ẹ́dógún",
    16: "Ẹ̀rìndínlógún",
    17: "Ẹ̀tàdínlógún",
    18: "Èjìdínlógún",
    19: "Ọ̀kàndínlógún",
    20: "Ogún",
}

IGBO_NUMBER_WORDS = {
    0: "Efu", 1: "Otu", 2: "Abụọ", 3: "Atọ", 4: "Anọ", 5: "Ise",
    6: "Isii", 7: "Asaa", 8: "Asatọ", 9: "Itoolu", 10: "Iri",
    11: "Iri na otu", 12: "Iri na abụọ", 13: "Iri na atọ", 14: "Iri na anọ",
    15: "Iri na ise", 16: "Iri na isii", 17: "Iri na asaa", 18: "Iri na asatọ",
    19: "Iri na itoolu", 20: "Iri abụọ",
}

HAUSA_NUMBER_WORDS = {
    0: "Sifili", 1: "Ɗaya", 2: "Biyu", 3: "Uku", 4: "Huɗu", 5: "Biyar",
    6: "Shida", 7: "Bakwai", 8: "Takwas", 9: "Tara", 10: "Goma",
    11: "Goma sha ɗaya", 12: "Goma sha biyu", 13: "Goma sha uku",
    14: "Goma sha huɗu", 15: "Goma sha biyar", 16: "Goma sha shida",
    17: "Goma sha bakwai", 18: "Goma sha takwas", 19: "Goma sha tara", 20: "Ashirin",
}

LOCALIZED_ANSWERS = {
    "Yoruba": ("Ìdáhùn", YORUBA_NUMBER_WORDS),
    "Igbo": ("Azịza", IGBO_NUMBER_WORDS),
    "Hausa": ("Amsa", HAUSA_NUMBER_WORDS),
}

TTS_VOICES = {"female": "Aoede", "male": "Charon"}
TTS_LANGUAGE_NAMES = {"English": "English", "Yoruba": "Yorùbá", "Igbo": "Igbo", "Hausa": "Hausa"}


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return _client


def _is_rate_limit_error(e: Exception) -> bool:
    text = str(e)
    return "429" in text or "RESOURCE_EXHAUSTED" in text or "quota" in text.lower()


def _pcm_to_wav(pcm: bytes) -> bytes:
    output = io.BytesIO()
    with wave.open(output, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(24000)
        wav_file.writeframes(pcm)
    return output.getvalue()


def _speech_chunks(text: str, max_chars: int = 700) -> list[str]:
    """Keep each TTS performance short enough to preserve one stable voice."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        pieces = [sentence[i:i + max_chars] for i in range(0, len(sentence), max_chars)] or [""]
        for piece in pieces:
            candidate = f"{current} {piece}".strip()
            if current and len(candidate) > max_chars:
                chunks.append(current)
                current = piece
            else:
                current = candidate
    if current:
        chunks.append(current)
    return chunks


def generate_tutor_speech(text: str, language: str = "English", voice_gender: str = "female") -> bytes:
    """Generate expressive teacher speech as a WAV file using Gemini TTS."""
    gender = "male" if voice_gender == "male" else "female"
    language_name = TTS_LANGUAGE_NAMES.get(language, "English")
    client = _get_client()
    pcm_chunks = []
    for chunk in _speech_chunks(text):
        prompt = (
            "Synthesize speech for the transcript below. Do not read these directions aloud. "
            f"Use the same unmistakably adult {gender} teacher voice speaking {language_name}. "
            "Sound warm, patient and conversational, with a gentle Nigerian classroom tone and a friendly vocal smile. "
            "Use the written punctuation for natural pauses, vary emphasis slightly, and avoid a stiff announcer cadence.\n\n"
            f"TRANSCRIPT:\n{chunk}"
        )
        last_error = None
        for _attempt in range(2):
            try:
                interaction = client.interactions.create(
                    model=GEMINI_TTS_MODEL,
                    input=prompt,
                    response_format={"type": "audio"},
                    generation_config={"speech_config": [{"voice": TTS_VOICES[gender]}]},
                )
                encoded = interaction.output_audio.data
                pcm = base64.b64decode(encoded) if isinstance(encoded, str) else bytes(encoded)
                if not pcm:
                    raise ValueError("Gemini TTS returned empty audio")
                pcm_chunks.append(pcm)
                break
            except Exception as exc:
                last_error = exc
        else:
            raise RuntimeError("Gemini TTS could not generate audio") from last_error
    return _pcm_to_wav(b"".join(pcm_chunks))


def _safe_arithmetic(expression: str):
    allowed = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod, ast.Pow: operator.pow, ast.USub: operator.neg, ast.UAdd: operator.pos}
    try:
        tree = ast.parse(expression, mode="eval")
        if sum(1 for _ in ast.walk(tree)) > 40: return None
        def evaluate(node):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool): return node.value
            if isinstance(node, ast.UnaryOp) and type(node.op) in allowed: return allowed[type(node.op)](evaluate(node.operand))
            if isinstance(node, ast.BinOp) and type(node.op) in allowed:
                left, right = evaluate(node.left), evaluate(node.right)
                if type(node.op) is ast.Pow and abs(right) > 10: raise ValueError("power too large")
                return allowed[type(node.op)](left, right)
            raise ValueError("unsupported expression")
        value = evaluate(tree.body)
        if isinstance(value, (int, float)) and abs(value) < 1e12 and value == value: return value
    except (SyntaxError, ValueError, TypeError, ZeroDivisionError, OverflowError): return None
    return None


def _wants_teaching(message: str) -> bool:
    """Detect requests where a worked explanation matters more than a terse answer."""
    text = message.lower()
    cues = (
        "step by step",
        "step-by-step",
        "show working",
        "show your working",
        "show the working",
        "explain",
        "teach me",
        "help me understand",
        "how do",
        "how to",
        "why",
    )
    return any(cue in text for cue in cues)


def _simple_arithmetic_answer(message: str, response_language: str = "English"):
    """Give deterministic answers only when the learner is asking for a short result.

    Explanatory requests deliberately go through the tutor model so Robo-Teacher
    can provide pedagogy and intermediate steps instead of merely evaluating the
    Python-like arithmetic expression.
    """
    if _wants_teaching(message):
        return None
    text = message.strip().lower().replace("×", "*").replace("÷", "/")
    text = re.sub(r"^(what is|calculate|compute|solve)\s+", "", text).rstrip("?.!")
    if not re.fullmatch(r"[0-9\s+\-*/().%]+", text) or "%" in text or not re.search(r"\d\s*[+\-*/]\s*\d", text): return None
    value = _safe_arithmetic(text)
    if value is None: return None
    if isinstance(value, float) and value.is_integer(): value = int(value)
    localized = LOCALIZED_ANSWERS.get(response_language)
    if localized:
        answer_label, number_words = localized
        localized_value = number_words.get(value, str(value))
        return f"{message.strip()} = {value}\n\n{answer_label}: {localized_value}"
    return f"{message.strip()} = {value}\n\nAnswer: {value}"


def _clean_model_reply(text: str) -> str:
    return ESCALATION_RESPONSE if text.strip().startswith(ESCALATION_MARKER) else text.strip()


def _safe_profile_update(student_id: str, message: str) -> dict:
    try: return update_profile_from_message(student_id, message)
    except Exception as exc:
        logger.error("Learner profile update failed for %s (%s); continuing with defaults", student_id, type(exc).__name__)
        try: return load_profile(student_id)
        except Exception: return dict(DEFAULT_PROFILE)


def _extract_text(response) -> str:
    try:
        if response.text: return response.text
    except Exception: pass
    try:
        texts = [p.text for p in response.candidates[0].content.parts if getattr(p, "text", None)]
        if texts: return "\n".join(texts)
    except Exception: pass
    raise ValueError("Gemini response contained no readable text")


def _language_instruction(response_language: str) -> str:
    language_details = {
        "Yoruba": ("Yorùbá", "Yorùbá"),
        "Igbo": ("Igbo", "Igbo"),
        "Hausa": ("Hausa", "Hausa"),
    }
    if response_language in language_details:
        language_name, number_word_language = language_details[response_language]
        return (
            f"The learner may ask the Maths question in {language_name} or English. Understand both languages, "
            f"but reply entirely in clear, natural {language_name} suitable for a Nigerian JSS2 learner. "
            "Write as a warm human teacher would speak: use complete sentences, natural punctuation, and short paragraphs. "
            "Use commas and full stops to create clear pauses when the answer is read aloud. "
            "Keep mathematical symbols and numerals in the working, but write the final-answer value "
            f"as a {number_word_language} number word."
        )
    return (
        "Detect whether the learner's current Maths question is in English, Yorùbá, Igbo, or Hausa. "
        "Reply entirely in the language used in the question. When replying in Yorùbá, Igbo, or Hausa, "
        "write as a warm human teacher would speak, using complete sentences, natural punctuation, and short paragraphs. "
        "Use commas and full stops to create clear pauses when the answer is read aloud. "
        "keep mathematical symbols and numerals in the working, but write the final-answer value as a "
        "number word in that language. Use language suitable for a Nigerian JSS2 learner."
    )


def get_tutor_reply(student_id: str, message: str, response_language: str = "English") -> tuple[str, float]:
    profile = _safe_profile_update(student_id, message)
    deterministic = _simple_arithmetic_answer(message, response_language)
    if deterministic is not None:
        return deterministic, 0.0
    start = time.time()
    try:
        client = _get_client()
    except Exception as exc:
        logger.error("Gemini client initialization failed (%s)", type(exc).__name__)
        return TECHNICAL_FALLBACK_RESPONSE, time.time() - start

    history = _conversations.get(student_id, [])
    try:
        text, new_history = _ask(client, history, message, profile, response_language)
    except Exception as first_error:
        if _is_rate_limit_error(first_error):
            return RATE_LIMIT_RESPONSE, time.time() - start
        logger.warning("Gemini request failed; retrying once without conversation history (%s)", type(first_error).__name__)
        try:
            text, new_history = _ask(client, [], message, profile, response_language)
        except Exception as retry_error:
            if _is_rate_limit_error(retry_error):
                return RATE_LIMIT_RESPONSE, time.time() - start
            logger.error("Gemini retry failed; returning safe technical fallback (%s)", type(retry_error).__name__)
            return TECHNICAL_FALLBACK_RESPONSE, time.time() - start

    _conversations[student_id] = new_history[-_MAX_TURNS * 2:]
    return _clean_model_reply(text), time.time() - start


def _media_reply(student_id: str, media_bytes: bytes, mime_type: str, prompt: str, profile_message: str, max_tokens: int = 700) -> tuple[str, float]:
    profile = _safe_profile_update(student_id, profile_message)
    adaptive_context = profile_prompt_context(profile)
    client, start = _get_client(), time.time()
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[f"{adaptive_context}\n\n{prompt}", types.Part.from_bytes(data=media_bytes, mime_type=mime_type)],
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT, max_output_tokens=max_tokens, thinking_config=types.ThinkingConfig(thinking_budget=0)),
    )
    return _clean_model_reply(_extract_text(response)), time.time() - start


def get_tutor_image_reply(student_id: str, image_bytes: bytes, mime_type: str, caption: str = "", response_language: str = "English") -> tuple[str, float]:
    if mime_type not in SUPPORTED_IMAGE_MIME_TYPES: raise ValueError("Unsupported image type")
    if not image_bytes or len(image_bytes) > MAX_IMAGE_BYTES: raise ValueError("Image is empty or too large")
    learning_message = caption.strip() or "Please help me understand the Maths problem in this image."
    prompt = f"{_language_instruction(response_language)}\nThe learner sent a Maths image. Read only the educational content. If unclear, request a clearer photo. Otherwise teach the method step by step.\nLearner caption: {learning_message}"
    return _media_reply(student_id, image_bytes, mime_type, prompt, learning_message)


def get_tutor_audio_reply(student_id: str, audio_bytes: bytes, mime_type: str, response_language: str = "English") -> tuple[str, float]:
    """Understand a learner's voice note and answer the spoken Maths question in text."""
    if mime_type not in SUPPORTED_AUDIO_MIME_TYPES: raise ValueError("Unsupported audio type")
    if not audio_bytes or len(audio_bytes) > MAX_AUDIO_BYTES: raise ValueError("Audio is empty or too large")
    profile_message = "Learner used a voice note for a Maths question."
    prompt = (
        f"{_language_instruction(response_language)} Listen to the learner voice note in English, Yorùbá, Igbo, or Hausa with a safety-first transcription rule. Before solving, silently verify every spoken number, sign, operator, and equation term from the audio itself. "
        "Do not infer a number because it makes the Maths easier or seems more likely. Pay special attention to easily confused spoken numbers such as seven versus seventeen, four versus fourteen, six versus sixteen, and similar pairs. "
        "If any number, operator, or important word is muffled, clipped, masked by background noise, or could plausibly have been heard another way, DO NOT solve the problem. Instead say that you may not have heard the question correctly and ask the learner to resend the voice note more clearly or type the equation. "
        "Only when every essential Maths token is clear should you answer the spoken question as a patient teacher and explain the method step by step in text. "
        "Never invent missing words or digits, and do not reproduce unrelated personal information that may be spoken in the recording."
    )
    return _media_reply(student_id, audio_bytes, mime_type, prompt, profile_message)


def _ask(client, history: list, message: str, profile: dict, response_language: str = "English") -> tuple[str, list]:
    chat = client.chats.create(model=GEMINI_MODEL, config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT, max_output_tokens=600, thinking_config=types.ThinkingConfig(thinking_budget=0)), history=history)
    response = chat.send_message(f"{profile_prompt_context(profile)}\n\n{_language_instruction(response_language)}\n\nCurrent student message:\n{message}")
    return _extract_text(response), chat.get_history()

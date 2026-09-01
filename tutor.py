"""Robo-Teacher — JSS2 Basic Maths tutor logic.

V2 adds pseudonymous adaptive learner memory and multimodal homework support
while preserving deterministic arithmetic and explicit escalation guardrails.
"""

import ast
import logging
import operator
import os
import re
import time

from google import genai
from google.genai import types

from learner_profile import DEFAULT_PROFILE, load_profile, profile_prompt_context, update_profile_from_message

logger = logging.getLogger("robo-teacher.tutor")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
SUPPORTED_IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_BYTES = 8 * 1024 * 1024

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

ESCALATION_RESPONSE = (
    "I don't want to guess and give you a wrong answer. This question is outside "
    "the Mathematics topics I'm currently set up to support. Please ask your teacher "
    "for help, or send me a JSS2 Maths question from the topics I support."
)
ESCALATION_MARKER = "[ESCALATE]"

SYSTEM_PROMPT = f"""You are Robo-Teacher, a warm, fun, patient AI Maths tutor for JSS2 students in Nigeria, built by Earlyon-Tech Brainery. Talk the way a kind teacher would talk to a bright, curious 10-year-old — simple words, short sentences, playful and encouraging.

Your job is to help students understand Basic Mathematics topics from the JSS2 first-term scheme of work, aligned with the NERDC curriculum. The topics currently in scope are:
{CURRICULUM_TOPICS}

How to behave:
- Explain things step by step, in simple language a 10-13 year old can follow.
- Use relatable, everyday Nigerian examples when useful.
- Always show complete step-by-step working.
- NEVER use LaTeX. Write maths in plain text.
- Keep replies reasonably short and easy to read on a phone screen.
- Adapt style, pacing, examples, and challenge level using the supplied learner profile.
- Treat profile signals as hints, not proof of mastery.
- For an uploaded homework image, first read only the educational content needed for the question. Ignore faces, names, phone numbers, school IDs, addresses, or other personal details that may appear in the image. Never identify a person from an image.
- If an image is blurry, cropped, unreadable, or the Maths problem cannot be established reliably, ask the learner to send a clearer photo instead of guessing.
- When solving from an image, teach through the problem step by step rather than returning only a final answer.
- If the question is outside the listed JSS2 Maths scope, or you cannot answer it reliably, begin your response with exactly {ESCALATION_MARKER} on its own line.
"""

_MAX_TURNS = 6
_conversations: dict[str, list] = {}
_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return _client


def _is_rate_limit_error(e: Exception) -> bool:
    text = str(e)
    return "429" in text or "RESOURCE_EXHAUSTED" in text or "quota" in text.lower()


def _safe_arithmetic(expression: str):
    allowed = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod, ast.Pow: operator.pow, ast.USub: operator.neg, ast.UAdd: operator.pos}
    try:
        tree = ast.parse(expression, mode="eval")
        if sum(1 for _ in ast.walk(tree)) > 40:
            return None
        def evaluate(node):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
                return node.value
            if isinstance(node, ast.UnaryOp) and type(node.op) in allowed:
                return allowed[type(node.op)](evaluate(node.operand))
            if isinstance(node, ast.BinOp) and type(node.op) in allowed:
                left, right = evaluate(node.left), evaluate(node.right)
                if type(node.op) is ast.Pow and abs(right) > 10:
                    raise ValueError("power too large")
                return allowed[type(node.op)](left, right)
            raise ValueError("unsupported expression")
        value = evaluate(tree.body)
        if isinstance(value, (int, float)) and abs(value) < 1e12 and value == value:
            return value
    except (SyntaxError, ValueError, TypeError, ZeroDivisionError, OverflowError):
        return None
    return None


def _simple_arithmetic_answer(message: str):
    text = message.strip().lower().replace("×", "*").replace("÷", "/")
    text = re.sub(r"^(what is|calculate|compute|solve)\s+", "", text).rstrip("?.!")
    if not re.fullmatch(r"[0-9\s+\-*/().%]+", text) or "%" in text:
        return None
    if not re.search(r"\d\s*[+\-*/]\s*\d", text):
        return None
    value = _safe_arithmetic(text)
    if value is None:
        return None
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return f"Let's work it out step by step.\n\n{message.strip()} = {value}\n\nAnswer: {value}"


def _clean_model_reply(text: str) -> str:
    return ESCALATION_RESPONSE if text.strip().startswith(ESCALATION_MARKER) else text.strip()


def _safe_profile_update(student_id: str, message: str) -> dict:
    try:
        return update_profile_from_message(student_id, message)
    except Exception:
        logger.exception("Learner profile update failed for %s; continuing with defaults", student_id)
        try:
            return load_profile(student_id)
        except Exception:
            return dict(DEFAULT_PROFILE)


def _extract_text(response) -> str:
    try:
        if response.text:
            return response.text
    except Exception:
        pass
    try:
        texts = [p.text for p in response.candidates[0].content.parts if getattr(p, "text", None)]
        if texts:
            return "\n".join(texts)
    except Exception:
        pass
    raise ValueError("Gemini response contained no readable text")


def get_tutor_reply(student_id: str, message: str) -> tuple[str, float]:
    profile = _safe_profile_update(student_id, message)
    deterministic = _simple_arithmetic_answer(message)
    if deterministic is not None:
        return deterministic, 0.0
    client = _get_client()
    history = _conversations.get(student_id, [])
    start = time.time()
    try:
        text, new_history = _ask(client, history, message, profile)
    except Exception as e:
        if _is_rate_limit_error(e):
            return "Lots of students are asking me questions right now, so I need a tiny break! Please try again in about a minute. 🙂", time.time() - start
        text, new_history = _ask(client, [], message, profile)
    latency = time.time() - start
    _conversations[student_id] = new_history[-_MAX_TURNS * 2:]
    return _clean_model_reply(text), latency


def get_tutor_image_reply(student_id: str, image_bytes: bytes, mime_type: str, caption: str = "") -> tuple[str, float]:
    """Teach from a learner-provided Maths image without persisting image bytes."""
    if mime_type not in SUPPORTED_IMAGE_MIME_TYPES:
        raise ValueError("Unsupported image type")
    if not image_bytes or len(image_bytes) > MAX_IMAGE_BYTES:
        raise ValueError("Image is empty or too large")

    learning_message = caption.strip() or "Please help me understand the Maths problem in this image."
    profile = _safe_profile_update(student_id, learning_message)
    adaptive_context = profile_prompt_context(profile)
    prompt = (
        f"{adaptive_context}\n\n"
        "The learner sent a homework or Maths image. Read the Maths problem carefully. "
        "Ignore personal information and non-educational details. If the problem is not clear enough to solve reliably, ask for a clearer photo. "
        "Otherwise explain it step by step and help the learner understand the method.\n\n"
        f"Learner caption: {learning_message}"
    )
    client = _get_client()
    start = time.time()
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[prompt, types.Part.from_bytes(data=image_bytes, mime_type=mime_type)],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=700,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )
    return _clean_model_reply(_extract_text(response)), time.time() - start


def _ask(client, history: list, message: str, profile: dict) -> tuple[str, list]:
    adaptive_context = profile_prompt_context(profile)
    chat = client.chats.create(
        model=GEMINI_MODEL,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT, max_output_tokens=600, thinking_config=types.ThinkingConfig(thinking_budget=0)),
        history=history,
    )
    response = chat.send_message(f"{adaptive_context}\n\nCurrent student message:\n{message}")
    return _extract_text(response), chat.get_history()

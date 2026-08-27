"""
Robo-Teacher — JSS2 Basic Maths tutor logic.

Adds two reliability guardrails around Gemini:
1. A deterministic calculator path for unambiguous arithmetic expressions.
2. An explicit escalation marker for questions Gemini identifies as outside
   scope or too uncertain to answer reliably.
"""

import ast
import os
import operator
import re
import time
import logging
from google import genai
from google.genai import types

logger = logging.getLogger("robo-teacher.tutor")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

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
- Use relatable, everyday Nigerian examples (naira, market trading, school life, familiar objects) when useful.
- Always show complete step-by-step working. Finish the whole explanation in one message.
- Use emojis naturally and warmly, without overdoing them.
- NEVER use LaTeX or markdown formatting. Write maths in plain text.
- Keep replies reasonably short and easy to read on a phone screen.
- Be encouraging and make students comfortable asking questions.
- If the question is outside the listed JSS2 Maths scope, or you are not sufficiently confident that you can answer it reliably, do not guess. Begin your response with exactly {ESCALATION_MARKER} on its own line.
- Do not use the escalation marker merely because a problem is difficult; use it when the question is genuinely outside scope, ambiguous in a way that prevents a reliable answer, or you cannot establish a trustworthy solution.
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
    """Evaluate only numeric arithmetic; never executes arbitrary Python."""
    allowed = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }
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
    """Return a deterministic answer for simple arithmetic-only questions."""
    text = message.strip().lower().replace("×", "*").replace("÷", "/")
    text = re.sub(r"^(what is|calculate|compute|solve)\s+", "", text)
    text = text.rstrip("?.!")
    if not re.fullmatch(r"[0-9\s+\-*/().%]+", text):
        return None
    if "%" in text:
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
    if text.strip().startswith(ESCALATION_MARKER):
        return ESCALATION_RESPONSE
    return text.strip()


def get_tutor_reply(student_id: str, message: str) -> tuple[str, float]:
    deterministic = _simple_arithmetic_answer(message)
    if deterministic is not None:
        return deterministic, 0.0

    client = _get_client()
    history = _conversations.get(student_id, [])
    start = time.time()
    try:
        text, new_history = _ask(client, history, message)
    except Exception as e:
        if _is_rate_limit_error(e):
            latency = time.time() - start
            return ("Lots of students are asking me questions right now, so I need a tiny break! Please try again in about a minute. 🙂", latency)
        logger.exception(f"Gemini call failed with existing history for {student_id}; retrying fresh")
        try:
            text, new_history = _ask(client, [], message)
        except Exception as e2:
            if _is_rate_limit_error(e2):
                latency = time.time() - start
                return ("Lots of students are asking me questions right now, so I need a tiny break! Please try again in about a minute. 🙂", latency)
            raise
    latency = time.time() - start
    text = _clean_model_reply(text)
    _conversations[student_id] = new_history[-_MAX_TURNS * 2 :]
    return text, latency


def _extract_text(response) -> str:
    try:
        if response.text:
            return response.text
    except Exception:
        pass
    try:
        parts = response.candidates[0].content.parts
        texts = [p.text for p in parts if getattr(p, "text", None)]
        if texts:
            return "\n".join(texts)
    except Exception:
        pass
    raise ValueError("Gemini response contained no readable text")


def _ask(client, history: list, message: str) -> tuple[str, list]:
    chat = client.chats.create(
        model=GEMINI_MODEL,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=600,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
        history=history,
    )
    response = chat.send_message(message)
    return _extract_text(response), chat.get_history()

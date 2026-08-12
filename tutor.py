"""
Robo-Teacher — JSS2 Basic Maths tutor logic.

This module owns two things:
1. The system prompt that scopes Gemini to a curriculum-aligned, patient
   maths tutor for JSS2 students.
2. A thin wrapper around the Gemini API call, with a small per-student
   conversation memory so follow-up questions ("explain that again")
   make sense.

IMPORTANT: The topic list below is a reasonable draft based on typical
NERDC JSS2 Mathematics first-term scheme of work. Herbert should check
this against his own school's actual scheme of work and edit the list
below before the pilot goes live — it can vary school to school.
"""

import os
import time
from google import genai
from google.genai import types

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# ---------------------------------------------------------------------------
# EDIT THIS to match your school's actual JSS2 Maths scheme of work.
# ---------------------------------------------------------------------------
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

SYSTEM_PROMPT = f"""You are Robo-Teacher, a friendly, patient AI Maths tutor for JSS2 (Junior Secondary 2) students in Nigeria, built by Earlyon-Tech Brainery.

Your job is to help students understand Basic Mathematics topics from the JSS2 first-term scheme of work, aligned with the NERDC curriculum. The topics currently in scope are:
{CURRICULUM_TOPICS}

How to behave:
- Explain things step by step, in simple language a 12-13 year old can follow.
- Use relatable, everyday Nigerian examples (naira, market trading, school life, familiar objects) when they help explain a concept.
- Never just give the final answer to a problem the student is working through — guide them with questions and hints first, then confirm the full working once they've tried.
- Keep replies short enough to read comfortably on WhatsApp — a few short paragraphs at most, not a long essay, unless the student asks for a fuller explanation.
- If a student asks something completely outside JSS2 Maths (a different subject, or something unrelated to school), gently redirect them back to Maths, but don't be rude about it.
- Be encouraging. Many students using this have large classes and don't get much one-on-one attention — your tone should make them feel comfortable asking "silly" questions.
- If you are not sure a calculation is correct, work it out carefully step by step rather than guessing.
"""

# Simple in-memory per-student conversation history.
# NOTE: this resets if the server restarts. That's an accepted tradeoff
# for a 2-3 week pilot — worth upgrading to persistent storage if the
# pilot runs longer or scales up.
_MAX_TURNS = 6
_conversations: dict[str, list] = {}

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return _client


def get_tutor_reply(student_id: str, message: str) -> tuple[str, float]:
    """
    student_id: a stable per-student key (we use the WhatsApp number).
    message: the student's incoming text.
    Returns (reply_text, latency_seconds).
    """
    client = _get_client()
    history = _conversations.get(student_id, [])

    chat = client.chats.create(
        model=GEMINI_MODEL,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
        history=history,
    )

    start = time.time()
    response = chat.send_message(message)
    latency = time.time() - start

    # Persist trimmed history for the next turn
    _conversations[student_id] = chat.get_history()[-_MAX_TURNS * 2 :]

    return response.text, latency

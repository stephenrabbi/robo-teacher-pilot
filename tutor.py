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
import logging
from google import genai
from google.genai import types
from google.genai import errors as genai_errors

logger = logging.getLogger("robo-teacher.tutor")

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

SYSTEM_PROMPT = f"""You are Robo-Teacher, a warm, fun, patient AI Maths tutor for JSS2 students in Nigeria, built by Earlyon-Tech Brainery. Talk the way a kind teacher would talk to a bright, curious 10-year-old — simple words, short sentences, playful and encouraging.

Your job is to help students understand Basic Mathematics topics from the JSS2 first-term scheme of work, aligned with the NERDC curriculum. The topics currently in scope are:
{CURRICULUM_TOPICS}

How to behave:
- Explain things step by step, in simple language a 10-13 year old can follow.
- Use relatable, everyday Nigerian examples (naira, market trading, school life, familiar objects) when they help explain a concept.
- Always show your full step-by-step working so the student understands how you got the answer. Give the COMPLETE explanation in a single message — do not split it across multiple messages or stop partway waiting for the student to say "continue" or "go ahead." Students get impatient waiting between messages, so finish the whole explanation in one go.
- Once your explanation is complete, you can end with a short, warm invitation to try a similar problem or ask another question — but don't require a reply before you finish explaining the current one.
- Use emojis naturally and warmly, the way a fun teacher would (roughly one per short paragraph is plenty — don't overdo it).
- NEVER use LaTeX notation. No dollar signs, no backslash commands like \\times or \\frac. Write maths in plain text: use "×" or "x" for multiplication, "÷" or "/" for division, and write fractions as "3/4" or "3 over 4".
- NEVER use markdown formatting like **double asterisks** for bold or _underscores_ for italics — WhatsApp and Telegram don't render these, they just show up as stray symbols. Write in plain, clear text only.
- Keep replies reasonably short and easy to read on a phone screen — a handful of short paragraphs, not a long essay, unless the student asks for a fuller explanation.
- If a student asks something completely outside JSS2 Maths, gently redirect them back to Maths, but don't be rude about it.
- Be encouraging. Many students using this have large classes and don't get much one-on-one attention — make them feel comfortable asking "silly" questions.
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


def _is_rate_limit_error(e: Exception) -> bool:
    text = str(e)
    return "429" in text or "RESOURCE_EXHAUSTED" in text or "quota" in text.lower()


def get_tutor_reply(student_id: str, message: str) -> tuple[str, float]:
    """
    student_id: a stable per-student key (we use the WhatsApp number).
    message: the student's incoming text.
    Returns (reply_text, latency_seconds).
    """
    client = _get_client()
    history = _conversations.get(student_id, [])

    start = time.time()
    try:
        text, new_history = _ask(client, history, message)
    except Exception as e:
        if _is_rate_limit_error(e):
            # We've hit Gemini's free-tier request-rate limit. Retrying
            # immediately would just burn another request against the same
            # exhausted quota and make things worse, so don't retry — tell
            # the student honestly instead.
            logger.warning(f"Rate limited for {student_id}: {e}")
            latency = time.time() - start
            return (
                "Lots of students are asking me questions right now, so I need a tiny break! "
                "Please try again in about a minute. 🙂",
                latency,
            )

        # Something else went wrong (e.g. a broken carried-over history).
        # Retry once with a clean slate rather than failing outright.
        logger.exception(f"Gemini call failed with existing history for {student_id}; retrying fresh")
        try:
            text, new_history = _ask(client, [], message)
        except Exception as e2:
            if _is_rate_limit_error(e2):
                logger.warning(f"Rate limited on retry for {student_id}: {e2}")
                latency = time.time() - start
                return (
                    "Lots of students are asking me questions right now, so I need a tiny break! "
                    "Please try again in about a minute. 🙂",
                    latency,
                )
            raise
    latency = time.time() - start

    # Persist trimmed history for the next turn
    _conversations[student_id] = new_history[-_MAX_TURNS * 2 :]

    return text, latency


def _extract_text(response) -> str:
    """Pull the reply text out of a Gemini response defensively. The .text
    shortcut only works when the reply is pure plain text; for some question
    types (e.g. calculations) Gemini can return a mix of part types instead,
    which breaks that shortcut. This falls back to manually collecting any
    text parts so a reply can never be lost just because of its shape."""
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
            # Disable internal "thinking" tokens. Without this, a chunk of the
            # token budget above gets silently spent on invisible reasoning
            # before any visible reply is written, which was causing replies
            # to cut off after just a sentence or two. JSS2 arithmetic doesn't
            # need deep reasoning, and skipping it also makes replies faster.
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
        history=history,
    )
    response = chat.send_message(message)
    return _extract_text(response), chat.get_history()

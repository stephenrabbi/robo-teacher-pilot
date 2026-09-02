"""Pseudonymous adaptive learner profiles for Robo-Teacher V2.

Stores learning-related signals keyed by Pilot ID. Recent-question memory is
redacted before durable storage to reduce accidental retention of direct PII.
"""

import datetime
import json
import os
import re
from copy import deepcopy

import gspread

_PROFILE_HEADER = [
    "Pilot ID",
    "Topic Counts JSON",
    "Last Topic",
    "Recent Questions JSON",
    "Preferred Explanation Style",
    "Difficulty Level",
    "Language Preference",
    "Updated At",
]

DEFAULT_PROFILE = {
    "topic_counts": {},
    "last_topic": "",
    "recent_questions": [],
    "preferred_explanation_style": "step-by-step",
    "difficulty_level": "standard",
    "language_preference": "English",
}

_TOPIC_PATTERNS = [
    ("Factors/HCF/LCM", r"\b(factors?|multiples?|prime|hcf|lcm)\b"),
    ("Fractions/Decimals", r"\b(fractions?|decimals?|numerator|denominator)\b|\d+\s*/\s*\d+"),
    ("Percentages/Ratio", r"\b(percent|percentage|percentages|ratio|ratios|proportion|proportions|rate|rates)\b|%"),
    ("Algebra", r"\b(algebra|equations?|expressions?|variables?|coefficients?)\b|\bsolve\s+[a-z]\b"),
    ("Financial Mathematics", r"\b(profit|loss|discount|interest|cost price|selling price)\b"),
    ("Number Operations", r"\b(add|subtract|multiply|divide|addition|subtraction|multiplication|division|whole numbers?|place value)\b"),
]

# Conservative patterns for common direct identifiers learners may accidentally
# type into a Maths message. This is minimization, not a claim of perfect PII detection.
_EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
# Nigerian mobile numbers: local 11-digit form (e.g. 0802...) or +234/234 form.
# Separators are allowed between digit groups while preserving surrounding Maths numbers.
_PHONE_RE = re.compile(
    r"(?<!\w)(?:"
    r"0[789][01][\s-]?\d{3}[\s-]?\d{4}"
    r"|\+?234[\s-]?[789][01][\s-]?\d{3}[\s-]?\d{4}"
    r")(?!\w)"
)
_TELEGRAM_HANDLE_RE = re.compile(r"(?<!\w)@[A-Za-z0-9_]{5,32}\b")

_client = None
_profile_ws = None
_cache: dict[str, dict] = {}


def _get_client():
    global _client
    if _client is None:
        creds_dict = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
        _client = gspread.service_account_from_dict(creds_dict)
    return _client


def _get_profile_worksheet():
    global _profile_ws
    if _profile_ws is None:
        sh = _get_client().open_by_key(os.environ["GOOGLE_SHEET_ID"])
        try:
            _profile_ws = sh.worksheet("Learner Profiles")
        except gspread.WorksheetNotFound:
            _profile_ws = sh.add_worksheet(title="Learner Profiles", rows=300, cols=len(_PROFILE_HEADER))
            _profile_ws.append_row(_PROFILE_HEADER)
    return _profile_ws


def classify_topic(message: str) -> str:
    text = message.lower()
    for topic, pattern in _TOPIC_PATTERNS:
        if re.search(pattern, text):
            return topic
    return "General Mathematics"


def redact_recent_question(message: str) -> str:
    """Redact common direct identifiers before storing short-term learning context."""
    text = message.strip()
    text = _EMAIL_RE.sub("[email redacted]", text)
    text = _PHONE_RE.sub("[phone redacted]", text)
    text = _TELEGRAM_HANDLE_RE.sub("[handle redacted]", text)
    return text[:180]


def _infer_preferences(profile: dict, message: str) -> None:
    text = message.lower()
    if any(p in text for p in ("simpler", "simple way", "explain simply", "easy way")):
        profile["preferred_explanation_style"] = "simple"
    elif any(p in text for p in ("example", "real life", "another example")):
        profile["preferred_explanation_style"] = "example-led"
    elif any(p in text for p in ("quiz me", "test me", "give me practice", "practice question")):
        profile["preferred_explanation_style"] = "practice-led"

    if any(p in text for p in ("harder", "challenge me", "more difficult")):
        profile["difficulty_level"] = "challenging"
    elif any(p in text for p in ("easier", "too hard", "make it easy")):
        profile["difficulty_level"] = "supportive"

    if "yoruba" in text:
        profile["language_preference"] = "Yoruba"
    elif "hausa" in text:
        profile["language_preference"] = "Hausa"
    elif "igbo" in text:
        profile["language_preference"] = "Igbo"
    elif "english" in text:
        profile["language_preference"] = "English"


def _deserialize_row(row: dict) -> dict:
    profile = deepcopy(DEFAULT_PROFILE)
    try:
        profile["topic_counts"] = json.loads(str(row.get("Topic Counts JSON", "{}")) or "{}")
    except (TypeError, json.JSONDecodeError):
        profile["topic_counts"] = {}
    try:
        profile["recent_questions"] = json.loads(str(row.get("Recent Questions JSON", "[]")) or "[]")
    except (TypeError, json.JSONDecodeError):
        profile["recent_questions"] = []
    profile["last_topic"] = str(row.get("Last Topic", "")).strip()
    profile["preferred_explanation_style"] = str(row.get("Preferred Explanation Style", "")).strip() or "step-by-step"
    profile["difficulty_level"] = str(row.get("Difficulty Level", "")).strip() or "standard"
    profile["language_preference"] = str(row.get("Language Preference", "")).strip() or "English"
    return profile


def load_profile(pilot_id: str) -> dict:
    """Load a profile by pseudonymous Pilot ID, returning safe defaults if absent."""
    if pilot_id in _cache:
        return deepcopy(_cache[pilot_id])

    ws = _get_profile_worksheet()
    for row in ws.get_all_records():
        if str(row.get("Pilot ID", "")).strip() == pilot_id:
            profile = _deserialize_row(row)
            _cache[pilot_id] = profile
            return deepcopy(profile)

    profile = deepcopy(DEFAULT_PROFILE)
    _cache[pilot_id] = profile
    return deepcopy(profile)


def _serialize_row(pilot_id: str, profile: dict) -> list:
    return [
        pilot_id,
        json.dumps(profile.get("topic_counts", {}), separators=(",", ":")),
        profile.get("last_topic", ""),
        json.dumps(profile.get("recent_questions", []), separators=(",", ":")),
        profile.get("preferred_explanation_style", "step-by-step"),
        profile.get("difficulty_level", "standard"),
        profile.get("language_preference", "English"),
        datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    ]


def save_profile(pilot_id: str, profile: dict) -> None:
    """Upsert one pseudonymous learner profile into the private Google Sheet."""
    _cache[pilot_id] = deepcopy(profile)
    ws = _get_profile_worksheet()
    ids = ws.col_values(1)
    row_values = _serialize_row(pilot_id, profile)
    try:
        row_index = ids.index(pilot_id) + 1
    except ValueError:
        ws.append_row(row_values)
    else:
        ws.update(f"A{row_index}:H{row_index}", [row_values])


def update_profile_from_message(pilot_id: str, message: str) -> dict:
    """Update durable learning signals after a learner message."""
    profile = load_profile(pilot_id)
    topic = classify_topic(message)
    counts = profile.setdefault("topic_counts", {})
    counts[topic] = int(counts.get(topic, 0)) + 1
    profile["last_topic"] = topic

    recent = list(profile.get("recent_questions", []))
    recent.append(redact_recent_question(message))
    profile["recent_questions"] = recent[-5:]

    _infer_preferences(profile, message)
    save_profile(pilot_id, profile)
    return deepcopy(profile)


def profile_prompt_context(profile: dict) -> str:
    """Convert stored profile signals into compact tutoring context with minimized PII."""
    counts = profile.get("topic_counts", {})
    frequent = sorted(counts.items(), key=lambda item: item[1], reverse=True)[:3]
    frequent_text = ", ".join(f"{topic} ({count})" for topic, count in frequent) or "none yet"
    recent = profile.get("recent_questions", [])[-3:]
    recent_text = " | ".join(recent) if recent else "none yet"
    return (
        "Learner profile (pseudonymous):\n"
        f"- Preferred explanation style: {profile.get('preferred_explanation_style', 'step-by-step')}\n"
        f"- Difficulty level: {profile.get('difficulty_level', 'standard')}\n"
        f"- Language preference: {profile.get('language_preference', 'English')}\n"
        f"- Last topic: {profile.get('last_topic', '') or 'none yet'}\n"
        f"- Most-practised topics: {frequent_text}\n"
        f"- Recent questions: {recent_text}\n"
        "Use these signals only to adapt teaching style, examples, pacing, and challenge. "
        "Do not claim certainty about mastery from question counts alone."
    )

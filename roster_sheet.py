"""
Dynamic student roster, backed by a "Student Roster" tab in the same
Google Sheet as the interaction log. Replaces the old static roster.json —
a new student is registered automatically the first time they message the
bot, via a one-time "which school are you from?" question, no manual
editing required.
"""

import os
import json
import datetime
import gspread

# Recognized replies -> (canonical school name, Pilot ID prefix)
SCHOOLS = {
    "1": ("Ise Senior High School, Epe", "ISE"),
    "ise": ("Ise Senior High School, Epe", "ISE"),
    "epe": ("Ise Senior High School, Epe", "ISE"),
    "2": ("Tio College, Ikorodu", "TIO"),
    "tio": ("Tio College, Ikorodu", "TIO"),
    "ikorodu": ("Tio College, Ikorodu", "TIO"),
}

ONBOARDING_PROMPT = (
    "Welcome to Robo-Teacher! \U0001F44B Before we start, which school are you from?\n\n"
    "1 \u2014 Ise Senior High School, Epe\n"
    "2 \u2014 Tio College, Ikorodu\n\n"
    "Just reply with 1 or 2."
)
ONBOARDING_RETRY = "Sorry, I didn't quite catch that \U0001F614 Please reply with just 1 or 2."

_ROSTER_HEADER = ["Pilot ID", "School", "WhatsApp Number", "Telegram Username", "Active", "Date Onboarded"]

_client = None
_roster_ws = None
_cache = None       # {(channel, normalized_identifier): {"pilot_id":.., "school":..}}
_next_number = {}   # {prefix: next available int}
_pending = {}        # {(channel, normalized_identifier): True}  awaiting school choice


def _get_client():
    global _client
    if _client is None:
        creds_dict = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
        _client = gspread.service_account_from_dict(creds_dict)
    return _client


def _get_roster_worksheet():
    global _roster_ws
    if _roster_ws is None:
        sh = _get_client().open_by_key(os.environ["GOOGLE_SHEET_ID"])
        try:
            _roster_ws = sh.worksheet("Student Roster")
        except gspread.WorksheetNotFound:
            _roster_ws = sh.add_worksheet(title="Student Roster", rows=300, cols=len(_ROSTER_HEADER))
            _roster_ws.append_row(_ROSTER_HEADER)
    return _roster_ws


def _normalize(channel: str, identifier: str) -> str:
    if channel == "whatsapp":
        return "".join(c for c in identifier if c.isdigit())
    return identifier.lstrip("@").strip().lower()


def _load_cache():
    global _cache, _next_number
    if _cache is not None:
        return
    ws = _get_roster_worksheet()
    _cache = {}
    _next_number = {}
    for row in ws.get_all_records():
        pilot_id = str(row.get("Pilot ID", "")).strip()
        school = str(row.get("School", "")).strip()
        wa = _normalize("whatsapp", str(row.get("WhatsApp Number", "")))
        tg = _normalize("telegram", str(row.get("Telegram Username", "")))
        if wa:
            _cache[("whatsapp", wa)] = {"pilot_id": pilot_id, "school": school}
        if tg:
            _cache[("telegram", tg)] = {"pilot_id": pilot_id, "school": school}
        if pilot_id:
            prefix = "".join(c for c in pilot_id if c.isalpha())
            num = int("".join(c for c in pilot_id if c.isdigit()) or 0)
            _next_number[prefix] = max(_next_number.get(prefix, 0), num + 1)


def lookup_student(channel: str, identifier: str):
    """Returns {'pilot_id':..., 'school':...} if already registered, else None."""
    _load_cache()
    return _cache.get((channel, _normalize(channel, identifier)))


def is_awaiting_school_choice(channel: str, identifier: str) -> bool:
    return _pending.get((channel, _normalize(channel, identifier)), False)


def mark_awaiting_school_choice(channel: str, identifier: str) -> None:
    _pending[(channel, _normalize(channel, identifier))] = True


def parse_school_choice(text: str):
    """Returns (school_name, prefix) if recognized, else None."""
    return SCHOOLS.get(text.strip().lower())


def register_student(channel: str, identifier: str, school: str, prefix: str) -> str:
    """Registers a new student in the Sheet, returns their new Pilot ID."""
    _load_cache()
    n = _next_number.get(prefix, 1)
    pilot_id = f"{prefix}{n:03d}"
    _next_number[prefix] = n + 1

    row = {
        "Pilot ID": pilot_id,
        "School": school,
        "WhatsApp Number": identifier if channel == "whatsapp" else "",
        "Telegram Username": identifier if channel == "telegram" else "",
        "Active": "Yes",
        "Date Onboarded": datetime.datetime.utcnow().isoformat(timespec="seconds"),
    }
    _get_roster_worksheet().append_row([row[h] for h in _ROSTER_HEADER])

    norm = _normalize(channel, identifier)
    _cache[(channel, norm)] = {"pilot_id": pilot_id, "school": school}
    _pending.pop((channel, norm), None)
    return pilot_id

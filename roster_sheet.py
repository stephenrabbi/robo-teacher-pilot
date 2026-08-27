"""
Dynamic student roster backed by the private Google Sheet.

Existing active students remain authorized. New users are only auto-registered
when ALLOW_AUTO_ENROLL is explicitly enabled; the closed-pilot default prevents
unknown users from self-registering.
"""

import os
import json
import datetime
import gspread

SCHOOLS = {
    "1": ("Ise Senior High School, Epe", "ISE"),
    "ise": ("Ise Senior High School, Epe", "ISE"),
    "epe": ("Ise Senior High School, Epe", "ISE"),
    "2": ("Tio College, Ikorodu", "TIO"),
    "tio": ("Tio College, Ikorodu", "TIO"),
    "ikorodu": ("Tio College, Ikorodu", "TIO"),
}

ONBOARDING_PROMPT = (
    "Welcome to Robo-Teacher! 👋 Before we start, which school are you from?\n\n"
    "1 — Ise Senior High School, Epe\n"
    "2 — Tio College, Ikorodu\n\n"
    "Just reply with 1 or 2."
)
ONBOARDING_RETRY = "Sorry, I didn't quite catch that 😔 Please reply with just 1 or 2."
ENROLLMENT_CLOSED_PROMPT = (
    "Robo-Teacher is currently running as a closed school pilot. "
    "Your account is not yet on the approved student roster. "
    "Please contact your teacher to be enrolled before using the tutor."
)

_ROSTER_HEADER = ["Pilot ID", "School", "WhatsApp Number", "Telegram Username", "Active", "Date Onboarded"]

_client = None
_roster_ws = None
_cache = None
_next_number = {}
_pending = {}


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
        active = str(row.get("Active", "Yes")).strip().lower()
        if active not in {"yes", "true", "1", "active"}:
            continue
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
    """Return an active registered participant or None."""
    _load_cache()
    return _cache.get((channel, _normalize(channel, identifier)))


def is_awaiting_school_choice(channel: str, identifier: str) -> bool:
    return _pending.get((channel, _normalize(channel, identifier)), False)


def mark_awaiting_school_choice(channel: str, identifier: str) -> None:
    _pending[(channel, _normalize(channel, identifier))] = True


def parse_school_choice(text: str):
    return SCHOOLS.get(text.strip().lower())


def auto_enrollment_enabled() -> bool:
    """Auto-enrollment is opt-in; the closed-pilot default is safer."""
    return os.getenv("ALLOW_AUTO_ENROLL", "false").strip().lower() in {"1", "true", "yes", "on"}


def register_student(channel: str, identifier: str, school: str, prefix: str) -> str:
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

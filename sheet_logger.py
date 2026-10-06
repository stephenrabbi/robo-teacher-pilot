"""
Logs every tutor interaction to an "Interaction Log" tab in Google Sheets,
so Herbert has human-readable pilot data ready for the grant application
without needing to query a database.

Privacy note: interaction logs use pseudonymous Pilot IDs and now redact
common direct identifiers (email addresses, phone numbers, @handles and URLs)
from stored question/reply excerpts. Messaging identifiers needed for closed
pilot access are maintained separately in the private Student Roster tab.
"""

import os
import json
import datetime
import re
import gspread

_HEADER = ["Timestamp (UTC)", "School", "Pilot ID", "Channel", "Session ID",
           "Question (redacted/truncated)", "Reply (redacted/truncated)", "Interaction Status", "Latency (s)"]

_EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_PHONE_RE = re.compile(r"(?<!\d)(?:\+?234|0)?[789]\d{9}(?!\d)")
_HANDLE_RE = re.compile(r"(?<!\w)@[A-Za-z0-9_]{5,32}\b")
_URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)

def _minimise_text(value: str) -> str:
    """Remove common direct identifiers before storing a short QA excerpt."""
    text = str(value or "")
    text = _EMAIL_RE.sub("[email redacted]", text)
    text = _PHONE_RE.sub("[phone redacted]", text)
    text = _HANDLE_RE.sub("[handle redacted]", text)
    text = _URL_RE.sub("[link redacted]", text)
    return text[:300]

_client = None
_log_ws = None


def _get_client():
    global _client
    if _client is None:
        creds_dict = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
        _client = gspread.service_account_from_dict(creds_dict)
    return _client


def _get_log_worksheet():
    global _log_ws
    if _log_ws is None:
        sh = _get_client().open_by_key(os.environ["GOOGLE_SHEET_ID"])
        try:
            _log_ws = sh.worksheet("Interaction Log")
        except gspread.WorksheetNotFound:
            _log_ws = sh.add_worksheet(title="Interaction Log", rows=1000, cols=len(_HEADER))
            _log_ws.append_row(_HEADER)
    return _log_ws


def log_interaction(pilot_id: str, school: str, channel: str, session_id: str,
                     question: str, reply: str, latency: float, status: str = "Success") -> None:
    """Best-effort logging -- must never crash the bot if the sheet is unreachable."""
    try:
        sheet = _get_log_worksheet()
        sheet.append_row([
            datetime.datetime.utcnow().isoformat(timespec="seconds"),
            school,
            pilot_id,
            channel,
            session_id,
            _minimise_text(question),
            _minimise_text(reply),
            status,
            round(latency, 2),
        ])
    except Exception as e:
        print(f"[sheet_logger] WARNING: failed to log interaction: {e}")

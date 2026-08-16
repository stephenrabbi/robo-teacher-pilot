"""
Logs every tutor interaction to an "Interaction Log" tab in Google Sheets,
so Herbert has human-readable pilot data ready for the grant application
without needing to query a database.

Privacy note: no phone number, Telegram username, or student name is
stored here at all -- only the anonymous Pilot ID assigned during
onboarding (see roster_sheet.py). The mapping from Pilot ID back to a
real student lives only in the separate Student Roster tab.
"""

import os
import json
import datetime
import gspread

_HEADER = ["Timestamp (UTC)", "School", "Pilot ID", "Channel", "Session ID",
           "Question", "Reply (truncated)", "Interaction Status", "Latency (s)"]

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
            question[:500],
            reply[:500],
            status,
            round(latency, 2),
        ])
    except Exception as e:
        print(f"[sheet_logger] WARNING: failed to log interaction: {e}")

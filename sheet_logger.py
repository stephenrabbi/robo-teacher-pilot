"""
Logs every tutor interaction to a Google Sheet, so Herbert has
human-readable pilot data ready for the grant application without
needing to query a database.

Setup required (see README.md):
1. Create a Google Cloud project, enable the Google Sheets API.
2. Create a Service Account, download its JSON key.
3. Create a Google Sheet, share it with the service account's email
   (found inside the JSON key file) as an Editor.
4. Put the Sheet's ID (from its URL) in GOOGLE_SHEET_ID.
5. Put the full JSON key contents (as one line) in GOOGLE_SERVICE_ACCOUNT_JSON.

Privacy note: we deliberately log only the LAST 4 DIGITS of the
student's WhatsApp number, not the full number, since these are minors.
That's enough to spot repeat usage without storing identifying contact
details in a spreadsheet several people may see.
"""

import os
import json
import datetime
import gspread

_HEADER = ["Timestamp (UTC)", "School", "Student Ref", "Question", "Reply (truncated)", "Latency (s)"]

_sheet = None


def _get_sheet():
    global _sheet
    if _sheet is None:
        creds_dict = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
        gc = gspread.service_account_from_dict(creds_dict)
        sh = gc.open_by_key(os.environ["GOOGLE_SHEET_ID"])
        _sheet = sh.sheet1
        if not _sheet.acell("A1").value:
            _sheet.append_row(_HEADER)
    return _sheet


def mask_number(whatsapp_number: str) -> str:
    digits = "".join(c for c in whatsapp_number if c.isdigit())
    return f"***{digits[-4:]}" if len(digits) >= 4 else "***"


def log_interaction(student_id: str, school: str, question: str, reply: str, latency: float) -> None:
    """Best-effort logging — must never crash the bot if the sheet is unreachable."""
    try:
        sheet = _get_sheet()
        sheet.append_row([
            datetime.datetime.utcnow().isoformat(timespec="seconds"),
            school,
            mask_number(student_id),
            question[:500],
            reply[:500],
            round(latency, 2),
        ])
    except Exception as e:
        print(f"[sheet_logger] WARNING: failed to log interaction: {e}")

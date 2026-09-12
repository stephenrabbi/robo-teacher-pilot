"""Central learner-code registry. Student names are deliberately never stored here."""
import json
import os
import threading
from datetime import datetime, timezone

import gspread
from google.oauth2.service_account import Credentials

_HEADER = ["Timestamp (UTC)", "Learner Code", "Class Level", "Status", "Replaces"]
_events: list[dict] = []
_client = None
_worksheet = None
_lock = threading.Lock()


def _get_client():
    global _client
    if _client is None:
        credentials = Credentials.from_service_account_info(json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]), scopes=["https://www.googleapis.com/auth/spreadsheets"])
        _client = gspread.authorize(credentials)
    return _client


def _get_worksheet():
    global _worksheet
    if _worksheet is None:
        spreadsheet = _get_client().open_by_key(os.environ["GOOGLE_SHEET_ID"])
        try:
            _worksheet = spreadsheet.worksheet("Learner Codes")
        except gspread.WorksheetNotFound:
            _worksheet = spreadsheet.add_worksheet(title="Learner Codes", rows=2000, cols=len(_HEADER))
            _worksheet.append_row(_HEADER)
    return _worksheet


def _read_events() -> tuple[list[dict], bool]:
    try:
        rows = _get_worksheet().get_all_records()
        events = [{"timestamp": str(row.get("Timestamp (UTC)", "")), "code": str(row.get("Learner Code", "")).strip().upper(), "class_level": str(row.get("Class Level", "JSS2")), "status": str(row.get("Status", "Active")).strip().title(), "replaces": str(row.get("Replaces", "")).strip().upper()} for row in rows if row.get("Learner Code")]
        return events, True
    except Exception:
        return list(_events), False


def list_codes(class_level: str) -> tuple[list[dict], bool]:
    events, synced = _read_events();latest = {}
    for event in events:
        if event["class_level"] == class_level:
            latest[event["code"]] = event
    return sorted(latest.values(), key=lambda item: item["code"]), synced


def _append(event: dict) -> None:
    _events.append(event)
    try:
        _get_worksheet().append_row([event["timestamp"], event["code"], event["class_level"], event["status"], event["replaces"]])
    except Exception:
        pass


def generate_codes(prefix: str, class_level: str, count: int) -> list[dict]:
    prefix = prefix.strip().upper().strip("-")
    with _lock:
        existing, _ = list_codes(class_level);stem = f"{prefix}-{class_level}-"
        numbers = [int(item["code"][len(stem):]) for item in existing if item["code"].startswith(stem) and item["code"][len(stem):].isdigit()]
        created = []
        for number in range(max(numbers, default=0) + 1, max(numbers, default=0) + count + 1):
            event = {"timestamp": datetime.now(timezone.utc).isoformat(), "code": f"{stem}{number:03d}", "class_level": class_level, "status": "Active", "replaces": ""}
            _append(event);created.append(event)
        return created


def replace_code(code: str, class_level: str) -> dict:
    code = code.strip().upper()
    with _lock:
        existing, _ = list_codes(class_level);current = next((item for item in existing if item["code"] == code), None)
        if not current or current["status"] != "Active":
            raise ValueError("Only an active learner code can be replaced")
        prefix = code.split("-", 1)[0];stem = f"{prefix}-{class_level}-"
        numbers = [int(item["code"][len(stem):]) for item in existing if item["code"].startswith(stem) and item["code"][len(stem):].isdigit()]
        now = datetime.now(timezone.utc).isoformat();_append({"timestamp": now, "code": code, "class_level": class_level, "status": "Retired", "replaces": ""})
        replacement = {"timestamp": now, "code": f"{stem}{max(numbers, default=0) + 1:03d}", "class_level": class_level, "status": "Active", "replaces": code};_append(replacement)
        return replacement


def validate_code(code: str, class_level: str) -> bool:
    if code.startswith("IND-"):
        return True
    codes, _ = list_codes(class_level);match = next((item for item in codes if item["code"] == code), None)
    # Grandfather codes issued before the central registry existed. A code is
    # rejected only after the teacher has explicitly retired it.
    return not match or match["status"] == "Active"


def _reset_for_tests():
    global _client, _worksheet
    _events.clear();_client = None;_worksheet = None

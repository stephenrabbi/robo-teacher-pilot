"""Identity-minimised evidence for adaptive reteaching strategies."""

import datetime
import json
import os
import secrets
import threading

import gspread


_HEADER = ["Timestamp (UTC)", "Event ID", "Learner ID", "Class Level", "Teaching Strategy", "Next Check Correct"]
_STRATEGIES = {"familiar_example", "concrete_objects", "guided_questions"}
_client = None
_worksheet = None
_memory_records: list[dict] = []
_lock = threading.Lock()


def _sheet_configured() -> bool:
    return bool(os.getenv("GOOGLE_SHEET_ID") and os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"))


def _get_worksheet():
    global _client, _worksheet
    if _worksheet is None:
        if _client is None:
            credentials = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
            _client = gspread.service_account_from_dict(credentials)
        spreadsheet = _client.open_by_key(os.environ["GOOGLE_SHEET_ID"])
        try:
            _worksheet = spreadsheet.worksheet("Strategy Evidence")
        except gspread.WorksheetNotFound:
            _worksheet = spreadsheet.add_worksheet(title="Strategy Evidence", rows=2000, cols=len(_HEADER))
            _worksheet.append_row(_HEADER)
    return _worksheet


def save_strategy_outcome(learner_id: str, class_level: str, strategy: str, correct: bool) -> bool:
    """Save one anonymous strategy/outcome pair; never store lesson or answer text."""
    if strategy not in _STRATEGIES or type(correct) is not bool:
        return False
    record = {
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),
        "event_id": secrets.token_hex(8),
        "learner_id": learner_id,
        "class_level": class_level,
        "strategy": strategy,
        "correct": correct,
    }
    with _lock:
        _memory_records.append(record)
    if not _sheet_configured():
        return False
    try:
        _get_worksheet().append_row([
            record["timestamp"], record["event_id"], learner_id, class_level, strategy, correct,
        ])
        return True
    except Exception as exc:
        print(f"[strategy_evidence] WARNING: failed to save outcome: {type(exc).__name__}")
        return False


def _reset_for_tests() -> None:
    global _client, _worksheet
    with _lock:
        _memory_records.clear()
    _client = None
    _worksheet = None

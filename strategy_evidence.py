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


def _as_bool(value) -> bool | None:
    if type(value) is bool:
        return value
    normalized = str(value).strip().lower()
    if normalized in {"true", "yes", "1"}:
        return True
    if normalized in {"false", "no", "0"}:
        return False
    return None


def _sheet_records() -> list[dict]:
    records = []
    for row in _get_worksheet().get_all_records():
        correct = _as_bool(row.get("Next Check Correct"))
        strategy = str(row.get("Teaching Strategy", ""))
        if strategy not in _STRATEGIES or correct is None:
            continue
        records.append({
            "event_id": str(row.get("Event ID", "")),
            "class_level": str(row.get("Class Level", "")),
            "strategy": strategy,
            "correct": correct,
        })
    return records


def build_strategy_summary(class_level: str) -> dict:
    """Aggregate anonymous outcomes without exposing learner-level records."""
    synced = False
    records = []
    if _sheet_configured():
        try:
            records = _sheet_records()
            synced = True
        except Exception as exc:
            print(f"[strategy_evidence] WARNING: failed to load outcomes: {type(exc).__name__}")
    known_ids = {item.get("event_id") for item in records if item.get("event_id")}
    with _lock:
        records.extend(item.copy() for item in _memory_records if item.get("event_id") not in known_ids)
    labels = {
        "familiar_example": "Familiar examples",
        "concrete_objects": "Concrete objects",
        "guided_questions": "Guided questions",
    }
    items = []
    for strategy, label in labels.items():
        matches = [item for item in records if item.get("class_level") == class_level and item.get("strategy") == strategy]
        correct = sum(item.get("correct") is True for item in matches)
        attempts = len(matches)
        items.append({
            "strategy": strategy,
            "label": label,
            "attempts": attempts,
            "correct": correct,
            "success_rate": round(correct / attempts * 100) if attempts else None,
        })
    total = sum(item["attempts"] for item in items)
    return {
        "items": items,
        "total_attempts": total,
        "sufficient_evidence": total >= 15 and all(item["attempts"] >= 5 for item in items),
        "storage_synced": synced,
    }
def _reset_for_tests() -> None:
    global _client, _worksheet
    with _lock:
        _memory_records.clear()
    _client = None
    _worksheet = None

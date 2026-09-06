"""Separate durable storage for privacy-safe diagnostic placement results."""

import datetime, json, os, threading
import gspread

_HEADER=["Timestamp (UTC)","Session ID","Learner ID","Class Level","Term","Score","Questions","Percentage","Recommended Topic","Recommended Difficulty","Topic Results JSON"]
_worksheet=None
_memory=[]
_lock=threading.Lock()

def _configured(): return bool(os.getenv("GOOGLE_SHEET_ID") and os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON"))

def _sheet():
    global _worksheet
    if _worksheet is None:
        client=gspread.service_account_from_dict(json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]));book=client.open_by_key(os.environ["GOOGLE_SHEET_ID"])
        try: _worksheet=book.worksheet("Diagnostic Results")
        except gspread.WorksheetNotFound:
            _worksheet=book.add_worksheet(title="Diagnostic Results",rows=1000,cols=len(_HEADER));_worksheet.append_row(_HEADER)
    return _worksheet

def save_diagnostic_result(learner_id: str, summary: dict) -> bool:
    record={"timestamp":datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds"),"session_id":summary["session_id"],"learner_id":learner_id,"class_level":summary["class_level"],"term":summary["term"],"score":summary["score"],"attempted":summary["attempted"],"percentage":summary["percentage"],"recommended_topic":summary["recommended_topic"],"recommended_difficulty":summary["recommended_difficulty"],"topic_results":summary["topic_results"]}
    with _lock:
        if not any(item["session_id"]==record["session_id"] for item in _memory): _memory.append(record)
    if not _configured(): return False
    try:
        _sheet().append_row([record["timestamp"],record["session_id"],learner_id,record["class_level"],record["term"],record["score"],record["attempted"],record["percentage"],record["recommended_topic"],record["recommended_difficulty"],json.dumps(record["topic_results"],ensure_ascii=False)])
        return True
    except Exception as exc:
        print(f"[diagnostic_progress] WARNING: failed to save result: {type(exc).__name__}");return False

def latest_diagnostic(learner_id: str, class_level: str):
    records=[]
    if _configured():
        try:
            for row in _sheet().get_all_records():
                if str(row.get("Learner ID"))==learner_id and str(row.get("Class Level"))==class_level:
                    records.append({"timestamp":str(row.get("Timestamp (UTC)","")),"session_id":str(row.get("Session ID","")),"class_level":class_level,"term":str(row.get("Term","")),"score":int(row.get("Score",0)),"attempted":int(row.get("Questions",0)),"percentage":int(row.get("Percentage",0)),"recommended_topic":str(row.get("Recommended Topic","")),"recommended_difficulty":str(row.get("Recommended Difficulty","Easy")),"topic_results":json.loads(str(row.get("Topic Results JSON","[]")))})
        except Exception as exc: print(f"[diagnostic_progress] WARNING: failed to load results: {type(exc).__name__}")
    with _lock:
        known={item["session_id"] for item in records};records.extend(item.copy() for item in _memory if item["learner_id"]==learner_id and item["class_level"]==class_level and item["session_id"] not in known)
    if not records: return None
    latest=max(records,key=lambda item:item["timestamp"]).copy();latest.pop("learner_id",None)
    return latest


def diagnostic_class_summary(class_level: str) -> dict:
    """Return class aggregates only; learner identifiers never leave this function."""
    records=[]
    if _configured():
        try:
            for row in _sheet().get_all_records():
                if str(row.get("Class Level"))==class_level:
                    records.append({"session_id":str(row.get("Session ID","")),"learner_id":str(row.get("Learner ID","")),"term":str(row.get("Term","")),"percentage":int(row.get("Percentage",0)),"recommended_topic":str(row.get("Recommended Topic",""))})
        except Exception as exc:
            print(f"[diagnostic_progress] WARNING: failed to load class results: {type(exc).__name__}")
    known={item["session_id"] for item in records}
    with _lock:
        records.extend({key:item[key] for key in ("session_id","learner_id","term","percentage","recommended_topic")} for item in _memory if item["class_level"]==class_level and item["session_id"] not in known)
    topic_counts={topic:sum(item["recommended_topic"]==topic for item in records) for topic in {item["recommended_topic"] for item in records if item["recommended_topic"]}}
    common=max(topic_counts,key=lambda topic:(topic_counts[topic],topic)) if topic_counts else None
    terms=[]
    for term in ("First Term","Second Term","Third Term"):
        items=[item for item in records if item["term"]==term]
        if items: terms.append({"term":term,"completed":len(items),"average_percentage":round(sum(item["percentage"] for item in items)/len(items))})
    return {"completed":len(records),"learners":len({item["learner_id"] for item in records}),"average_percentage":round(sum(item["percentage"] for item in records)/len(records)) if records else 0,"common_focus_topic":common,"terms":terms}

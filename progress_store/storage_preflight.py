"""Fail-closed preflight for the isolated SQLite prototype schema.

Does not migrate or open production data. Use only on a disposable synthetic
database. Production managed storage needs separate design and review.
"""
import sqlite3

EXPECTED = {
    "synthetic_enrollments": {"school","subject","reviewer_id","approved_at","session_epoch"},
    "synthetic_recovery": {"school","subject","challenge_hash","expires_at"},
    "synthetic_recovery_attempts": {"school","subject","failures","locked_until"},
    "synthetic_login_credentials": {"school","subject","salt","verifier"},
    "synthetic_login_attempts": {"school","subject","failures","locked_until"},
    "redeemed_approvals": {"provider_id","decision_id","kind","school","subject"},
    "learner_events": {"school","subject","event_id","event_type","class_level","topic_key","correct_count","total_count","occurred_at"},
}

def check_synthetic_schema(db):
    if not isinstance(db,sqlite3.Connection):
        raise TypeError("SQLite test connection required")
    errors=[]
    for table,expected in EXPECTED.items():
        columns={row[1] for row in db.execute("PRAGMA table_info("+table+")")}
        if columns!=expected:
            errors.append(table+": missing="+",".join(sorted(expected-columns))+" unexpected="+",".join(sorted(columns-expected)))
    violations=db.execute("PRAGMA foreign_key_check").fetchall()
    if violations:
        errors.append("foreign key violations: "+str(len(violations)))
    if errors:
        raise RuntimeError("Synthetic storage schema is not ready: "+"; ".join(errors))
    return True

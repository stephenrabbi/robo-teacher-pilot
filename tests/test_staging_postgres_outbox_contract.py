"""Static staging schema checks (no database connection or student data)."""
from pathlib import Path

SCHEMA = (Path(__file__).resolve().parents[1] / "staging/progress_outbox_postgres.sql").read_text()

def test_postgres_outbox_idempotency_and_json_constraints():
    assert "event_id text PRIMARY KEY" in SCHEMA
    assert "payload jsonb NOT NULL" in SCHEMA
    assert "jsonb_typeof(payload)='object'" in SCHEMA

def test_postgres_claim_pattern_prevents_parallel_double_claim():
    assert "FOR UPDATE SKIP LOCKED" in SCHEMA
    assert "status='leased'" in SCHEMA
    assert "lease_until" in SCHEMA
    assert "next_attempt_at" in SCHEMA

def test_schema_is_staging_only_and_does_not_expose_credentials():
    assert "Staging-only" in SCHEMA
    assert "DATABASE_URL=" not in SCHEMA
    assert "CREATE TABLE IF NOT EXISTS" in SCHEMA

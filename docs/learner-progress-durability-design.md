# Robo-Teacher learner-progress durability — staged implementation design

Issue: #167. This document describes a proposed design, not deployed functionality.

## Confirmed current behavior
- `practice_progress.py` stores Practice results in Google Sheets and falls back to process-local `_memory_records` when Sheets is unavailable.
- `diagnostic_progress.py` also has a process-local fallback.
- `classroom_api.py` schedules the practice write as a FastAPI background task. `progress_saving: true` indicates scheduling, not a completed durable write.
- In-memory-only progress may disappear on process restart. A successful UI display does not prove persistence.

## Proposed safe architecture
1. Keep Google Sheets as the existing reporting destination until migration has been validated.
2. Add an independently durable Postgres **outbox** for completed synthetic or learner practice/diagnostic events. A *confirmed outbox transaction* becomes the definition of `queued`, and a confirmed Sheets write becomes `synced`.
3. The outbox table should have `event_id`/practice session ID as a unique key, pseudonymous owner ID, event type, minimal validated payload, status, attempts, `next_attempt_at`, and created/updated timestamps. Retain the minimum required data.
4. An authorized worker leases pending events and retries Google Sheets delivery with bounded exponential backoff and jitter. Avoid permanent replay loops. After a max attempt threshold, mark for operator review.
5. Google Sheets lacks an atomic idempotent append. Protect against duplicate sheet rows on worker crash by querying for the session ID before append; reconcile duplicates if needed. This is *at-least-once* delivery with best-effort dedupe, **not** exactly-once.
6. Expose status to the learner as `saved` (durable outbox acknowledged), `syncing` (queued for Sheets), `synced` (confirmed in Sheets), or `failed` (neither durable location saved). Never show `saved` merely because background processing started.
7. Require authenticated ownership for polling status. Do not expose raw records or private teacher access values in observability.
8. Add least-privilege storage credentials and a rollback flag. Do not switch on the new write path until staging simulations pass.

## Validation gates
- Synthetic-only tests for Sheets unavailable, outbox unavailable, repeated delivery, restart between enqueue and delivery, concurrent workers, and unauthorized owner status lookup.
- Confirm staging Postgres persistence through a controlled app restart.
- Measure pending queue age, failed items and delivery lag; exercise an operator-run dead-letter recovery procedure.
- Verify Google Sheets export and restore using a **separate test workbook**; never mutate or reset live school data.
- Check intended RPO and RTO with the school operator before making recovery commitments.

## Deployment boundary
All implementation changes stay in a draft branch and a staging database. Production remains at its current verified release until staging tests, credentials review and rollout plan are approved.

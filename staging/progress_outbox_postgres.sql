-- Staging-only PostgreSQL outbox schema. Do NOT apply to production without review.
-- Queue contains pseudonymous identifiers and strictly limited progress payloads.
CREATE TABLE IF NOT EXISTS progress_outbox (
 event_id text PRIMARY KEY,
 learner_id text NOT NULL,
 event_type text NOT NULL CHECK (event_type IN ('practice','diagnostic')),
 payload jsonb NOT NULL CHECK (jsonb_typeof(payload)='object'),
 status text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','leased','synced','failed')),
 attempts integer NOT NULL DEFAULT 0 CHECK (attempts >= 0),
 next_attempt_at timestamptz NOT NULL DEFAULT now(),
 lease_until timestamptz,
 created_at timestamptz NOT NULL DEFAULT now(),
 updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS progress_outbox_due_idx
 ON progress_outbox(next_attempt_at, created_at)
 WHERE status='pending';
-- Atomic claim. Execute in one transaction; SKIP LOCKED prevents double claim.
-- Worker must check Sheets for event_id before appending to mitigate ambiguous delivery.
-- UPDATE progress_outbox SET status='leased', lease_until=now()+interval '2 minutes',updated_at=now()
-- WHERE event_id IN (
--   SELECT event_id FROM progress_outbox
--   WHERE status='pending' AND next_attempt_at<=now()
--   ORDER BY next_attempt_at,created_at LIMIT 25 FOR UPDATE SKIP LOCKED
-- ) RETURNING event_id,learner_id,event_type,payload,attempts;
-- Recover expired leases before retry:
-- UPDATE progress_outbox SET status='pending', lease_until=NULL
-- WHERE status='leased' AND lease_until<now();
-- Security requirement: application/worker role must be least privilege;
-- database credentials and row status endpoints must not be publicly exposed.

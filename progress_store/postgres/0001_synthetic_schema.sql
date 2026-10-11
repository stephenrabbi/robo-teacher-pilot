-- Synthetic-only PostgreSQL v0001. Never apply to a real learner database.
BEGIN;
CREATE SCHEMA IF NOT EXISTS rt_synthetic;
CREATE TABLE rt_synthetic.enrollments (
 school text NOT NULL, subject text NOT NULL, reviewer_id text NOT NULL,
 approved_at bigint NOT NULL, session_epoch bigint NOT NULL DEFAULT 0 CHECK (session_epoch >= 0),
 PRIMARY KEY (school,subject)
);
CREATE TABLE rt_synthetic.events (
 school text NOT NULL, subject text NOT NULL, event_id uuid NOT NULL,
 event_type text NOT NULL CHECK(event_type IN ('practice_completed','diagnostic_completed','revision_completed')),
 class_level text NOT NULL CHECK(class_level IN ('JSS1','JSS2','JSS3')),
 topic_key text NOT NULL, correct_count integer NOT NULL, total_count integer NOT NULL,
 occurred_at timestamptz NOT NULL,
 CHECK (correct_count >= 0 AND correct_count <= total_count AND total_count <= 100),
 PRIMARY KEY(school,subject,event_id),
 FOREIGN KEY(school,subject) REFERENCES rt_synthetic.enrollments(school,subject)
);
CREATE INDEX events_scoped_history ON rt_synthetic.events(school,subject,occurred_at,event_id);
CREATE TABLE rt_synthetic.redeemed_approvals (
 provider_id text NOT NULL, decision_id text NOT NULL,
 kind text NOT NULL CHECK(kind IN ('enrollment','recovery')),
 school text NOT NULL, subject text NOT NULL,
 PRIMARY KEY(provider_id,decision_id)
);
CREATE TABLE rt_synthetic.login_credentials (
 school text NOT NULL, subject text NOT NULL, salt bytea NOT NULL, verifier bytea NOT NULL,
 PRIMARY KEY(school,subject),
 FOREIGN KEY(school,subject) REFERENCES rt_synthetic.enrollments(school,subject)
);
CREATE TABLE rt_synthetic.login_attempts (
 school text NOT NULL, subject text NOT NULL,
 failures integer NOT NULL DEFAULT 0 CHECK(failures >= 0),
 locked_until bigint NOT NULL DEFAULT 0,
 PRIMARY KEY(school,subject)
);
CREATE TABLE rt_synthetic.recovery (
 school text NOT NULL, subject text NOT NULL, challenge_hash bytea NOT NULL,
 expires_at bigint NOT NULL,
 PRIMARY KEY(school,subject),
 FOREIGN KEY(school,subject) REFERENCES rt_synthetic.enrollments(school,subject)
);
CREATE TABLE rt_synthetic.recovery_attempts (
 school text NOT NULL, subject text NOT NULL,
 failures integer NOT NULL DEFAULT 0 CHECK(failures >= 0),
 locked_until bigint NOT NULL DEFAULT 0,
 PRIMARY KEY(school,subject)
);
COMMIT;

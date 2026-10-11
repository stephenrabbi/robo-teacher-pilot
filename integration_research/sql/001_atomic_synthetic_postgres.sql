-- Synthetic-only PostgreSQL transaction foundation. Not deployed.
-- The caller MUST independently authenticate and verify approvals; this SQL does not.
CREATE SCHEMA IF NOT EXISTS synthetic_identity_lab;
CREATE TABLE IF NOT EXISTS synthetic_identity_lab.approval_redemptions (
    approval_fingerprint CHAR(64) PRIMARY KEY,
    school_ref TEXT NOT NULL,
    learner_ref TEXT NOT NULL,
    redeemed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CHECK (length(school_ref) > 0 AND length(learner_ref) > 0)
);
CREATE TABLE IF NOT EXISTS synthetic_identity_lab.learner_activations (
    school_ref TEXT NOT NULL,
    learner_ref TEXT NOT NULL,
    approval_fingerprint CHAR(64) NOT NULL UNIQUE
        REFERENCES synthetic_identity_lab.approval_redemptions(approval_fingerprint),
    activated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (school_ref, learner_ref)
);
-- Deploy only to a disposable, access-restricted development database.
-- Execute both INSERT statements in one transaction; never use AUTOCOMMIT.

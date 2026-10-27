# Learner identity release decision — 11 October 2026

**NO-GO: Do not merge or deploy PR #92 as live learner identity.**

Verified:
- Existing Render production service `srv-d9ugo2lbedkc73a5rk6g` deploys `main` automatically and is public (`0.0.0.0/0`).
- Render workspace `tea-d9ugf1u1egvs73ef17f0` currently lists **no PostgreSQL instances**.
- GitHub Actions disposable PostgreSQL 16 synthetic integration tests have passed. This is not a durable live database.
- PR #92 test verifier is caller-injected and has no authenticated school or guardian identity source.
- CI does not prove verified individualized institutional/guardian approval, safeguarding signoff, rollback rehearsal or a protected deployment.

Required before live account rollout:
1. Configure real authenticated institutional and guardian approval with independently confirmed authority and privacy/safeguarding approval; never treat prior synthetic-planning signoff as consent for named pupils.
2. Provision and configure a managed PostgreSQL instance for the future production service, with least-privilege credentials, network restrictions, encryption, backup/restore test, migration and retention/deletion controls.
3. Use a restricted staging deployment, exercise actual authentication, recovery, browser device-switch/logout and concurrent-account tests; obtain independent review.
4. Rehearse rollback and verify no loss/cross-account exposure. Record exact approved deployed Git SHA. Enable identity only behind a default-off feature flag.

Until then: keep PRs #85, #91, #92 draft/unmerged and the production application unchanged. The code preflight in `integration_research/release_preflight.py` rejects absent release-approval assertions but cannot authenticate them; its passing with environment variables is **not** independently verified approval.

# Synthetic progress storage — managed database migration gate

**Status:** Design only. PR #85 is isolated and must not be merged or connected to actual learner records.

## Target architecture
- Select a managed transactional relational database (PostgreSQL is a candidate; no provider selected). Maintain immutable per-school and pseudonymous per-learner scoped event identifiers.
- Enforce a unique (school, subject, event_id) constraint for idempotency and immutable event payload conflict rejection.
- Store enrollment, revocation epoch, recovery challenge digest, one-use provider approvals, login verifier and throttling data server-side. Never persist raw recovery secrets or passwords.
- Authenticate first; use one transaction for revocation-epoch verification and event insertion, ensuring the concurrent recovery operation uses compatible locking/serialization semantics.
- Distinct database roles for migrations and runtime, encrypted connections and provider-managed encrypted backups, controlled secret rotation and audited administrator access.
- Define retention, deletion and export workflows and documented school/guardian authorization before any children's data is migrated.

## Explicit migration gates
1. Inventory every schema and public route; choose managed DB/provider after establishing backup, disaster recovery and regional/privacy requirements.
2. Write additive/versioned migrations, forward and rollback procedures, deterministic seeds using **synthetic identifiers only**, and an ownership/access model.
3. Execute dry-run against a disposable instance; verify indexes, uniqueness, foreign keys, scoped access, revocation, transaction isolation, and multi-worker load.
4. Test backup/restore and deletion with outcome evidence. Prove rollback without losing acknowledged events.
5. Conduct authenticated staging UX tests on mobile/shared devices, and an independent security and child-data governance review.
6. Permit a separate reviewed integration PR only after sign-off. Keep feature flag disabled by default and never migrate existing pupil spreadsheets casually.

## Current limited automated check
`progress_store/storage_preflight.py` inspects the existing SQLite synthetic tables and rejects missing columns or foreign-key violations without creating or migrating records. It is **not** a managed-database migration, backup test, vulnerability scan or release authorization.

## Known design hazard
The current isolated API assumes enrollment and events share the exact same SQLite connection to guarantee serialized revocation and writes. Changing to a managed DB requires revisiting transaction boundaries, pooled connections, lock granularity and isolation levels. Do not carry the connection-identity check over as a substitute for database correctness.

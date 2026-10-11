# Synthetic progress API — staging-only launch gate

The prototype in `progress_store/synthetic_api.py` is **not attached** to `main.py`, `v25_app.py`, or any Render service. Do not set `enabled=True` in a public application or ship the example signing keys.

## Prerequisites for a protected non-public test environment

1. Verify green CI for storage, session, identity, recovery, boundary, learner journey, and API tests.
2. Provision an isolated disposable test database, with no connections or imports from existing pupil Google Sheets.
3. Configure a separate private test deployment with authentication at the perimeter and access restricted to the development team. A publicly accessible Render URL is **not** by itself a safe private environment.
4. Store secrets in a managed secret store. Rotate on exposure; never put keys in GitHub, client JavaScript, URL parameters, or logs.
5. Use synthetic identities and records only. The example `TestIdentityAuthority` and `VerifiedEnrollmentGateway` do not validate real parental or school authorization.
6. Disable the application by default. Supply an explicit isolated database and secret to the application factory only in the protected test process.
7. Test invalid token, missing token, altered owner field, other-school access, idempotency, database restart, token expiration, and recovery approval.
8. Do not expose a token-issuance endpoint or permit arbitrary client-provided subject/school values. Decide the real credential/guardian recovery provider separately.
9. Record run metadata and rollback instructions but no learner text, credentials, or personal identifiers.
10. Do not connect the production classroom, enable migrations, or write actual pupil records until security and school permissions are independently reviewed.

## Current scope

Prototype SQLite is suitable for a single-process synthetic demonstration only. It is not the final managed database design. SQLite connections configured with `check_same_thread=False` for tests are not a production concurrency or durability guarantee. The in-memory identity approver is not a source of trustworthy real-world approvals.

## Promotion conditions

Require passing API validation, independently verified actual authentication, account recovery and consent policy, persistent managed storage with backups, cross-device sync conflict handling, staging mobile/browser checks, and a documented rollback. Keep feature flag disabled by default.

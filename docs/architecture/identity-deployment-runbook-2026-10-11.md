# Identity deployment runbook — 11 October 2026

**Current decision: NO-GO for real learner identity and persistent progress in live production.**

## Provisioned synthetic infrastructure
- Render PostgreSQL: `dpg-db5s7acs728c738s84eg-a`, `robo-teacher-identity-synthetic-staging`, Frankfurt, PostgreSQL 16.
- Free plan; **expires 10 November 2026**. No HA; not an operational production database.
- Status at creation: `creating`. Recheck before any integration and do not copy connection strings into GitHub.
- Do not put names, phone numbers, consent records, learner passwords, real sessions, or actual student progress in this staging database.
- The CI PostgreSQL integration already runs against disposable PostgreSQL 16; that success does not verify this new Render database's access configuration or backup/restore support.

## Institutional authorization — independently required
The school-approved eight-item process was expressly for *further planning and synthetic testing only*. The user's project-owner authorization cannot serve as school approval, a guardian's permission, or a reviewer credential.
1. Obtain verifiable school authorization identifying the responsible official, institution, authorized learners and deployment scope.
2. Confirm which guardian notices/permissions and age-appropriate learner assent apply, and record the approved workflow without exposing sensitive data.
3. Assign independently authenticated reviewer/operator accounts and revocation responsibility through an actual provider. Test onboarding, removal, recovery and audit trails.
4. Document safeguarding contacts, complaint handling, breach response, retention and deletion and obtain the required institutional/privacy sign-offs.

## Production technical gates
1. Deploy to a **restricted staging environment** with real access control; the available Render web-service creation connector only provisions public-facing services and cannot itself establish restricted staging. Do not use its public endpoint for identities.
2. Migrate to a suitable persistent *production* PostgreSQL plan with role-scoped credentials, encryption, backups and a tested restore procedure; do not rely on expiring free database.
3. Run end-to-end cross-school, shared-device, consent revocation, concurrent redemption, logout/session revocation and recovery tests. Disable account issuance until all pass.
4. Independently review the release and sign off; preserve an exact rollback SHA, release/feature flags default OFF and monitor failure rates after deployment.

## Automated evidence
- `tests/test_real_postgres_atomic.py`: actual disposable PostgreSQL transactions under CI.
- `integration_research/release_preflight.py`: fail-closed configuration assertion checklist; assertions are **not independent evidence**.
- `docs/architecture/identity-release-no-go-2026-10-11.md`: release findings.

### Release decision
Do **not** merge PRs #85, #91 or #92 wholesale. Keep public Robo-Teacher running its established routes without learner identity activation. Reassess only after evidence is independently confirmed and protected staging tests pass.

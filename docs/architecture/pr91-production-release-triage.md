# PR #91 release decision — security triage

**Decision: BLOCKED for production integration.** Review based on PR #91 source diff and successful CI #650 (11 October 2026). The school's reported approval authorizes further planning and synthetic testing, **not** public activation with real learner records. This is a repository review, not a penetration test.

## What the branch actually contains
- `integration_research/`: synthetic enrollment decisions, operator/reviewer HMAC role fixtures, disposable SQLite credential hashing and recovery, single-use test assertion tracker, disabled-by-default HTTP health route.
- `tests/`: isolated authorization journey and preflight tests.
- `README.md` and planning documents.
- Neither live `main.py` nor `v25_app.py` has been changed or wired to new login/progress routes.
- Render production deploys `main` on each commit. **Do not merge PR #91 wholesale:** merging this entire draft would promote experimental research source and test code to production even though endpoints are not mounted.

## Material release blockers
| Priority | Blocker | Minimum closeout proof |
|---|---|---|
| P0 | `ProvisioningDecision.allowed` and `SyntheticDecision.approved` are caller-created Python dataclass values; they do not prove actual independently verified school/guardian authorization. | Production trust-provider adapters, signed/verified decision provenance, revocation/expiry and negative tampering tests. |
| P0 | HMAC synthetic operator assertions are created by `issue_synthetic_role`; test keys and allowlists do not identify authorized real officials. | Independent authenticated operator/reviewer provider, operator onboarding/offboarding and auditing, production secret handling. |
| P0 | The replay guard is *opt-in* and is not a single transaction with credential creation; test assertions may be consumed on later failing operations. | Atomic authorization+redemption+account mutation with properly scoped DB transactions and concurrent/restart tests. |
| P0 | `SyntheticDurableCredentialLab` is disposable SQLite, single-connection/in-process locking and lacks protected managed hosting, password reset and operational abuse controls. | Production managed DB with roles/migrations, independent multi-worker tests, anti-enumeration, credential policy and key lifecycle. |
| P0 | `recover` accepts an unsigned test `RecoveryApproval` dataclass and a test-only role verifier; it is not verified out-of-band guardian/learner proof. | Approved operational recovery identity assurance, durable one-use approvals and independent reviewer workflow. |
| P0 | Plaintext shared-device queue and learner-data retention/deletion operational controls have not been validated end-to-end. | Privacy/safeguarding signoff, mobile switching and logout tests, retention/deletion/export and incident exercise. |
| P0 | No protected dedicated staging service verified; existing Render synthetic service is publicly reachable and on another branch. | Protected internal/private staging target with synthetic fixtures and restricted access before staging UAT. |

## Smallest next release path
1. **Keep PR #91 draft/unmerged.** Do not promote branch or enable synthetic routes in production.
2. Pick a trusted identity/authorization provider and secure private staging target; document actual role governance and technical secrets. No fabricated signoffs.
3. Build a *new* integration branch with authenticated provider adapter, transactionally bound single-use approval, durable database, secure browser design and feature flag default OFF.
4. Run cross-device, multi-worker, rollback and independent security/privacy review on synthetic staging.
5. Only after signed release approval merge the separately reviewed integration PR and inspect Render deployed commit.
6. If a README-only public update is desired now, isolate it in a documentation-only PR rather than merging experimental identity code.

**Evidence:** GitHub Actions run #650 https://github.com/stephenrabbi/robo-teacher-pilot/actions/runs/38155408833 ; PR #91 https://github.com/stephenrabbi/robo-teacher-pilot/pull/91.

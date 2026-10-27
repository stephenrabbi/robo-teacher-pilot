# PR #85 consolidated security review — 11 October 2026

**Decision: NO-GO for production merge, public enrollment, live learner records, or deployment.** This is a source/CI evidence review of a synthetic research branch, not an independent security assessment.

**Review scope:** PR #85 at commit `f3a9e51a9ff21afec104642252704561dfde5b1e`; the identity, API, SQLite and PostgreSQL components; synthetic browser queue; architecture review documents; the successful [CI run #605](https://github.com/stephenrabbi/robo-teacher-pilot/actions/runs/38147112620). The PR remains draft and unmerged. No live service or real devices were security-tested.

## Evidence reconciled with older documents

The original `pr85-production-readiness-gate.md` is a **historical finding snapshot**. It is not an accurate current-state checklist: its S01/S03/S04/S05 descriptions precede subsequent changes. The old issuer methods `DurableSyntheticIdentity.issue`, `VerifiedEnrollmentGateway.issue`, and `TestIdentityAuthority.issue_for_approved` were removed. Both synthetic progress APIs reject unauthenticated sessions and check durable enrollment plus session epoch. Disposable PostgreSQL CI exercises event scoping, idempotency, multi-client submissions, revocation, backup/restore, restricted runtime role and transaction interruption. These facts **reduce specific technical risks, but do not close production controls**.

## Mandatory blockers — accountable closure evidence

| ID | Status | Production release blocker | Evidence required for closure |
|---|---|---|---|
| P0-A | **OPEN** | Real-world school/guardian enrollment and recovery authority absent. Synthetic signed assertions do not establish the issuer's real identity or the lawful guardian's authorization. | Named accountable school authority, guardian/assent policy, approved provider trust and revocation flow, independent negative tests, audit logs |
| P0-B | **OPEN** | Real credential provisioning is guarded only by caller-supplied `authorized_operator=True`. No trustworthy operator authentication or lifecycle. | Authenticated operator role model, provisioning approvals, rotation/disable, revocation and anti-impersonation tests |
| P0-C | **OPEN** | Legacy test signing helper remains importable to any code with the signing key; synthetic APIs deliberately depend on test-only keys. | Separate deployable package/build boundary; least-privilege signing custody; release-time imports, routes and secret scans; no public arbitrary-subject issuance |
| P0-D | **OPEN** | Plaintext synthetic offline queue in browser localStorage has not been redesigned for real shared devices. | Server-first/minimized-storage design, secure session switching, XSS/CSP review, lost-device/logout tests on actual mobile browsers |
| P0-E | **OPEN** | Minor-data legal/safeguarding governance incomplete. | Named controller/processor, lawful authority and informed notice, retention and deletion/export process, vendor/subprocessor review, incident response and independent privacy review |
| P0-F | **OPEN** | No managed DB with production access controls, monitoring, secrets, encrypted backup policy, operational recovery/rollback, and release control. | Separate managed staging, scoped least-privilege roles, backups/restore and restore-point objectives, monitoring and migration rollback drill |
| P0-G | **OPEN** | Missing independently reviewed end-to-end authenticated school/guardian-to-mobile-to-server integration. | Multi-device Android/iOS, low bandwidth/offline, multi-worker concurrency, explicit safeguarding and external security sign-off |
| P1-A | **OPEN** | Abuse and rate limits beyond synthetic per-account login/recovery throttling incomplete. | Enrollment/recovery initiation throttles, enumeration resistance, systemic and operator audit monitoring |
| P1-B | **OPEN** | Offline/recovery and database failure injection limited to synthetic CI scenarios. | Defined failure model, replication/backup retention tests, last acknowledged event recovery, resilient restore process under production-like topology |

## Security contracts that are supported by CI (synthetic-only)

- Disabled-by-default standalone APIs: SQLite `synthetic_api.py` and PostgreSQL `postgres_synthetic_api.py`; neither mounted in live `main.py`/`v25_app.py`.
- Verified signed bearer principal, school/learner-scoped event access, durable enrollment and session epoch checks.
- Epoch-sensitive SQL locking during PostgreSQL event read and write, coordinating with epoch updates.
- Identical event retries are idempotent; different content with same scoped event ID is rejected.
- Disposable PostgreSQL backup/restore preserved acknowledged event and epoch; uncommitted test insert rolled back on disconnect.
- Restricted CI runtime DB role prevented schema changes, enrollment updates and table deletion.

**Limits:** CI does not establish production auth, independent consent validity, mobile data confidentiality, actual availability/restore objectives, safety of localStorage, or safe operation under managed service constraints. PostgreSQL adapter currently uses connection factory selected by caller; an untrusted caller must never provide connection strings or sign tokens. Offline browser queue remains an unresolved risk.

## Go/no-go decision and explicit stop point

1. **Freeze further synthetic feature expansion.** The implementation has adequate prototype evidence to identify the next material dependencies; expanding fixtures endlessly has diminishing value.
2. **Do not merge PR #85.** Preserve its tests, docs and reviewed changes as research evidence, not release artifacts.
3. **Next decision is external to this PR:** agree on the school/guardian approval and credential model, retention/deletion policy, and managed staging provider before further integration code.
4. After those decisions, create a **new, separately reviewed integration PR** with truly authenticated provider enrollment and least-privilege staging infrastructure; retain a disabled-by-default feature flag. Test on real devices with synthetic data; obtain independent security/privacy approval before any pilot data flows.
5. Existing production classroom and existing pilot/evidence work remain separate and unchanged.

## Review limitations and document hygiene

This review reconciled available repository contents and CI but did not execute independent penetration testing or an external legal/child-safeguarding assessment. Previous dated files (`pr85-production-readiness-gate.md`, `pr85-session-issuance-audit.md`, `pr85-managed-storage-migration-gate.md`) contain historic observations, not continuously updated proof of unresolved flaws. Prefer this consolidated review for **current disposition**, while treating any test-specific conclusions as synthetic evidence only.

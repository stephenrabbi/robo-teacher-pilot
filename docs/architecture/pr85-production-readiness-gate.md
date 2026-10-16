# PR #85: release security assessment and integration decision
**Review date:** 11 October 2026
**Scope:** isolated secure-progress feature branch. Source-level review of synthetic_api.py, durable_identity.py, signed_approval_provider.py, browser_queue.cjs, current CI coverage and prior architecture notes.
**Decision: NO-GO for production merge, live pupil records, or public staging enrollment.**

## What is already evidenced
- Synthetic per-school/per-subject event persistence, signed token checks and duplicate-event handling.
- SQLite-backed synthetic enrollments, independently signed *test* decisions, one-use approval records, single-use recovery and timed recovery-submission lockouts.
- Isolated FastAPI progress API and negative authorization tests; one set of Playwright Chromium tests covering multi-tab lock behavior and simulated queue isolation.
- CI checks for the above have passed on earlier branch commits. Tests are not a substitute for independently reviewed production security.

## P0 blockers — mandatory before any real learner-data integration

| ID | Gap observed in source | Why this matters | Required closure / acceptance evidence |
| --- | --- | --- | --- |
| S01 | `build_synthetic_progress_app(... enrollment_connection=None)` allows an explicit enabled API without enrollment lookup. | Correctly signed session can reach storage without durable enrollment enforcement if misconfigured. | Production-intended factory must fail closed without durable enrollment verifier; negative test for missing verifier/config and all request paths. Do not break synthetic-only legacy tests without an intentional migration. |
| S02 | `DurableSyntheticIdentity` uses signed **synthetic** school decisions; no real trusted identity provider, authentic school/guardian approval, or documented reviewer lifecycle. | A signature validates the chosen test key, not the real-world authority or consent. | Select an actual independent provider, verify reviewer identity and approval policy, implement registration/revocation/audit and test malicious enrollment/recovery attempts. |
| S03 | `issue(subject, school)` can mint a session for *any enrolled pair* when called by trusted Python code, without a separate login proof; do not expose this on the web. | Enrollment is not authentication. | Real proof-of-possession/login session flow; no public arbitrary subject-token issuance; tests for impersonation and session theft. |
| S04 | Recovery creates a new session but does not revoke previously issued still-valid tokens. | A lost/stolen old session remains usable until expiry. | Durable session generation / revocation checks on every read/write; test old-token denial immediately following recovery and enrollment revocation. |
| S05 | Prototype storage is local SQLite, without production managed encrypted backups, restore exercises, migrations, access controls or multi-worker transaction review. | Restart persistence does not prove resilience on a real service. | Isolated managed database architecture, backup/restore tests, retention and deletion, key rotation, monitoring and rollback. |
| S06 | `browser_queue.cjs` stores synthetic events in plain `localStorage`; scope keys are client-controlled and browser storage is shared within a profile. | A real learner's content and scores could leak on shared phones or through same-origin scripts. | Design server-first authenticated sync, minimise browser content, safe offline encryption/key lifecycle if offline is retained; XSS/CSP and shared-device threat tests. |
| S07 | Current rate limit covers failed `complete_recovery` attempts per subject/school only; no initiation throttles, broad account enumeration defense, IP/device/network abuse guard or operator audit. | An attacker could trigger repeated workflows or distribute attacks. | Gate initiation, cap per-account/provider and systemic traffic, generic failure responses, security monitoring and escalation. |
| S08 | Real minor-data governance remains unapproved: consent/assent, school/guardian authority, retention/deletion, access/export, incident plan, vendors. | A technically working API may still be inappropriate for children's records. | Documented authorization by participating schools and lawful guardian process, data minimization/privacy review, clear operator responsibility and incident response. |

## P1 operational validation required before rollout
- Expand browser coverage to Android Chrome and iOS Safari; camera/microphone denial, shared-device switching, concurrent network loss, refresh, quota errors and failed restores.
- Verify scoped sync with a fully authenticated end-to-end browser-to-server flow, not only mock submissions and synthetic sessions.
- Protect staging behind authenticated network controls, not only an unadvertised URL; use distinct secrets and synthetic fixtures.
- Perform concurrency/atomicity review of enrollment, recovery, progress and approval tables under separate DB connections; add crash-injection tests.
- Validate safe logs with no tokens, recovery challenges, names, student answers or other personal data.
- Have an independent security/privacy reviewer approve release gates.

## Implementation order (avoid indefinite prototype expansion)
1. **Freeze scope and repair S01/S03:** define one non-public, fail-closed integration contract requiring provider-authenticated identity and durable enrollment. Do not add public token issuance.
2. **Select real-world trust/consent provider:** decide which schools and authorized guardians can approve enrollment/recovery, how they verify identity, and how approvals are revoked.
3. **Implement server-side session revocation and recovery security** with tests for stolen/old sessions; add end-to-end login and scoped API tests.
4. **Choose durable service architecture** and run backup/restore, concurrency, retention and deletion tests using synthetic accounts only.
5. **Conduct staging UAT** on real devices, shared phones, low-bandwidth flows and accessibility; independent safeguarding/security sign-off.
6. **Separate go/no-go decision:** only then consider production code integration via a new reviewed release PR, controlled feature flag, dry-run migration and rollback.

## Stop conditions
Do not merge PR #85 into `main`, connect real pupil data, or enable public enrollment while any P0 blocker is open. Current live Robo-Teacher Mathematics classroom remains operational separately. Avoid claiming the complete real-world identity or mobile sync system is already delivered.

**Audit caveat:** This is a code-and-test review, not a penetration test, independent legal opinion, proof of operational backups, or evaluation on physical Android/iPhone devices.

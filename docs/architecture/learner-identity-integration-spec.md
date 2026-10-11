# Learner identity integration — decision and acceptance specification

**Status: DESIGN ONLY — NOT AUTHORIZED FOR DEPLOYMENT.** This branch starts from `main`, not PR #85. No live login, API, progress storage, child roster, or production settings are changed.

## Purpose
Define the real-world trust boundary needed before learner accounts and persistent progress can be connected to Robo-Teacher. PR #85 remains a synthetic research prototype and should not be merged wholesale.

## Proposed workflow (requires approval by school/safeguarding authorities)
1. **Participating school** appoints named authorized reviewers with verified identity, defined term, and revocation mechanism. A school-issued invitation is not itself learner authentication.
2. **Guardian and learner** receive age-appropriate information and complete the documented authorization/assent process applicable to the pilot. Use minimum necessary data; do not collect guardian IDs or student names in this planning repository.
3. **Enrollment** occurs only after a server-side independent check of the school's approval *and* the guardian/learner authorization policy; record provenance, purpose, timestamp, scope and expiration in an auditable store.
4. **Credential provisioning** requires authenticated operator authorization, separate from the learner's public login. The operator cannot mint a learner session simply by selecting school and subject.
5. **Login** requires a separate learner-held authentication factor. Bind the short-lived token to school, pseudonymous subject, audience, issuer and current revocation version; server checks epoch each request.
6. **Recovery** requires a stronger independently verified approval workflow, rate limiting, and a single-use challenge. Completing recovery increments the durable session epoch before returning a new session.
7. **Revocation/deletion**: school/guardian withdrawal, compromised device and learner departure trigger access disable, session revocation and documented retention/deletion rules.
8. **Shared-device safety**: remove or minimize plaintext local event storage, ensure logout and learner switches clear previous identity and queued events; independently test low-bandwidth scenarios.

## Requirements that cannot be guessed from repository code
- Accountable school authority and participating school(s), approved reviewer appointment/verification
- Who legally authorizes learners of different ages; consent/assent records and withdrawal channel
- Privacy roles, vendors, minimum fields, data-retention period and deletion/export contacts
- Recovery verification and escalation, shared family phone constraints and accessible alternatives
- Hosting region, protected staging environment, incident escalation and independent reviewer

Until these are agreed, **no enrollment endpoint, token issuer, credential-provisioning route or user-data migration may be connected to the live app**.

## Acceptance criteria for a later implementation PR
- [ ] Written school/guardian workflow and privacy review signed off
- [ ] Named reviewer role governance, authentication, expiry, revocation and audit
- [ ] No caller-controlled provisioning bypasses or arbitrary subject session issue method
- [ ] Separate credential verification, failed-login throttling and generic errors
- [ ] Atomic recovery-and-revocation confirmed under concurrent reads/writes
- [ ] Managed synthetic staging only; no real pupil identifiers or imported school spreadsheets
- [ ] Secure browser/offline design with shared-device, logout and XSS/CSP review
- [ ] Negative tests for impersonation, stolen token, unapproved operator and wrong-school access
- [ ] Backup/restore, incident response and deletion/export evidence with documented approval
- [ ] Android Chrome/iOS Safari staging UAT and independent child-data security review
- [ ] Separate release PR, explicit production go/no-go, rollback plan and disabled feature flag

## Deliberate exclusions
No code import from PR #85; no PostgreSQL credentials, application route changes, deployment config changes, or production deployment. This document is an implementation gate, not a substitute for actual school/guardian approval.

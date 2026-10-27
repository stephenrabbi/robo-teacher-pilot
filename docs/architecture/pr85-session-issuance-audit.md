# Session-issuance audit — PR #85 (11 October 2026)

**Scope:** PR #85 diff, the isolated progress_store modules and their tests. **NO-GO for merging into the live classroom.** No real pupil records or deployed routes were accessed.

## Findings and classification

| Component | Can mint a session? | Identity proof required? | Exposure / disposition |
|---|---|---|---|
| `progress_store/session_auth.py:issue_test_session` | Yes, with server signing secret and caller-supplied subject/school | No; low-level cryptographic fixture helper | Must remain a private test-only helper; never expose directly in endpoints, scripts or integration interfaces |
| `progress_store/identity_prototype.py:TestIdentityAuthority.issue_for_approved` | Yes, after volatile approved flag | No individual login proof; flag alone | **Legacy test-only**, not connected to deployed API; remove/retire before any actual identity service is built |
| `progress_store/enrollment_gateway.py:VerifiedEnrollmentGateway.issue` | Yes, after test reviewer approval | Reviewer identity only; no learner credential | **Legacy test-only** adapter; not acceptable for authentication or production integration |
| `progress_store/proof_login.py:SyntheticProofLogin.login` | Yes | Separately provisioned long credential verified by salted scrypt hash; SQLite per-account throttling | Intended synthetic proof-of-possession path; provisioning uses a caller-controlled boolean, so still not adequate for real deployment |
| `progress_store/durable_identity.py:DurableSyntheticIdentity.complete_recovery` | Yes | Single-use recovery challenge created from signed synthetic approval, with attempt throttling | Intended synthetic recovery path; real guardian/school recovery authority is unimplemented |
| `progress_store/durable_identity.py:DurableSyntheticIdentity.issue` | **Removed** | Previously none beyond enrollment | Fix committed; tests do not rely on it |
| `progress_store/synthetic_api.py` | **No issuance endpoints** | Verifies signed sessions, enrollment membership and durable epoch | Opt-in, unmounted; rejects missing enrollment storage and epochless tokens |

## Critical trust-boundary limitations

1. Possession of the server signing secret still allows `issue_test_session` to mint signed, correctly epoch-tagged tokens for an arbitrary subject. This helper intentionally requires the secret; proper secret custody is essential. Test environments must use distinct keys and must never ship the helper as an authentication route.
2. The legacy volatile test gateway does not prove possession of a learner credential, and its sessions are not bound to the current durable epoch. It must not be presented as a release-quality identity mechanism.
3. `SyntheticProofLogin.provision(authorized_operator=True)` is caller-supplied test scaffolding; it is not a trustworthy school/guardian approval mechanism. Never expose it through HTTP.
4. Synthetic recovery approval signatures verify a configured test key, not real-life reviewer authority, parent consent, or a child's identity.
5. Credential changes and logout-all-sessions need explicit epoch bump and server-side revocation. Recovery already increments the epoch, and enrolled progress API GET/POST validates it.
6. Token validation is performed prior to progress persistence, but on a shared SQLite deployment there remains a potential time-of-check/time-of-use race between authentication validation and a concurrent recovery/revocation transaction. A production integration needs transactionally bound authorization to writes, plus concurrency tests.
7. The test-only low-level signing helper appears in direct authorization-negative tests by design. Avoid confusing test fixture token issuance with authenticated login.

## Integration decisions (binding for PR review)

- **Acceptable synthetic issuance:** `SyntheticProofLogin.login()` and `DurableSyntheticIdentity.complete_recovery()`, under test-only isolated configuration.
- **Disallowed for real usage:** any caller-supplied `issue_test_session`, `issue_for_approved`, legacy gateway `issue`, or UI-side token creation.
- **Release contract:** authenticated proof of possession or independently authorized recovery; durable enrollment and revocation epoch checked on every request; secret management, issuer/audience/time checks; no arbitrary subject token endpoints; audit trail; school/guardian authorization.
- **Before merging:** retire legacy issuance modules from the production-intended package (or physically separate test utilities), review import graph and deployed app registration, establish real authority for credential provisioning, test recovery/logout revocation under concurrent reads and writes, security review with child-data consent.
- **No retroactive claim:** passing synthetic CI does not demonstrate deployment-grade authentication, consent, managed infrastructure or physical-device security.

## Evidence inspected

PR #85 unified diff, `session_auth.py`, `synthetic_api.py`, `durable_identity.py`, `proof_login.py`, `identity_prototype.py`, `enrollment_gateway.py` and test suites listed in the PR. This was a repository-level source audit, not a whole-system penetration test or formal code security certification.

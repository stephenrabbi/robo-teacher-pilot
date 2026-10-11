# Security review — isolated progress prototype (11 October 2026)

## Test status
- Shared-device queue CI for commit b83ea3b passed both jobs.
- Regression fix on this branch now invalidates the old session even if replacement session validation fails. This fixes a fail-open shared-device account-switch case. New test added; latest CI must pass before approval.

## Blocking gaps before any real learner rollout

1. **Authentication and enrollment are not real.** The synthetic client accepts caller-supplied subject/school scope; a caller can impersonate a learner in local storage. In-memory approvals take a boolean / reviewer name and do not verify guardian or school authority.
2. **Recovery verification is not real.** A caller asserting approved_recovery=True can generate a recovery challenge. The challenge is one-time but approval has not been externally proved.
3. **Browser queue is plaintext.** Browser localStorage is accessible to scripts in the same origin and anyone with device/profile access. Never put real pupil scores in this prototype or treat client-derived scope as a security boundary.
4. **Shared-device and refresh races.** The single-flight guard only covers one JS runtime and one storage object; separate tabs or browser processes can race. Server idempotency helps, but an app-level Web Lock or durable queue claim protocol and cross-tab tests remain necessary.
5. **In-flight requests.** Switching sessions blocks *later* submissions but cannot retract an already transmitted request. The backend must validate the signed token and scope for every request.
6. **Queue durability.** Browser writes may fail (quota/private mode) and localStorage can be cleared. UI must show pending status and failed-save warnings, with an approved device recovery strategy.
7. **Database durability.** Synthetic SQLite connections are not a managed encrypted backup/recovery configuration, and browser tests do not prove production-ready multi-worker behavior.
8. **API exposure.** The opt-in FastAPI app is deliberately unmounted. A staging environment still needs network perimeter restriction, secret lifecycle controls, request limits, monitoring, and independent security review. No publicly accessible learner issuance endpoint should be introduced.
9. **Data governance.** Define minimal schema, retention/deletion windows, export/access requests, school/guardian consent and incident response before real records are stored.

## Required release criteria
- Actual independent authentication + verifiable consent/recovery authority.
- Automated negative authorization tests at the deployed API boundary.
- Durable managed storage, backups, retention/deletion and tested restoration.
- Multi-tab/browser synchronization recovery and mobile UAT.
- Explicit dry-run migration plan and rollback.
- Security/privacy sign-off before connecting real student records.

**Conclusion:** Suitable for further synthetic development, not ready to stage with real users, not ready for production merge.

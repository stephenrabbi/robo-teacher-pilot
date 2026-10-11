# Robo-Teacher release handoff — PR #85

**Disposition: NO-GO.** This is a release handoff checklist, not approval to deploy. As of 11 October 2026 the Render production service `robo-teacher` deploys `main` automatically; V2.5 staging deploys `fix/stable-voice-playback`. The PR #85 branch is `feat/secure-progress-storage-design` and is not attached to a Render service.

## Non-negotiable boundaries
- Never merge PR #85 directly into `main`, change production Render branch to this feature branch, or trigger a manual deploy expecting it to include PR #85.
- Do not mount `progress_store.synthetic_api` or `progress_store.postgres_synthetic_api` on the live application.
- Do not import any real pupil CSV, spreadsheet, database, identifiable assessment, or actual school roster into synthetic tests or prototype APIs.
- Keep feature flags disabled until external authorization and privacy reviews are completed.

## Evidence before opening a separately reviewed release PR
- [ ] Identify school approvers and verify their identity independently; define guardian/assent authority and recovery escalation.
- [ ] Replace caller-controlled `authorized_operator=True` credential provisioning with authenticated, auditable trusted-operator workflow.
- [ ] Remove or isolate the low-level test token helper from deployable artifacts; implement safe secret custody and rotation.
- [ ] Replace plaintext shared-device browser persistence with an approved, threat-tested strategy.
- [ ] Approve data controller/processor responsibilities, retention, deletion/export, incident response, vendor agreements, and Nigerian minor-data safeguards.
- [ ] Provision restricted managed staging with dedicated secrets, migrations, rollback, operational backup and access monitoring.
- [ ] Verify authenticated enrollment/login/recovery and scoped progress from browser to staging API using synthetic accounts; test concurrency, mobile/shared-device switching and offline failures.
- [ ] Obtain independent security and privacy sign-off; document reviewer, date, scope, evidence and remaining risks.

## Release procedure after the above gates
1. Create a NEW integration branch and pull request selecting only reviewed production-intended changes. Do not merge all of PR #85.
2. Run all unit, database, browser and security checks. Confirm no public enrollment/token issuance endpoints or non-consented learner identifiers.
3. Deploy to a protected staging service using an explicit reviewed branch and only synthetic records; inspect logs, access restrictions and rollback.
4. Review real mobile UAT and staging results with the authorized safeguarding/technical owners.
5. Require explicit go/no-go approval for production rollout; use a disabled-by-default feature flag and documented rollback.
6. Only then merge the separate release PR and verify the Render deployment commit, smoke tests, and access controls.

**Current decision:** Continue operating the existing production classroom independently. No PR #85 functionality is authorized for public deployment.

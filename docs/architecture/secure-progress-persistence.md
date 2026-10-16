# Secure learner progress persistence — implementation contract

Status: design and test specification only. No production data migration or persistence endpoints enabled.

## Current baseline (v2.6.1)
- Google Sheets contains pseudonymous practice, diagnostic, and reporting records.
- Browser localStorage contains saved lessons, adaptive memory, and profile mappings.
- Resume snapshots expire after seven days.
- Current learner keys are browser-held; a learner code or nickname must **not** become an authentication credential.

## Security properties required before enabling cross-device access
1. **Authentication**: issue short-lived, server-validated learner sessions only after an approved school/guardian-supported enrolment and recovery flow. Do not authorize by nickname, class, guessable pilot code, or client-supplied learner ID alone.
2. **Authorization**: bind every read/write to a server-side authenticated subject and school scope; ignore any client-provided owner field. Apply the same restrictions to teacher summaries. Include negative cross-learner and cross-school tests.
3. **Minimisation**: store pseudonymous learner ID, class/term, topic/assessment progress, revision metadata and necessary timestamps. Do not persist full questions, image/audio uploads, contact details, or tutor transcripts in the new store.
4. **Integrity**: validate payload schemas and size limits; use unique event IDs and idempotent upserts; never allow a stale device to overwrite newer mastery events. Store UTC timestamps and schema version.
5. **Durability**: use a persistent managed database with encryption in transit, protected backups, recovery drill, and a written retention/deletion policy. Browser storage is a cache, not the source of truth.
6. **Child safety and privacy**: guardian/school permissions, restricted service credentials, secret rotation, audit metadata without sensitive content, deletion/access procedures, and breach response must be defined before rollout.
7. **Migration**: preserve existing local profiles and Sheets records. Start with synthetic learners in a private test environment; opt-in migration only after authorization and reconciliation checks. No automatic import from a device merely because a code matches.
8. **Availability**: offline updates queue locally, retry safely, and show whether progress was synchronized. Recovery must avoid duplicate grading and loss of local work.

## Suggested minimum record contract
```json
{
  "schema_version": 1,
  "event_id": "random UUID",
  "learner_subject": "derived server-side, never client-authoritative",
  "school_scope": "derived server-side",
  "class_level": "JSS2",
  "topic_key": "curriculum-controlled-key",
  "event_type": "practice_completed",
  "correct": 3,
  "total": 5,
  "occurred_at": "UTC ISO-8601",
  "revision": 1
}
```
The sample above is a design sketch, not an API that exists today.

## Gate tests
- Unauthenticated read and write denied.
- Learner A cannot read/update learner B's records, even with a known pilot code.
- Teacher scope cannot read another school's data.
- Replayed events cannot double-count progress.
- Concurrent device updates retain both valid events.
- Restart and database restoration recover progress.
- Data export and deletion work within approved policy.
- Failed network responses do not silently claim synchronization.

## Rollout stages
1. Review data governance and select managed storage/authentication approach.
2. Implement schema, server-side authorization, and automated synthetic tests in an isolated development branch.
3. Connect client with offline queue and explicit sync status, behind a disabled-by-default feature flag.
4. Test in staging on desktop/Android/iPhone and recover from simulated interruptions.
5. Review security and privacy; roll out to a small consented cohort, then production.

**Never enable or deploy persistent learner records until the authorization, policy and migration gates pass.**

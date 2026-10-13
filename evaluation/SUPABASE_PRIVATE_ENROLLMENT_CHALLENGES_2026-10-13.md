# Private test-only durable enrollment challenges (2026-10-13)

Secondary Supabase project: `drzaxpofuhqchmpkwhpy` ONLY. Production project remains untouched.

Migration: `private_test_one_time_enrollment_challenges` creates non-exposed schema `robo_test_private` with the `enrollment_challenges` table. Columns: unique challenge UUID, Supabase Auth `user_id`, unique binary `proof_digest`, `expires_at`, nullable `consumed_at`, and `created_at`. RLS is enabled. Access is revoked from PUBLIC, anonymous and authenticated roles, including schema USAGE. Neither the database nor application stores a plaintext challenge. **No test endpoints have been mounted and no client RPC is exposed.**

## Executed test transaction
Synthetic Learners A and B (already verified Auth users). A privilege-level database transaction inserted an artificial digest, used one conditional UPDATE per attempted consumption and verified row counts:
- other-account attempt => 0
- first use by owning account => 1
- replay by owning account => 0
- expired proof => 0

The transaction finished with ROLLBACK. Follow-up SQL confirmed zero retained challenges and no authenticated schema access, SELECT or INSERT privileges.

The test uses `decode(md5(...),'hex')` **only to generate distinct non-secret fixture bytes**, not as the production digest algorithm. Production must use a cryptographically secure randomly issued token and SHA-256 (or appropriate HMAC) digest, with minimum entropy, constant-time validation where relevant, server-issued browser challenge session binding, atomic consumption, request rate limits, expiration, audit logging without secret leakage, replay/concurrency tests, and guardian permissions.

## Unverified/release blockers
- No live backend issuance/consumption implementation or genuine two-account HTTP API calls.
- No validated proof of ownership of historical `WEB-` classroom records.
- No production cloud-progress enrollment, saving or recovery.
- Do not advertise this as operational account recovery or cross-device syncing.

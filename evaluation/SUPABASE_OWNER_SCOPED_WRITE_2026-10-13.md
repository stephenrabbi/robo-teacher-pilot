# Supabase owner-scoped synthetic progress write — 2026-10-13

**Environment:** separate testing project `drzaxpofuhqchmpkwhpy`, not the production Robo-Teacher Supabase project. Two synthetic learners and two synthetic progress rows. The live classroom identity feature flag remains OFF.

## Test-only implementation
Migration `test_only_owner_scoped_progress_rpc` adds a unique index on `(user_id, topic_code)` and `public.robo_save_own_progress(text, smallint)`. This SECURITY DEFINER function:
- derives `user_id` with Supabase `auth.uid()`; caller cannot pass `user_id` or `school_id`;
- requires an existing learner profile and validates topic format and score bounds;
- upserts only the authenticated user's topic record;
- permits RPC EXECUTE to the authenticated database role, denies anonymous EXECUTE; retains no direct learner INSERT/UPDATE/DELETE on progress tables.

## Executed checks
Simulated authenticated transaction for Learner A: own topic score changed to 52 in-transaction; other user's records invisible. Rolled back.
Simulated authenticated transaction for Learner B: own topic score changed to 67 in-transaction; other user's records invisible. Rolled back.
Database permissions: anon RPC execute denied; authenticated RPC execute permitted; authenticated direct table insert and update denied. Original two synthetic progress records retained.

**Limits:** these write checks use a simulated authenticated SQL role/JWT subject, **not two independently issued API tokens**. The founder-reported real Auth/API test on 2026-10-13 tested SELECT isolation only.

## Security concerns / production blockers
- **Never deploy this proof-of-concept RPC to production unchanged.** It accepts `p_mastery_score` supplied by the caller, so a learner could fake their score. Production evaluation and scoring must be performed or independently verified by trusted server code with rate limits, auditability and anti-replay controls.
- Supabase security advisor warns when authenticated users can execute this intentionally SECURITY DEFINER function. Review the privilege model, attack surface, and schema exposure before any release. Ref: https://supabase.com/docs/guides/database/database-linter?lint=0029_authenticated_security_definer_function_executable
- The test project also reports leaked-password protection disabled: https://supabase.com/docs/guides/auth/password-security#password-strength-and-leaked-password-protection
- The schools table remains intentionally inaccessible to clients without a policy.
- Next: test denied writes and accepted writes with genuine synthetic Auth JWTs via HTTPS, test cross-account adversarial requests, implement trusted scoring and guardians' account recovery.

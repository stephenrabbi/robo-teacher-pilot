# Restricted test enrollment role: RLS configuration — 2026-10-13

**Isolated Supabase project** `drzaxpofuhqchmpkwhpy` only. Never promote this migration to production without security review.

The prior `robo_test_enrollment_executor` role is NOLOGIN and cannot directly authenticate to Postgres. Its existing column-scoped grants allow challenge creation/consumption and cloud-enrollment creation, but the two private tables have RLS enabled. To permit their intended use under this role, migration `allow_test_executor_private_enrollment_rls` added five role-scoped policies for `robo_test_private.enrollment_challenges` and `robo_test_private.cloud_enrollments` (SELECT/INSERT and challenge UPDATE only when an unconsumed record becomes consumed).

The policies use broad row predicates `true` **for this privileged, private test role** and rely on that role remaining inaccessible to browser identities, NOLOGIN, and ungranted to untrusted logins. Such policies do not provide per-user isolation for the executor; caller-side verified identity and private transaction logic remain mandatory.

**Verified:** Five policies present, anonymous/function EXECUTE false, authenticated/function EXECUTE false, executor/function EXECUTE true.

**Not verified:** Supabase SQL runner cannot `SET ROLE robo_test_enrollment_executor` (permission denied); no live connection exists under this role. The role cannot log in; no database credential or service login was created. Consequently its operational database transaction, RLS interactions, and genuine Auth-to-DB HTTP flow are still untested. No production deployment or cloud sync is enabled.

Before a restricted staging connection: use a separate securely managed staging credential/role membership only with appropriate authorization, verify grants and `current_user`, run read/write/rollback tests, enforce request security on the server, and never expose connection strings or database passwords in client code/GitHub.

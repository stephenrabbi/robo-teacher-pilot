# Robo-Teacher Supabase read-only availability checks

This is a **small free-plan resilience measure**, not a guarantee that a Free
Supabase project will never pause. Supabase says a few user database requests
each day are usually sufficient; only paid plans are exempt.

- **Target:** dedicated project `gpshctxxgjvzplrbegwf`, named Robo-Teacher.
- **Do not target:** older inactive project `drzaxpofuhqchmpkwhpy`.
- **Frequency:** three GitHub Actions scheduled checks daily (UTC), plus manual dispatch.
- **Request:** a single `GET /rest/v1/robo_schools?select=id&limit=1`.
- **Data:** read only; no student/profile/progress tables, dummy enrollments or writes.
- **Failure handling:** red GitHub Actions run with non-secret status diagnostics.

## Required one-time setup

1. In Supabase, open project `gpshctxxgjvzplrbegwf` and copy its **publishable / legacy anon API key**, **not** its service-role or secret key.
2. In GitHub `stephenrabbi/robo-teacher-pilot`, navigate to
   **Settings → Secrets and variables → Actions → New repository secret**.
3. Create repository secret **`ROBO_SUPABASE_HEALTH_API_KEY`** with that key.
4. After merging this PR to the default branch, open **Actions → Robo-Teacher Supabase read-only health → Run workflow**. Check that the run succeeds. Scheduled workflows normally run from the default branch, and can be delayed.

If the workflow reports HTTP 401/403, verify the chosen publishable key and
whether the configured RLS / Data API grants permit a harmless read of
`public.robo_schools`. **Do not grant broad table access, disable RLS, or
use a service-role key simply to satisfy the check.** Stop and review the
least-privilege design instead.

Do not confuse these maintenance requests with usage by learners: **the live
classroom's Supabase identity adapter is intentionally unmounted** and must
remain so until consent, guardian recovery and secure account mapping are
properly validated. Production learner usage and database activity require a
separate integration project.

Relevant documentation:
https://supabase.com/docs/guides/platform/free-project-pausing

# Durable synthetic Supabase account links — 2026-10-13

Project: secondary test database `drzaxpofuhqchmpkwhpy` only; **not** the production Supabase project.

Applied migration `synthetic_test_account_link_uniqueness` creates table `public.robo_test_account_links`:
- `classroom_student_id` text PRIMARY KEY, constrained to test-compatible WEB-* format
- `supabase_user_id` UUID NOT NULL UNIQUE, FK to `robo_learner_profiles(user_id)`, ON DELETE CASCADE
- `created_at` timestamp
- RLS enabled with **no learner-visible policies**, and all access revoked from `PUBLIC`, `anon` and `authenticated`.

Two synthetic links were inserted through privileged test SQL:
- WEB-SYNTHETIC-A, mapped to synthetic Learner A
- WEB-SYNTHETIC-B, mapped to synthetic Learner B

**Database tests passed:**
1. Reassigning existing WEB-SYNTHETIC-A to Learner B raises a uniqueness violation.
2. Attempting to link Learner A to an additional classroom identity raises a uniqueness violation.
3. Exactly two links remain.
4. Anonymous users have no direct SELECT; authenticated users have neither SELECT nor INSERT.

**Scope / critical limitations:** These classroom labels are fabricated fixtures, **not** actual classroom token-verifier outputs. SQL constraints prevent duplicate links but do not authenticate an owner. The current signed classroom sessions have an independent pseudonymous identity and session issuance flow, which must be reviewed for impersonation and account takeover before any production binding. The live classroom still has no mounted Supabase account-linking route. No backend mapping writer or authorized cross-device persistence exists. Account recovery, device testing and guardian consent remain unresolved. Test-only fixture IDs must not be presented as live learners.

**Next:** Design a server-verified, consent-aware enrollment handshake and atomic mapping writer that cannot bind two existing identities without proving ownership. Test revoked/expired tokens, replay, concurrent claims and cross-account takeover through genuine API requests before release.

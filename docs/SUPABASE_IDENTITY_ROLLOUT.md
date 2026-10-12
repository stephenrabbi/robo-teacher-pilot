# Supabase identity integration — staged rollout

The existing open classroom works with an independent `IND-` learning reference or an optional school-issued code. Neither is a secure identity credential.

## Current foundation

- Supabase project `gpshctxxgjvzplrbegwf`: healthy; RLS on schools, profiles and progress.
- School associations can be NULL for independent learners. Profiles still require authenticated `user_id`.
- Authenticated users have read-only access to their own profiles and progress via RLS. No learner direct table write grants.
- `classroom/supabase-identity-gated.js` is a **fail-closed, unmounted adapter**. Both its internal feature constant and optional external switch must allow access; its internal switch is currently OFF. It must never be loaded into the production classroom or described as active account recovery.

## Safety gates before activation

1. Use separately controlled synthetic accounts (no real child records). Confirm Supabase Auth provider configuration and approved, age-appropriate parent/guardian permission and recovery method.
2. Verify an authenticated user cannot read or alter another user's rows, even when choosing a different school or learner code. Remember that Supabase anonymous Auth accounts use the `authenticated` database role and cannot recover on another device until properly linked.
3. Design audited backend-only enrollment/profile creation. An `IND-` reference cannot authorize linking an existing school learner profile. Verify actual school affiliation independently before assigning a school ID.
4. Test consent withdrawal, device loss, account linking, duplicate identities and recovery; retain a non-cloud path when guardian details are unavailable.
5. Add a separately reviewed, *default-disabled* browser integration once tests and safeguarding review pass; do not quietly turn on Supabase writes or automatic anonymous accounts for children.
6. Run Android, desktop and iPhone smoke tests including old school-code and no-code onboarding, alongside the automated suite, before deployment.

Supabase references: https://supabase.com/docs/guides/auth/auth-anonymous and https://supabase.com/docs/guides/auth/auth-email-passwordless.

## What is already released

PR #103 permits leaving the code blank; a random `IND-` reference is generated on Start Learning Now. This is public onboarding, **not** a cross-device Supabase account.

## Next technical milestone

Implement synthetic two-account RLS and persistence tests in an isolated, non-production environment; decide and test the recovery method, with appropriate guardian authorization. Only then wire browser authentication and audited progress writes.

# Synthetic Supabase Auth test — not yet executed

Project: `gpshctxxgjvzplrbegwf`. This standalone smoke test is deliberately **not a live classroom feature**.

## Prerequisites
1. Create two **disposable** Supabase Auth users by a separately approved administrator using the Supabase dashboard. Do not use real students or their emails.
2. Through a trusted administrative process, create a distinct synthetic learner profile **and at least one progress row** for each, with different `auth.users.id` values. Do not modify existing real user records.
3. Configure a GitHub environment named `synthetic-supabase-tests` with appropriately restricted access and five secret values: `ROBO_TEST_SUPABASE_PUBLISHABLE_KEY`, `ROBO_TEST_USER_A_EMAIL`, `ROBO_TEST_USER_A_PASSWORD`, `ROBO_TEST_USER_B_EMAIL`, `ROBO_TEST_USER_B_PASSWORD`.
4. Manually run the `Supabase Synthetic Two-Account Isolation` workflow.

The test logs in each independently authenticated user through Supabase Auth and reads profiles/progress using the user's access token. It **fails** if both accounts share an ID, if fixtures are empty, or if any fetched row belongs to another user. It uses only a publishable key; **never** put the service-role key in GitHub workflow secrets for this test.

Passing this check does **not** certify guardian authorization, enrollment, account recovery, production rollout, or full privacy compliance. Remove synthetic accounts/test rows after verification using a verified administrator workflow.

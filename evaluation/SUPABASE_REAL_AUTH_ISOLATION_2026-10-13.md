# Supabase synthetic two-account Auth/API SELECT isolation — 2026-10-13

## Scope and environment
- Secondary Supabase project only: `drzaxpofuhqchmpkwhpy` (Earlyon-Tech Brainery test environment).
- Two synthetic, email-confirmed accounts: Learner A and Learner B.
- Two separate synthetic profile rows and two distinct synthetic progress rows.
- User ran the local browser read-only Supabase Auth/API test and supplied its results in chat.
- **Evidence classification: founder-executed test, result log reported by user; not an independently observed browser execution.**
- No passwords, auth tokens, API keys, real minor information or synthetic user UUIDs stored in this document.

## Reported output
```text
Starting read-only Supabase Auth/API checks against test project only…
PASS: Learner A signed in and identity verified
PASS: Learner B signed in and identity verified
PASS: Learner A sees own robo_learner_profiles and not the other learner
PASS: Learner A sees own robo_learning_progress and not the other learner
PASS: Learner B sees own robo_learner_profiles and not the other learner
PASS: Learner B sees own robo_learning_progress and not the other learner
SUCCESS: Two real Supabase Auth sessions passed SELECT isolation.
NOT YET TESTED: account recovery, backend-authorized writes, production deployment.
```

## Interpretation
The user-reported browser run confirms successful login and expected own-row versus cross-row SELECT filtering **under the two test credentials**. This supplements the separate database-role RLS simulation. It does not establish email recovery, device switching, full permission coverage, adversarial security, backend-authorized progress writes, school account linking or safety for live student data.

## Release gates — remain off
1. Implement and test server-side authenticated ownership checks for progress writes. Never trust a nickname, school code or user-selected `user_id`.
2. Define guardian authorization, age-appropriate identity linking and real cross-device recovery. Synthetic `example.com` mailboxes cannot test email delivery.
3. Verify account linking/enrollment without allowing a learner to claim another school's code/profile.
4. Repeat genuine Auth/API read+write negative tests, signed-out behavior and token refresh/expiry in an isolated environment.
5. Test desktop, Android and iPhone workflows and audit privacy wording.
6. Activate only after review; `classroom/supabase-identity-gated.js` stays hard-disabled and the live classroom is unchanged.

Do not claim cross-device syncing or account recovery has launched.

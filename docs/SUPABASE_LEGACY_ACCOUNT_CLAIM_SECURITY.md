# Security decision: prevent legacy session takeover during cloud account enrollment

Current `classroom_api._new_session` derives a `WEB-...` identifier from a school learner code or browser-supplied learner key and signs a four-hour session. This authenticates possession of the newly issued classroom token, **not legitimate ownership of all prior records tied to that ID**. A student who knows another student's school code could ask for a session associated with that code. A sufficiently weak/compromised browser learner key has similar issues.

**Release rule:** Do not use `create_verified_binding` or `/supabase-test/verify-link` to migrate historical classroom progress merely because both tokens validate. Supabase Auth verification authenticates the account but does not solve historical classroom ownership. The test-only mappings WEB-SYNTHETIC-A/B are not authorization evidence.

This PR adds an **unmounted fail-closed gate** for future new-account enrollment and an always-denied legacy historical-claim function. Its callback is a test seam, not a real proof issuer or verifier. A secure future design requires fresh cryptographically random, one-time, server-held enrollment challenges with expiry, atomic consumption, device/session binding, authenticated Supabase identity, anti-replay rate limits, and guardian/teacher-approved historical migration where needed. A client-provided proof string, existing learner code, nickname, or session alone must never grant an old account's data. Use newly issued IDs for new cloud identities and retain old progress separately pending a deliberate verification procedure.

**No production feature flag or account-linking endpoint is enabled.**

# Existing practice scoring is server-side — Supabase integration boundary

Robo-Teacher currently uses two related but distinct reporting paths:

- `/api/classroom/practice/answer` receives a session token and selected answer. `practice.answer_practice()` compares the answer with `state.expected` held by the server. Upon a completed practice run, the API queues `save_result()` using its server-computed summary. **This is the preferred source for future verified practice-progress snapshots** after authenticated learner linkage, attempt replay protection and consent review.
- `/api/classroom/mastery/event` currently receives a `correct` boolean and `correct_choice` from the client. Do NOT regard this client-supplied assessment signal as verified scoring for Supabase mastery records without independent server verification.

The standalone `trusted_assessment_scoring.py` prototype from PR #110 is not activated. Do not deploy two competing scorers or disrupt current practice/session UI.

## Next backend work before cloud persistence

1. Authenticate a Supabase JWT on the **server** and derive an immutable user ID; do not accept a user ID, school code, claimed mastery score, or learner nickname as identity from the browser.
2. Link the verified Supabase identity to the existing pseudonymous classroom session via a validated, explicit account-link operation. Reject a mismatch and prevent codes from claiming another account.
3. At completion of a server-graded practice attempt, build a bounded normalized topic/progress event from the existing server-side result and use a privileged backend operation with minimum required permissions.
4. Verify idempotency, replay resistance, retries and error isolation. Failure of Supabase must not break the current non-cloud classroom.
5. Implement real guardian-controlled recovery and repeat two real Auth/API account-isolation and write tests on the **secondary** test project.
6. Keep feature flag disabled until tests and device QA pass, and do not publish minors' records.

No production cloud progress writes or identity integration are activated by this note.

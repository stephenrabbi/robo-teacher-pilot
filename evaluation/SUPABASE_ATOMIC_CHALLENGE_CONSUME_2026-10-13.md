# Isolated Supabase atomic enrollment challenge consumption — 2026-10-13

**Secondary project only:** `drzaxpofuhqchmpkwhpy`. Production Supabase and the live classroom were not modified.

Migration `private_atomic_enrollment_consume` creates `robo_test_private.consume_enrollment_challenge(uuid,bytea)`, a SECURITY INVOKER private function using a single conditional UPDATE to set consumed_at for one unexpired, unconsumed challenge matching both verified-account UUID and a 32-byte proof digest. It returns boolean success and does not expose data. PUBLIC, anon and authenticated EXECUTE are revoked; the private schema has no client USAGE privileges. Only a trusted backend with separately verified identity should eventually access this pattern using appropriate narrowly scoped database credentials.

Executed rollback-protected synthetic test (Learners A and B):
- Learner B tries A's valid challenge: false
- Learner A first consumption: true
- Learner A replay: false
- Learner A incorrect proof: false

Subsequent inspection: anon EXECUTE false, authenticated EXECUTE false, zero retained challenge rows. No live user data included.

**Critical:** This is not proof of complete concurrent API behavior or a browser enrollment workflow. It has no secure one-time proof issuer, persistent verified enrollment, network request authorization, account recovery, guardian consent, rate limiting, or two-token authenticated HTTP tests. Backend MUST establish account from independently verified Supabase Auth, never accept a supplied user UUID as ownership proof. Legacy classroom learner code/session must not claim historical records.

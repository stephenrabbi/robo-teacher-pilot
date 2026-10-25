# Restart-safe identity candidate

Status: opt-in candidate, not a production migration.

## Reproduced defect

Legacy coded-learner IDs use the session-signing key. If
`CLASSROOM_SESSION_SECRET` is absent, the generated key changes at process
startup. The same learner code then addresses a different progress owner.
This reproduces the code-level risk; production configuration has not been
verified and reachable storage alone does not establish the cause of missing
historical records.

## Candidate

`CLASSROOM_IDENTITY_MODE=device-key-v2` derives a separately namespaced learner
ID from the existing high-entropy browser learner key and normalized code.
Signing-key rotation invalidates tokens, but not progress ownership. A code
without the device key creates a fresh anonymous identity, not account recovery.
Cross-device recovery still requires the separately verified authenticated
account-binding workflow. Clearing browser storage loses the device identity.

Default remains `legacy` to preserve existing production record lookups.
No credentials, database permissions, or production settings are changed.

## Release gate

1. Enable only on an approved isolated synthetic staging service.
2. Complete practice and verify durable save, restart the service, then verify
   retrieval with the same device key. A second device key must see no records.
3. Verify that the token expires/reissues safely after restart or key rotation.
4. Before production activation, establish a verified ownership-based migration
   for existing records. Never transfer records based on a school code or
   nickname alone. Keep legacy records intact; do not bulk-reassign ownership.
5. Verify durable storage configuration and account recovery separately. This
   candidate does not repair unavailable storage or recover unknown old keys.

Offline regression tests cover key rotation, strict token verification, owner
isolation, code normalization, simulated durable retrieval after cache reset,
and unchanged legacy defaults. They are not a live staging test.

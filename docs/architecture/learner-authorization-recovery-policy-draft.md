# Proposed school authorization and learner recovery operating policy

**DRAFT FOR SCHOOL, GUARDIAN AND PRIVACY REVIEW — NOT AN APPROVED POLICY.** No learner roster, signature, credential or real authorization data should be committed to GitHub.

## Roles and separation of duties

| Role | Proposed authority | Prohibited action |
|---|---|---|
| School head or formally delegated safeguarding officer | Designates approved school enrollment reviewers; can withdraw school participation | Cannot impersonate a learner or bypass guardian process |
| Named school enrollment reviewer | Confirms learner eligibility against school records under an approved procedure and records a bounded decision | Cannot issue learner tokens, view password material, or unilaterally override guardian withdrawal |
| Guardian / applicable lawful representative | Completes documented authorization, receives notice and can request withdrawal under applicable rules | Cannot use another learner's school enrollment |
| Learner | Receives age-appropriate notice/assent process and privately activates a credential | Cannot select a different student's identifier or school |
| Earlyon-Tech restricted operator | Performs audited technical provisioning on independently approved cases | Cannot self-approve reviewer identity, guardian decision, or recovery |
| Independent privacy / safeguarding reviewer | Approves operational policy and incident escalation before rollout | Cannot substitute CI results for legal or safeguarding authorization |

## Evidence required before accepting enrollment

1. Verify school appointment and expiration of the named reviewer independently of the application (for example through the head's documented delegation).
2. Confirm school eligibility using a minimal, pseudonymous learner reference, with no student name stored in this repository.
3. Apply a documented age-specific guardian authorization, learner notice and assent policy; obtain qualified advice on the applicable Nigerian child-data rules before collecting records.
4. Store signed/audited approval references server-side with issuing authority, purpose, school/learner scope, timestamp, expiry, and revocation status. Do not put approval tokens in URLs or browser logs.
5. Require two independent checks — school eligibility and the applicable guardian/learner authorization — before an authenticated operator may provision a credential.
6. Provide a private first-use activation path with expiry, throttling and no arbitrary-subject session issuance.

## Recovery and compromised-device decision

- A recovery request must not reveal whether an enrollment exists; use generic responses and bounded request limits.
- Validate the claimant through an approved out-of-band process. The school reviewer can confirm continued school eligibility, but that **alone is insufficient** to prove the claimant is entitled to the account.
- Require independently reviewed recovery authorization, a short-lived single-use challenge, and a recorded reason (lost phone, lost credential, compromise).
- On successful recovery atomically increase session epoch, revoke all earlier sessions, replace credential, and record a minimally necessary audit event.
- For reported compromise, enable immediate account disable before proceeding. No recovered session is returned until the checks succeed.
- Provide a supervised or offline alternative when a minor has no private device or guardian cannot use an online channel.

## Withdrawal, access and retention

- Define accountable response owners for school withdrawal, guardian requests, suspected misuse and lost devices.
- Immediately deny access following a verified disable action; retention/deletion obligations must be decided, not improvised or equated with immediate physical deletion of backups.
- Log only pseudonymous references, decision IDs, reviewer/operator IDs, action and outcome. Never log learner answers, raw credentials, signing keys, recovery challenges or guardian documents in operational logs.
- Maintain an access request and correction process through appropriate verified representatives; set specific retention periods only after a documented privacy review.

## Decisions requiring explicit external sign-off

| Decision | Proposed owner | Current state |
|---|---|---|
| Participating school and who can appoint reviewers | School leadership | Unconfirmed |
| Applicable guardian authorization and age-specific assent procedure | School safeguarding lead + qualified privacy reviewer | Unconfirmed |
| Organization responsible as data controller and processors | Earlyon-Tech + partner school + privacy reviewer | Unconfirmed |
| Credential recovery second-factor mechanism and accessibility alternatives | School safeguarding lead + technical security reviewer | Unconfirmed |
| Consent withdrawal, retention period, deletion/export response timelines | Responsible data controller + privacy reviewer | Unconfirmed |
| Named operator access, key custody, incident escalation | Earlyon-Tech technical owner + independent reviewer | Unconfirmed |

**Release consequence:** None of these unconfirmed decisions may be treated as completed by a code test, school pilot invitation, or an existing principal letter. Remain NO-GO for public learner identity and progress storage until independent approvals, staging tests and a new reviewed integration PR exist.

# School authorization review and acceptance checklist

**Draft working checklist — no approval implied.** Complete outside GitHub through authorized school and privacy channels. Record only decision status and non-personal reference IDs in this repository; do not commit names, signatures, contact numbers, learner IDs, guardian documents or consent forms.

## School decision record

| Gate | Required evidence (held privately by responsible institution) | Status |
|---|---|---|
| School participation | Signed institutional permission, scope of learner access and designated safeguarding contact | NOT VERIFIED |
| Enrollment reviewers | Appointed reviewers, verification procedure, effective dates, offboarding and independent verification | NOT VERIFIED |
| Learner authorization | Approved age-appropriate notice, guardian/legal basis, assent where applicable, withdrawal mechanism | NOT VERIFIED |
| Technical account creation | Who can grant technical operator privileges, approval separation and audit trail | NOT VERIFIED |
| Account recovery | Independent claimant verification, escalation, emergency disable and device-loss alternatives | NOT VERIFIED |
| Data protection | Controller/processor roles, minimum fields, location/transfers, retention, access/export/deletion | NOT VERIFIED |
| Security operations | Incident response, logs, secrets, personnel access, backups and incident escalation | NOT VERIFIED |
| Staging validation | Synthetic UAT on shared phones, Android Chrome/iOS Safari and intermittent connections | NOT RUN |
| Independent review | Written security, accessibility and safeguarding go/no-go decision | NOT OBTAINED |

## Acceptance scenarios for a separately reviewed staging integration

| ID | Given | When | Required result |
|---|---|---|---|
| E01 | No verified school designation | Operator requests enrollment | Denied; no learner account created |
| E02 | School eligibility but missing applicable guardian/learner authorization | Enrollment requested | Denied without creating a credential |
| E03 | All approvals present but operator unauthenticated | Provisioning requested | Denied and appropriately audited |
| E04 | Correct approved scope | Credential privately activated by learner | Short-lived school-and-subject-scoped session |
| E05 | Learner A authenticated | Requests learner B or different school progress | Denied; no cross-learner data |
| E06 | Known session, then independently approved recovery | Recovery completes | Older sessions immediately rejected on reads and writes |
| E07 | School reviewer appointment expires or revoked | New decision submitted | Denied even if historical approvals exist |
| E08 | Lost/shared device, learner logs out | Another learner opens app | Previous identity, queue and progress not exposed |
| E09 | Failed attempts or account enumeration probes | Repeated login/recovery | Generic responses, rate limits and monitoring |
| E10 | Guardian/school verified withdrawal | Disable requested | New access blocked, existing sessions revoked; retention process initiated |
| E11 | Write in progress while revocation commits | Old token attempts another write | Atomic rejection based on committed epoch |
| E12 | Network interruption, offline retry and DB failure | Learner retries event | No corruption or duplicate; never claim success before commit |
| E13 | Unapproved synthetic API feature toggle | Request sent to production | Route not mounted; zero real-data access |
| E14 | Approved deletion/export request | Authorized operator processes it | Audited policy-compliant action, including backup retention handling |

## Suggested evidence matrix

For each scenario retain: test identifier, environment, anonymized fixture ID, expected and actual result, CI link or private test report, date, reviewer role, disposition. Do not upload actual learner records, screenshots exposing minors, tokens or recovery challenges.

## Review meeting agenda

1. School authority and reviewer appointments
2. Guardian/learner notice, applicable authorization and language accessibility
3. Identity recovery through shared devices and low-connectivity alternatives
4. Data responsibility, retention, withdrawal and incident contacts
5. Read-only review of synthetic staging approach and explicit release exclusions
6. Record unresolved decisions and named institutional owners privately

**Stop condition:** If any mandatory approval remains unverified, no learner identity endpoint or persistent learner-data feature may be activated, merged or deployed.

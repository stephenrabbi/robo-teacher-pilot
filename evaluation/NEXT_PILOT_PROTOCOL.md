# Robo-Teacher Four-Week Pilot Protocol

## Purpose

Run a controlled, staging-first pilot that measures learner engagement, system reliability, safety incidents, and observed Mathematics learning change without collecting unnecessary personal data.

The pilot measures association and observed change. It does not establish that Robo-Teacher alone caused any improvement.

## Pilot structure

| Period | Activity | Evidence produced |
|---|---|---|
| Before week 1 | Confirm consent, assign Pilot IDs, administer Form A | Consent count and baseline score |
| Week 1 | Onboarding and supervised first use | Activation and first-session completion |
| Weeks 2–3 | Independent or teacher-supported use | Active days, completed practice, errors and incidents |
| Week 4 | Final use week, Form B, feedback survey | Post score, learner feedback and retention |

Use a fixed start and end date. Record absences, connectivity problems, timetable disruption, or other conditions that could affect comparison.

## Minimum learner exposure

A learner belongs in the exposure analysis when the learner:

- has a valid Pilot ID;
- completes at least three sessions on at least two different dates; and
- completes at least ten practice questions in total.

Keep all consented participants in the participation report. Do not remove low-use learners to make results look stronger. Report learning outcomes for the matched assessment cohort and engagement outcomes for the active cohort.

## Assessment design

- Use `BASELINE_ASSESSMENT.md` as Form A before access begins.
- Use `POST_ASSESSMENT_FORM_B.md` after the four-week exposure period.
- Allow 30–40 minutes for each assessment.
- Use comparable rooms, instructions and supervision.
- Do not use either assessment as practice material during the pilot.
- Record only Pilot ID, school/class, date, score and administration notes in the evaluation table.

Form B tests the same skills with different numbers and wording. This reduces, but does not eliminate, test familiarity.

## Weekly measures

Record these aggregate measures each week:

| Area | Measures |
|---|---|
| Reach | Consented, onboarded and active learners |
| Engagement | Returning learners, active days, sessions and completed practice questions |
| Learning | Practice accuracy by topic and difficulty; Form A/Form B scores |
| Reliability | Successful requests, errors, median response time and language-switch failures |
| Safety | Incorrect-answer reports, inappropriate responses, personal-data exposure and safeguarding escalations |
| Experience | Short learner feedback and teacher observations |

Define a returning learner as an active learner with valid activity on at least two distinct dates.

## Incident recording

Use `PILOT_INCIDENT_LOG_TEMPLATE.md`. Never enter a learner's name, phone number, username, raw message history, credential or secret. Store any necessary identifying follow-up privately and separately.

Severity definitions:

- **S1 Critical:** personal-data exposure, dangerous guidance, compromised access control, or a serious safeguarding failure.
- **S2 High:** materially incorrect teaching repeated across learners, loss of learner progress, or a core flow unavailable.
- **S3 Moderate:** isolated incorrect explanation, language failure, significant delay, or recoverable session problem.
- **S4 Low:** cosmetic or minor usability problem with a clear workaround.

Pause the affected pilot flow for any S1 incident. Review S2 incidents before the next learner session.

## Staging and release gates

All fixes must pass automated tests and staging UAT before production promotion.

Do not promote when any of these conditions applies:

- an unresolved S1 or S2 incident exists;
- learner identity or contact data appears in a public log or dashboard;
- a core learner flow fails on the representative Android device;
- the assessment or practice score cannot be reproduced from source records; or
- a regression reduces lesson steps, loses progress, or incorrectly marks a valid answer.

## Final analysis

Report:

- consented, onboarded, active and returning learners;
- matched Form A/Form B cohort size;
- mean and median baseline and post scores;
- mean and median percentage-point change;
- counts improved, unchanged and declined;
- results by school/class where groups are large enough for responsible reporting;
- engagement and reliability measures for the exact pilot dates;
- every S1/S2 incident and its resolution status;
- feedback response count and item-level results; and
- limitations, missing data and differences in administration conditions.

Present the full matched cohort first. Any minimum-exposure subgroup is secondary analysis and must be labelled clearly.

## Evidence boundary

Separate all final statements into:

- **Verified result:** reproduced from retained source data or directly observed in testing.
- **User- or teacher-reported result:** reported by a participant but not independently reproduced.
- **Pending verification:** incomplete, missing, or awaiting review.

Do not present plans, targets, demonstrations, or generated test records as pilot outcomes.

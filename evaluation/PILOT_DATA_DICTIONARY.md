# Robo-Teacher Pilot Data Dictionary

Use one randomly assigned `Pilot ID` across the evaluation tables. Keep the separate identity-to-Pilot-ID roster private and access-restricted.

## Participant register

This evaluation register must not contain names, phone numbers, messaging usernames, home addresses, or parent contact details.

| Field | Format | Required | Rule |
|---|---|---:|---|
| Pilot ID | Text | Yes | Random identifier, for example `PILOT-4F8K2` |
| School code | Text | Yes | Approved code, not an improvised school name |
| Class level | Text | Yes | JSS1, JSS2 or JSS3 |
| Consent confirmed | Boolean | Yes | `Yes` only when evidence is retained privately |
| Baseline eligible | Boolean | Yes | Meets inclusion criteria before Form A |
| Onboarding date | Date | No | ISO date: `YYYY-MM-DD` |
| Withdrawal date | Date | No | Blank unless participant withdraws |
| Withdrawal reason code | Text | No | Use a non-identifying category |

## Assessment table

| Field | Format | Required | Rule |
|---|---|---:|---|
| Pilot ID | Text | Yes | Must match participant register |
| Assessment form | Text | Yes | `A` or `B` |
| Assessment date | Date | Yes | Actual administration date |
| Raw score | Integer | Yes | 0–20 |
| Percentage | Number | Yes | `Raw score / 20 × 100` |
| Duration minutes | Integer | No | Actual completion time |
| Conditions code | Text | Yes | `STANDARD` or documented exception code |
| Notes | Text | No | No identifying details |

Reject duplicate Pilot ID plus assessment-form combinations unless the record is explicitly marked as a corrected entry with an audit note.

## Weekly engagement table

| Field | Format | Required | Rule |
|---|---|---:|---|
| Week | Integer | Yes | 1–4 |
| Pilot ID | Text | Yes | Must match participant register |
| Active dates | Integer | Yes | Distinct dates with valid activity during the week |
| Sessions completed | Integer | Yes | Completed learner sessions |
| Practice questions completed | Integer | Yes | Submitted and scored questions |
| Correct practice answers | Integer | Yes | Cannot exceed completed questions |
| Median response time ms | Integer | No | Use successful requests only |
| Errors | Integer | Yes | Technical failures affecting the learner |
| Language switches | Integer | No | Completed language changes |
| Language-switch failures | Integer | No | Failed or destructive changes |

## Feedback table

| Field | Format | Required | Rule |
|---|---|---:|---|
| Pilot ID | Text | Yes | Must match participant register |
| Survey date | Date | Yes | Actual completion date |
| Q1–Q7 | Integer | Yes | Each value must be 1–5 |
| Most helpful | Text | No | Remove identifying details |
| Suggested improvement | Text | No | Remove identifying details |
| Topic helped | Text | No | Curriculum topic only |

## Incident table

Use the fields in `PILOT_INCIDENT_LOG_TEMPLATE.md`. A learner incident may use Pilot ID, but evidence containing raw conversation content must remain private and separately access-controlled.

## Derived measures

- Active learner: at least one valid interaction.
- Returning learner: valid activity on at least two distinct dates.
- Minimum-exposure learner: at least three sessions, two active dates and ten completed practice questions.
- Practice accuracy: correct answers divided by completed questions.
- Matched learner: one valid Form A result and one valid Form B result.
- Percentage-point change: Form B percentage minus Form A percentage.
- Reliability rate: successful requests divided by successful requests plus errors.

## Validation rules

- Never replace missing data with zero.
- Use blank or `NA` for data that was not observed; document which convention is used.
- Keep withdrawn participants in the participation accounting.
- Do not silently correct source records. Retain an audit note.
- Do not upload the private identity roster or raw learner data to the public repository.

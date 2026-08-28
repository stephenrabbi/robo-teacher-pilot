# Robo-Teacher Pilot Evidence Record

This document contains aggregate pilot evidence only. Do not place student names, phone numbers, Telegram usernames, raw student records, consent forms, or credentials in the public repository.

## 1. Pilot identification

| Field | Value |
|---|---|
| Pilot period | August 2026 |
| School 1 | Ise Junior High School, Epe |
| School 2 | Tio College, Ikorodu |
| Planned participants | 56 |
| Actual participants | 56 |
| Consent status | All 56 participants consented |
| Matched pre/post cohort | 56 |
| Completed feedback responses | 56 |

**Pilot-size note:** The original planning target was 20 students (10 per school). The pilot was subsequently expanded to 56 consented students. Final reporting uses the actual participant and analysis counts.

## 2. Product evidence

Keep original screenshots privately. Record or submit only anonymized examples externally.

| Evidence | Status | Notes |
|---|---|---|
| Render health/live deployment | Available | Live pilot service deployed |
| Student onboarding | Available | WhatsApp and Telegram onboarding flow implemented |
| Representative Mathematics interaction | Available | Use anonymized screenshot only |
| Follow-up/context interaction | Available | Use anonymized screenshot only |
| Telegram interaction | Available | Live pilot channel |
| WhatsApp interaction | Available | Live pilot channel |

## 3. Pilot usage metrics

| Metric | Verified value |
|---|---:|
| Students consented | 56 |
| Students in roster | 56 |
| Students with ≥1 logged interaction | 56 |
| Total logged interactions | 176 |
| WhatsApp interactions | 107 |
| Telegram interactions | 69 |
| Average interactions per student | 3.14 |
| Average response latency | 3.28 seconds |

The 176-interaction figure is the aggregate interaction count in the live pilot dataset used for evaluation reporting. Historical development/test records are retained separately and are not part of this figure.

## 4. School breakdown

| School | Students | Logged interactions | Baseline mean | Post-test mean | Gain | Improved |
|---|---:|---:|---:|---:|---:|---:|
| Ise Junior High School, Epe | 25 | 103 | 14.0% | 26.4% | +12.4 pp | 88.0% |
| Tio College, Ikorodu | 31 | 73 | 11.6% | 26.6% | +15.0 pp | 93.5% |

## 5. Learning outcomes

| Metric | Verified result |
|---|---:|
| Completed baseline assessments | 56 |
| Completed post assessments | 56 |
| Students with both tests | 56 |
| Average baseline score | 12.7% |
| Average post-test score | 26.5% |
| Average observed gain | +13.8 percentage points |
| Students improved | 51 of 56 |
| Percentage improved | 91.1% |
| Students not improved | 5 of 56 |

### Topic-level observations

| Topic group | Baseline | Post | Change |
|---|---:|---:|---:|
| Number Operations | 13.1% | 30.4% | +17.3 pp |
| Factors / HCF / LCM | 19.0% | 36.9% | +17.9 pp |
| Fractions / Decimals | 8.9% | 30.4% | +21.4 pp |
| Percentages / Ratio | 17.9% | 32.1% | +14.3 pp |
| Algebra | 0.0% | 17.0% | +17.0 pp |
| Financial Mathematics | 17.9% | 10.7% | -7.1 pp |
| Geometry | 10.7% | 18.5% | +7.7 pp |

Financial Mathematics is a priority improvement area for the next iteration of the tutor.

## 6. Student feedback

| Metric | Verified result |
|---|---:|
| Completed surveys | 56 |
| Response rate | 100% |
| Overall mean feedback score | 4.84 / 5 |

Recurring positive themes included:

- clear, step-by-step explanations;
- simple language and patient support;
- ability to ask questions without embarrassment;
- convenient access through WhatsApp and Telegram;
- help with homework and practice.

Recurring requested improvements included:

- images and visual explanations;
- voice/video support;
- Yoruba/Hausa or other local-language support;
- more practice questions and exam-style exercises;
- progress tracking and scores;
- games/rewards;
- lower-data/offline access;
- stronger personalization and memory.

These qualitative themes are recurring patterns in open-ended responses and are not presented as frequency-ranked counts.

## 7. Reliability and quality review

| Check | Status | Notes/evidence |
|---|---|---|
| Arithmetic verification | Implemented | Deterministic arithmetic guardrail is tested |
| Webhook authentication | Implemented | WhatsApp and Telegram request authentication enabled |
| Pseudonymized interaction logging | Implemented | Interaction log uses Pilot ID rather than names/contact identifiers |
| Identity/interaction separation | Implemented | Private Student Roster is separate from Interaction Log |
| AI limitations documented | Implemented | Public README and responsible-AI notes describe limitations |
| Out-of-scope handling | Implemented/reviewed | Tutor scope and escalation behavior documented |

## 8. Evidence provenance

The authoritative source for reported pilot figures is the private Google Sheet containing the Student Roster, Interaction Log, baseline/post assessments, student feedback, evaluation summary, and pilot-evidence dashboard.

Every competition figure should remain reproducible from retained source data. Raw student-level records, identifiers, and consent documentation should remain private.

## 9. Interpretation boundary

The learning results are descriptive matched pre/post observations. The pilot did not use a randomized control group. Therefore use language such as **“observed improvement during the pilot”**, **“pilot results suggest”**, or **“early evidence of learning improvement”** rather than claiming Robo-Teacher caused the change.

## 10. Final evidence checklist

- [x] Actual participant count verified
- [x] School participation documented
- [x] Consent/permission documentation retained privately
- [x] Interaction metrics calculated
- [x] Baseline scores entered
- [x] Post-assessment scores entered
- [x] Matched pre/post analysis completed
- [x] Feedback responses summarized
- [x] Topic-level analysis completed
- [x] Public repository uses aggregate evidence only
- [x] Application claim boundary documented
- [ ] Final anonymized product screenshots archived/selected for submission
- [ ] Final competition application text completed

# Google AI Lab Competition Evidence Checklist

This checklist defines the evidence package for Robo-Teacher. Store sensitive/raw student data outside the public repository.

## Problem and context

- [x] Short problem statement grounded in the Nigerian classroom context
- [x] Description of target learners and JSS2 Mathematics scope
- [x] Explanation of why WhatsApp/Telegram access matters for the pilot context

## Product evidence

- [x] Live deployment/health-check evidence
- [x] Student onboarding flow implemented and tested
- [x] Representative Mathematics interactions available privately
- [x] Follow-up/contextual interactions available privately
- [x] Telegram pilot evidence available
- [x] WhatsApp pilot evidence available
- [x] GitHub repository available
- [x] Technical architecture/source-code documentation available
- [ ] Final anonymized screenshot set selected for submission

## Final screenshot evidence set

Capture and retain the following screenshots privately. Use only anonymized/redacted versions in an application, pitch deck, public repository, or external submission.

| # | Screenshot | What it proves | Privacy / capture requirement | Suggested filename |
|---|---|---|---|---|
| 1 | Robo-Teacher live deployment / health response | The application is deployed and operational | Show only the public health response; no environment variables, tokens, service-account details, or dashboard secrets | `01_live_deployment.png` |
| 2 | WhatsApp onboarding flow | Students can access Robo-Teacher through a familiar channel and are assigned to the controlled pilot | Hide phone number, profile photo, contact name, and any identifying notification content | `02_whatsapp_onboarding.png` |
| 3 | WhatsApp Mathematics tutoring interaction | Robo-Teacher provides step-by-step Mathematics support in the live channel | Use a representative Mathematics question; hide phone number, name, profile photo, and unrelated chats | `03_whatsapp_math_interaction.png` |
| 4 | Telegram Mathematics tutoring interaction | The same tutor works through Telegram | Hide username, profile image, chat ID, and identifying notifications | `04_telegram_math_interaction.png` |
| 5 | Follow-up / conversational context example | Robo-Teacher supports an iterative tutoring exchange rather than only one-shot answers | Capture a short sequence showing a follow-up question; remove all participant identifiers | `05_followup_context.png` |
| 6 | Student Roster summary | The pilot contains 56 registered participants across two schools | Prefer a cropped summary/count view. Do **not** expose WhatsApp numbers or Telegram usernames. Pilot IDs may be shown only if necessary, but aggregate counts are preferred | `06_student_roster_summary.png` |
| 7 | Interaction Log summary | Real usage was logged across WhatsApp and Telegram | Show aggregate or carefully cropped columns only. Do not expose contact identifiers; avoid publishing raw student questions if they may identify a participant | `07_interaction_log_summary.png` |
| 8 | Pilot Evidence dashboard | The final evidence is reproducible from the evaluation workbook | Show the headline aggregate outcomes: 56 students, 176 interactions, 12.7% baseline, 26.5% post-test, +13.8 percentage points, 91.1% improved, 4.84/5 feedback | `08_pilot_evidence_dashboard.png` |
| 9 | Baseline / post evaluation summary | The project measured learning before and after the pilot | Prefer the aggregate Evaluation Summary rather than student-level answer-entry sheets | `09_learning_evaluation.png` |
| 10 | Student feedback summary | Students completed structured post-pilot feedback | Show aggregate score/count and, if useful, non-identifying summarized themes; do not expose identifiable open-ended responses | `10_student_feedback_summary.png` |
| 11 | GitHub repository / architecture evidence | The project is technically implemented, documented, and reproducible | Capture the README or architecture section; ensure no secrets appear anywhere on screen | `11_github_architecture.png` |

### Minimum submission set

If an application permits only a few images, prioritize these five:

1. `03_whatsapp_math_interaction.png` — demonstrates the product in use.
2. `04_telegram_math_interaction.png` — demonstrates multi-channel access.
3. `08_pilot_evidence_dashboard.png` — demonstrates measured pilot evidence.
4. `09_learning_evaluation.png` — demonstrates the pre/post evaluation design and outcomes.
5. `11_github_architecture.png` — demonstrates technical implementation and responsible documentation.

### Screenshot quality rules

- Crop tightly around the evidence being demonstrated.
- Keep text large enough to read without zooming.
- Do not include phone numbers, student names, Telegram usernames, profile photographs, chat IDs, API keys, environment variables, service-account JSON, webhook secrets, or authentication tokens.
- When an image contains a student interaction, use a genuine pilot interaction only after removing identifying information; do not manufacture a fictional interaction and present it as pilot evidence.
- Keep the original unredacted source privately for provenance when appropriate, but never commit it to the public repository.
- Use a short caption in the application explaining exactly what each screenshot proves.
- Do not use screenshots as a substitute for the underlying quantitative evidence; the private Google Sheet remains the source of record for evaluation figures.

## Pilot evidence

- [x] School participation documented: Ise Junior High School, Epe and Tio College, Ikorodu
- [x] Consent/permission documentation retained privately for all 56 participants
- [x] Number of students in pilot verified: 56
- [x] Students with at least one logged interaction verified: 56
- [x] Total logged interactions verified: 176
- [x] Channel breakdown verified: 107 WhatsApp, 69 Telegram
- [x] School interaction breakdown verified: 103 Ise, 73 Tio
- [x] Average response latency calculated: 3.28 seconds
- [ ] Final returning-student measure documented for submission, if needed
- [ ] Final success-rate metric documented only if the interaction-status definition is validated for the reporting period

## Learning evidence

- [x] Baseline assessment administered
- [x] Baseline results recorded by Pilot ID
- [x] Post-assessment administered after the pilot exposure period
- [x] Matched pre/post analysis completed for 56 students
- [x] Average baseline verified: 12.7%
- [x] Average post-test verified: 26.5%
- [x] Observed average gain verified: +13.8 percentage points
- [x] Students improved verified: 51 of 56 (91.1%)
- [x] Topic-level analysis completed
- [x] Student feedback survey completed by 56 students
- [x] Aggregate feedback verified: 4.84 / 5
- [x] Qualitative feedback themes summarized without identifying students

## Responsible AI and privacy

- [x] Student identity data kept separate from interaction data
- [x] Public repository contains no live student roster/contact identifiers
- [x] Webhook authentication enabled for deployed channels
- [x] AI limitations documented
- [x] Out-of-scope handling documented
- [x] Application claims use only traceable aggregate evidence
- [x] Pre/post results explicitly described as observational rather than causal

## Evidence quality rules

1. Use actual figures from the pilot; do not use targets as results.
2. Anonymize student examples before external publication.
3. Do not publish phone numbers, Telegram usernames, names, or raw student-level records.
4. Distinguish observed usage from measured learning outcomes.
5. Describe pre/post changes as observed pilot changes, not causal proof, unless the study design supports a causal claim.
6. Keep original screenshots and raw exports privately so every reported figure can be verified.
7. Report the 13.8-point gain as **percentage points**, not as a 13.8% relative increase.
8. Treat the 4.84/5 feedback score as student self-report, not as proof of learning impact.

## Recommended final package

1. One-page project summary
2. Technical architecture/appendix
3. Pilot metrics summary
4. Learning evaluation summary
5. Student feedback summary
6. Selected anonymized interaction examples
7. Privacy and responsible-AI note
8. GitHub repository
9. Competition/application narrative using the verified evidence above

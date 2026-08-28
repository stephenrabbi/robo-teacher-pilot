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

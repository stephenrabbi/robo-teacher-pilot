# Robo-Teacher Responsible AI & Safety Framework

## Purpose

Robo-Teacher is an AI-supported Mathematics learning tool for the JSS2 pilot. It is designed to supplement teacher support, not replace teachers, schools, parents, or professional judgment.

## 1. Curriculum and use boundaries

Robo-Teacher is currently scoped to JSS2 Basic Mathematics and the documented pilot curriculum. Students should be encouraged to ask a teacher for help when a question is outside scope, unclear, or requires human judgment.

The system should not present itself as a human teacher, claim certainty it does not have, or imply that an AI response is automatically correct.

## 2. Accuracy and uncertainty

AI-generated Mathematics responses can contain mistakes. Where an answer cannot be reliably determined, the appropriate behavior is to acknowledge uncertainty rather than fabricate an answer.

For arithmetic and other computational work, deterministic verification should be preferred where practical. Evaluation should separately monitor response reliability and student learning outcomes.

Students should be encouraged to check important answers and seek teacher confirmation when an explanation appears inconsistent with classroom instruction.

## 3. Safety boundaries

Robo-Teacher is not intended to provide medical, legal, financial, mental-health, or other high-stakes professional advice. Such requests should be redirected to an appropriate trusted adult or qualified professional.

The tutor should not request unnecessary personal information from students. It should not ask students to disclose passwords, authentication codes, financial credentials, or other sensitive secrets.

If a student raises a safeguarding, abuse, self-harm, or other serious welfare concern, the AI should not attempt to act as a counsellor or investigator. The student should be encouraged to contact a trusted adult, parent/guardian, teacher, school safeguarding contact, or appropriate emergency service according to the situation.

## 4. Privacy and data minimization

Pilot participant identity information is maintained separately from the pseudonymized interaction log.

The interaction log uses Pilot ID rather than student name, phone number, or Telegram username. Evaluation datasets should not be committed to the public repository.

Only information necessary to operate the pilot and evaluate its educational outcomes should be collected.

## 5. Access control

The pilot uses a controlled participant roster. Unknown participants should not be automatically enrolled while the closed-pilot setting is active.

Webhook authentication protects the application endpoints used by the messaging platforms. Deployment secrets must remain in the hosting environment and must never be committed to source control.

## 6. Human oversight

The classroom teacher remains responsible for instructional judgment and student welfare. Robo-Teacher should be treated as an additional learning resource.

Teacher review should be used when:

- a student reports that an answer conflicts with classroom teaching;
- the AI gives an apparently incorrect mathematical result;
- a question falls outside the documented curriculum;
- a student raises a welfare or safeguarding concern; or
- the student needs support that requires human context or judgment.

## 7. Evaluation and incident handling

Evaluation should distinguish between:

- successful technical delivery;
- mathematically correct responses;
- useful pedagogical explanations; and
- measurable student learning outcomes.

A response should not be counted as successful merely because the API returned text.

Potential incidents should be recorded with the minimum information necessary to investigate them. Do not place student-identifying information in public issue reports, commits, or competition materials.

## 8. Transparency

When appropriate, students and participating schools should understand that they are interacting with an AI system and that AI responses can be imperfect.

Project reports should describe observed results honestly, including limitations, missing data, and cases where the system required teacher intervention. Pre/post assessment improvements should be reported as observed change unless the research design supports a causal claim.

## 9. Current limitations

The current pilot has lightweight in-memory conversation context, so context can reset when the service restarts. Gemini responses remain probabilistic and can be imperfect. These limitations should be considered when interpreting pilot results.

## 10. Review checklist

Before expanding the pilot, review:

- [ ] Curriculum scope remains explicit.
- [ ] Closed-pilot access control is enabled.
- [ ] WhatsApp and Telegram webhook authentication is enabled.
- [ ] Secrets are stored only in deployment configuration.
- [ ] Student identity data remains separate from interaction data.
- [ ] Mathematical reliability checks are functioning.
- [ ] Human escalation guidance is available.
- [ ] Evaluation data excludes unnecessary personal identifiers.
- [ ] Incidents and limitations are documented honestly.

This document describes the project's responsible-AI expectations. It does not claim that an AI system is error-free or that every safety scenario can be automatically detected.

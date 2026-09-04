# Robo-Teacher V2

**A Gemini-powered, adaptive and multimodal Mathematics tutor for African learners, built by Earlyon-Tech Brainery.**

Robo-Teacher is an AI tutoring system designed to extend individualized learning support beyond the classroom. The current production release focuses on **JSS2 Basic Mathematics** and combines curriculum-focused tutoring with adaptive learner profiles, text tutoring, homework-image support, voice questions, privacy-conscious analytics, and authenticated messaging integrations.

> **Current status:** Robo-Teacher V2 has been merged into the production `main` branch, passed the automated CI test suite, and is deployed to production on Render.

> **V2.5 staging:** The next interactive classroom release is being validated on the unmerged `v2.5-classroom` branch through draft PR #9. It does not change the production application. [Open the V2.5 staging classroom](https://robo-teacher-v25-staging.onrender.com/classroom-app).

## V2.5 Interactive Classroom — Staging

The browser classroom extends the messaging tutor into one learning workspace while preserving the existing production release. Learners can currently:

- ask typed Mathematics questions and receive step-by-step teaching;
- submit questions using camera capture or image upload;
- record voice questions;
- write problems or show working on an interactive whiteboard with pen, eraser, clear, close and **Ask Teacher** controls;
- learn in English, Yorùbá, Igbo or Hausa across text, voice, image and whiteboard pathways;
- enter questions in the selected Nigerian language and receive the explanation and final-answer wording in that language;
- practise across 11 JSS2 Mathematics topic groups at Easy, Medium or Challenge level;
- choose 5-, 10- or 20-question practice sessions generated with no repeated prompt within a session;
- receive praise for correct answers and a worked explanation after incorrect answers;
- review missed questions, scores, percentages and next-step recommendations; and
- reopen a persistent progress dashboard showing completed sessions, total questions, overall score, topic performance, strongest and focus topics, and recent history.

Browser learners are represented by stable pseudonymous identifiers derived from a device-generated random key. Practice history is stored in a separate **Practice Progress** worksheet; names, phone numbers and email addresses are not required for this feature.

These capabilities have passed controlled automated staging tests. They are product-development results and are not included in the frozen 56-student pilot evidence below.

## Why Robo-Teacher

Large classes can limit the amount of individualized explanation, practice and feedback each learner receives. Robo-Teacher is being developed as an always-available AI learning layer that can provide patient, step-by-step support through channels learners already know how to use.

The long-term product vision is a **multilingual, multimodal AI virtual teacher** that can see, listen, speak, teach, demonstrate, assess and personalize learning across African curricula, subjects and education levels.

## V2 Capabilities

### Adaptive learner profiles

Robo-Teacher maintains a lightweight learner profile keyed by pseudonymous Pilot ID. The profile can track:

- topic interaction counts
- last topic studied
- recent-question context
- preferred explanation style
- difficulty level
- language preference

Recent-question data is minimized before durable storage, including redaction of common email addresses, Nigerian mobile numbers and Telegram handles.

### Step-by-step Mathematics tutoring

The Gemini-powered tutor is prompted to teach rather than simply provide answers. It supports worked explanations, misconception correction, Socratic guidance and multi-turn follow-up within the documented Mathematics scope.

### Homework-image tutoring

Students can submit supported homework images through Telegram. Robo-Teacher can use Gemini's multimodal capability to interpret a readable Mathematics problem and explain it step by step.

Image handling includes download-size limits and defensive processing. If an image is too unclear to interpret reliably, the tutor is designed to request a clearer image rather than inventing the missing content.

### Voice-question tutoring

Students can send supported voice/audio questions through Telegram and receive a text tutoring response. The voice pathway includes instructions to verify important numbers, signs and operators and to ask the learner to resend or type the question when the audio is ambiguous.

### Conversation continuity

The tutor maintains lightweight in-memory conversation history so follow-up questions can retain context during a running session. Conversation history is only updated after a successful model response, helping prevent provider failures from corrupting the active history.

### Safe fallback behaviour

The tutor includes bounded retry and fallback handling for model-provider errors and rate limits. Provider failures do not trigger unlimited retries, and user-facing responses avoid exposing internal technical details.

## Verified Pilot Evidence

The original evaluation involved students from **Ise Junior High School, Epe** and **Tio College, Ikorodu**.

### Frozen evaluation snapshot

- **56 students** participated across the two schools.
- All **56 students completed matched baseline and post-test assessments**.
- Mean Mathematics assessment performance increased from **12.7% at baseline to 26.5% at post-test** — an observed gain of **13.8 percentage points**.
- **51 of 56 students (91.1%)** recorded a higher post-test score than baseline.
- All **56 students completed the feedback survey**.
- Overall mean student-feedback rating: **4.84/5**.
- The frozen evaluation snapshot contains **188 successful student interactions**: **119 WhatsApp** and **69 Telegram**.

These are **descriptive pilot results**. The evaluation did not use a randomized control group, so the pre/post change should be interpreted as **observed improvement during the pilot**, not proof that Robo-Teacher alone caused the improvement.

The pilot evidence remains separate from later V2 development and controlled staging tests. New development activity is not retroactively added to the frozen evaluation dataset.

See `evaluation/PILOT_DASHBOARD.md` and `evaluation/PILOT_EVIDENCE_RECORD.md` for the aggregate evidence record. Student-level results and identifiers remain in private records and are not committed to this public repository.

## Current Architecture

```text
Learner
   |
   v
Telegram / WhatsApp migration path
   |
   v
Authenticated FastAPI webhooks (`main.py`)
   |
   +--> learner identity / roster (`roster_sheet.py`)
   |
   +--> text / image / voice input handling
   |
   v
Tutor orchestrator (`tutor.py`)
   |
   +--> adaptive learner profile (`learner_profile.py`)
   |
   +--> conversation context
   |
   v
Google Gemini
   |
   v
Pedagogical response / safe fallback
   |
   v
Learner response
   |
   v
Pseudonymized analytics (`sheet_logger.py`) --> Google Sheets
```

The production architecture separates participant identity data from pseudonymized interaction records.

The V2.5 staging application adds a browser classroom (`classroom/` and `classroom_api.py`), generated Practice Mode sessions (`practice.py` and `practice_generator.py`), and pseudonymous progress aggregation backed by Google Sheets (`practice_progress.py`).

## Messaging Channels

### Telegram

Telegram is the primary production tutoring channel for the current V2 release. The Telegram webhook supports authenticated text, image and voice/audio interactions.

### WhatsApp

The original pilot used the Twilio WhatsApp Sandbox as well as Telegram. The current production code keeps WhatsApp webhook authentication in place and supports a migration/redirect path rather than silently reactivating unrestricted WhatsApp tutoring.

This distinction is important: the original pilot evidence includes WhatsApp interactions, while current V2 multimodal development is centered on Telegram.

## Curriculum Scope

The production tutor remains deliberately scoped to **JSS2 Basic Mathematics**, aligned with the NERDC scheme of work. Topics include:

- whole numbers and place value
- factors, multiples and prime numbers
- LCM and HCF
- fractions and decimals
- approximation and estimation
- ratio, proportion and rate
- basic algebraic expressions and simple equations
- percentages and everyday arithmetic
- introductory financial Mathematics
- relevant JSS2 geometry

The curriculum and pedagogical instructions are maintained in `tutor.py`.

## Data and Privacy

Robo-Teacher uses **pseudonymization**, not a claim of full anonymity.

The private Student Roster contains the information required to recognize authorized learners. Interaction records use a Pilot ID rather than directly storing a learner's phone number, Telegram username or name.

The interaction log can include:

- UTC timestamp
- school
- Pilot ID
- channel
- session ID
- learner question
- truncated tutor response
- interaction status
- response latency

Because a Pilot ID can be linked back to the separately protected roster, the dataset must be treated as pseudonymized.

Adaptive-memory storage also applies PII-minimization rules to recent-question text before durable storage.

## Security Controls

Current controls include:

- Twilio `X-Twilio-Signature` validation for WhatsApp requests
- Telegram `X-Telegram-Bot-Api-Secret-Token` validation before processing Telegram updates
- webhook-secret format validation
- HTTPS validation for configured Telegram webhook URLs
- safe handling of malformed Telegram updates
- streamed Telegram media downloads with accumulated-byte limits
- sanitized provider/API error logging to reduce credential, URL and payload leakage
- secrets supplied through deployment environment variables rather than committed files
- closed-pilot roster behaviour by default
- separation of production and staging data/configuration

Never commit `.env`, API keys, bot tokens, service-account JSON or other credentials to this repository.

## Automated Testing and CI

The GitHub Actions workflow runs credential-free automated tests using mocks and synthetic data. Current CI coverage includes:

- pilot sanity tests
- adaptive-memory and learner-profile tests
- PII-redaction regression tests
- multimodal/media safety tests
- voice safety tests
- resilience, retry and fallback tests
- conversation-history integrity on provider failure
- Telegram webhook authentication tests
- malformed Telegram update handling

The production V2 merge passed the full automated suite before and after promotion to `main`.

Useful local commands include:

```bash
python test_webhook.py
python test_v2_profile.py
python test_v2_multimodal.py
python test_v2_voice.py
python test_v2_resilience.py
python test_v2_webhook_security.py
```

## Production and Staging

Development and release validation use separate environments:

- `v2-development` was used to isolate V2 development from the original production branch.
- a separate Render staging service and staging Google Sheet were used for controlled V2 validation.
- the tested V2 release was promoted to `main` only after automated tests and staging checks passed.
- Render automatically deploys the production service from `main`.

This workflow reduces the risk of experimental changes directly affecting the live system.

## Getting Started

### Prerequisites

- Python 3
- Gemini API key
- Telegram bot token
- Telegram webhook secret
- Google Sheet and Google service-account credentials
- Twilio credentials if operating the WhatsApp integration
- a Python hosting environment capable of running FastAPI

### Setup

1. Clone the repository.
2. Copy `.env.example` to `.env`.
3. Add the required local environment variables. Do not commit the completed `.env` file.
4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Run the automated tests.
6. Start locally:

```bash
uvicorn main:app --reload
```

For deployment:

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Environment Variables

Use `.env.example` as the configuration template. Relevant variables include:

```env
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.1-flash-lite
GOOGLE_SHEET_ID=
GOOGLE_SERVICE_ACCOUNT_JSON=
TELEGRAM_BOT_TOKEN=
TELEGRAM_WEBHOOK_SECRET=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
ALLOW_AUTO_ENROLL=false
```

Keep `ALLOW_AUTO_ENROLL=false` for a controlled/closed pilot unless there is a deliberate decision to change the enrollment model.

## Repository Components

- `main.py` — FastAPI application, authenticated webhooks and channel flow
- `tutor.py` — Gemini orchestration, curriculum, pedagogy, multimodal prompts and fallback behaviour
- `roster_sheet.py` — Google Sheets-backed learner recognition/onboarding
- `learner_profile.py` — adaptive learner profile and PII-minimized recent-question memory
- `sheet_logger.py` — pseudonymized interaction logging
- `classroom/` — responsive V2.5 browser classroom interface
- `classroom_api.py` — signed browser sessions and classroom endpoints
- `practice.py` — Practice Mode session, marking and review logic
- `practice_generator.py` — varied questions across topics and difficulty levels
- `practice_progress.py` — durable pseudonymous learner-progress records and recommendations
- `v25_app.py` — isolated V2.5 staging entrypoint
- `telegram_adapter.py` — Telegram messaging integration
- `whatsapp_adapter.py` — Twilio WhatsApp integration
- `evaluation/` — pilot instruments, evidence summaries and evaluation documentation
- `.github/workflows/test.yml` — automated CI test workflow

`roster.json` is only a placeholder/example. Live participant records must not be committed to the public repository.

## Known Limitations

Robo-Teacher V2 is a production-deployed early-stage system, not a finished autonomous teacher.

- Conversation history is currently in memory and can reset when the service restarts.
- Adaptive profiles are lightweight and should not be interpreted as a complete learner model.
- Image interpretation depends on image quality and model capability.
- Voice understanding can fail when audio is noisy or numbers/operators are ambiguous.
- Gemini responses can still be imperfect; automated guardrails reduce risk but do not eliminate model error.
- The pilot evaluation was not a randomized controlled trial.
- The original post-test mean of 26.5% remains low in absolute terms despite the observed improvement.
- Financial Mathematics declined in the topic-level pilot analysis and remains an identified improvement area.
- Current production scope is intentionally narrow rather than claiming support for every curriculum, subject or learner level.

## Roadmap

### V2.5 — Interactive AI teacher experience (staging)

Implemented on the draft staging branch:

- interactive teacher/classroom interface
- text, image/camera, voice and whiteboard tutoring
- English, Yorùbá, Igbo and Hausa tutoring
- curriculum-based Practice Mode with varied questions and worked feedback
- session results, missed-question review and learner progress dashboard
- persistent, pseudonymous Practice Mode history in Google Sheets

Before production release, V2.5 still requires broader learner testing, accessibility review, monitoring and a deliberate merge decision.

### V2.6 — School and commercialization layer

Planned work includes:

- school administration tools
- teacher dashboards
- teacher- and school-level learner progress reporting
- expanded evaluation and safeguarding controls
- school-level deployment and pricing workflows
- additional subjects and grade levels

### Longer-term vision

Robo-Teacher is intended to evolve from a messaging-based tutor into an **AI learning layer for African education**: a multilingual, multimodal virtual teacher that can personalize instruction while keeping teachers, schools and responsible evaluation central to deployment.

## Responsible Evidence Policy

This repository distinguishes among:

1. **verified pilot evidence** — results from the documented 56-student evaluation;
2. **controlled development/staging tests** — used to validate new capabilities but not counted as pilot outcomes; and
3. **future product plans** — clearly described as roadmap items rather than completed capabilities.

This distinction is intentional. Robo-Teacher's public claims should remain traceable to evidence rather than treating prototypes, mockups or future plans as completed outcomes.

## About Earlyon-Tech Brainery

Earlyon-Tech Brainery is a Nigerian education-technology initiative focused on expanding access to quality technical and digital education. Robo-Teacher represents the organization's transition from delivering technology-enabled learning primarily through human-led programs toward building scalable AI-powered education infrastructure.

**Product direction:** *Every learner. Their own AI teacher.*

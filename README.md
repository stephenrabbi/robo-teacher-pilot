# Robo-Teacher

*An AI-powered Mathematics tutor for JSS2 students, built by Earlyon-Tech Brainery.*

## About

Robo-Teacher addresses a persistent gap in Nigerian classrooms: large class sizes can limit the individual attention students receive. It provides a patient, always-available Mathematics tutor through platforms students already use — WhatsApp and Telegram.

The pilot is intentionally focused on JSS2 Basic Mathematics and aligned with the NERDC scheme of work. Future expansion can include additional subjects, grade levels, multimedia interactions, and platform integrations.

## Pilot status

Robo-Teacher is a live pilot system used by students from **Ise Junior High School, Epe** and **Tio College, Ikorodu**. The project records pseudonymized interaction evidence for evaluation while keeping participant identity data separate from the interaction log.

### Verified aggregate pilot results

- **56 students** participated across the two schools.
- All **56 students completed matched baseline and post-test assessments**.
- Mean Mathematics assessment performance increased from **12.7% at baseline to 26.5% at post-test**, an observed gain of **13.8 percentage points**.
- **51 of 56 students (91.1%)** recorded a higher post-test score than baseline.
- All **56 students completed the feedback survey**, with an overall mean rating of **4.84/5**.
- The live pilot dataset currently contains **188 logged student interactions** across WhatsApp and Telegram (**119 WhatsApp, 69 Telegram**).

These are descriptive pilot results. Because the evaluation did not use a randomized control group, the pre/post change should be interpreted as **observed improvement during the pilot**, not as proof that Robo-Teacher alone caused the improvement.

See `evaluation/PILOT_DASHBOARD.md` and `evaluation/PILOT_EVIDENCE_RECORD.md` for the aggregate evidence summary. Student-level results remain in private evaluation records and are not committed to this public repository.

## How It Works

When a student sends a Mathematics question, Robo-Teacher:

1. Receives the question through WhatsApp or Telegram.
2. Authenticates the incoming webhook request.
3. Looks up or onboards the participant through the Google Sheets-backed roster.
4. Uses Google's Gemini model to generate a curriculum-focused, step-by-step response.
5. Maintains lightweight conversation context using the anonymous Pilot ID as the memory key.
6. Records pseudonymized pilot interaction data in Google Sheets for evaluation.

Student identity data used for onboarding is kept separately from the interaction log.

## Curriculum Scope

The current tutor covers JSS2 Basic Mathematics, including:

- Whole numbers and place value
- Factors, multiples, and prime numbers
- LCM and HCF
- Fractions and decimals
- Approximation and estimation
- Ratio, proportion, and rate
- Basic algebraic expressions and simple equations
- Everyday arithmetic, including profit, loss, and percentages

The curriculum prompt is maintained in `tutor.py`.

## Architecture

```text
Student
   ↓
WhatsApp / Telegram
   ↓
Authenticated FastAPI webhook (`main.py`)
   ↓
Student lookup / onboarding (`roster_sheet.py`)
   ↓
Gemini tutor (`tutor.py`)
   ↓
Response via WhatsApp / Telegram
   ↓
Pseudonymized interaction log → Google Sheets
```

The Student Roster and Interaction Log are separate. The roster contains the mapping needed to recognize pilot participants, while the interaction log uses the Pilot ID and does not store phone numbers, Telegram usernames, or student names.

## Evaluation

The repository includes an evaluation protocol under `evaluation/`:

- `BASELINE_ASSESSMENT.md` — 20-question JSS2 Mathematics baseline
- `POST_ASSESSMENT.md` — parallel 20-question post-assessment
- `STUDENT_FEEDBACK_SURVEY.md` — structured 1–5 student feedback instrument
- `PILOT_DASHBOARD.md` — verified aggregate pilot results
- `PILOT_EVIDENCE_RECORD.md` — evidence provenance and reporting record
- `ANALYSIS_TEMPLATE.md` — engagement, reliability, learning-gain, and feedback analysis rules
- `TOPIC_CATEGORIES.md` — consistent topic classification for interaction analysis
- `COMPETITION_EVIDENCE_CHECKLIST.md` — evidence package checklist

Student-level results and contact identifiers remain in private pilot records and are not committed to this public repository.

## Getting Started

### Prerequisites

- Gemini API key (Google AI Studio)
- Twilio account with WhatsApp Sandbox access or a production WhatsApp sender
- Telegram bot token from BotFather
- Google Sheet and service account for the pilot roster and interaction log
- Python hosting environment capable of running a FastAPI service

### Setup

1. Clone this repository.
2. Copy `.env.example` to `.env` and fill in the required environment variables.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the automated sanity tests:

```bash
python test_webhook.py
```

5. Start locally:

```bash
uvicorn main:app --reload
```

6. Deploy the service using:

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port $PORT
```

7. Configure the Twilio WhatsApp webhook as:

```text
https://<your-deployed-url>/webhook/whatsapp
```

8. Configure the Telegram webhook at:

```text
https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://<your-deployed-url>/webhook/telegram
```

## Security

The WhatsApp webhook validates Twilio's `X-Twilio-Signature` using `TWILIO_AUTH_TOKEN`.

The Telegram webhook validates `X-Telegram-Bot-Api-Secret-Token` using `TELEGRAM_WEBHOOK_SECRET`.

These secrets belong in the deployment environment and must never be committed to the repository. The automated test suite includes both valid-authentication and rejection-path checks.

## Configuration

- `tutor.py` — Gemini model, tutor behaviour, curriculum scope, and conversation context
- `roster_sheet.py` — student onboarding and Google Sheets roster management
- `sheet_logger.py` — privacy-conscious interaction logging
- `whatsapp_adapter.py` — Twilio WhatsApp responses
- `telegram_adapter.py` — Telegram responses
- `main.py` — authenticated FastAPI webhooks and application flow

`roster.json` remains as a placeholder/example file only. Live pilot participant data should be maintained in the private Google Sheet, not committed to this public repository.

## Environment Variables

Use `.env.example` as the template. **Never commit `.env` or service-account credentials to GitHub.** The repository includes a `.gitignore` to help prevent accidental commits of local secrets.

## Data & Privacy

Robo-Teacher uses a pseudonymization model for pilot evaluation. Participant identity data is kept separately from interaction data.

The private **Student Roster** contains the information required to onboard and recognize pilot participants. The **Interaction Log** stores:

- UTC timestamp
- school
- anonymous Pilot ID
- channel
- session ID
- student question
- tutor response (truncated)
- interaction status
- response latency

The interaction log does **not** store phone numbers, Telegram usernames, or student names. Because the Pilot ID can be linked back to the private roster, the interaction dataset should be treated as **pseudonymized rather than fully anonymous**.

## Testing

`test_webhook.py` runs without live API credentials. It uses mocked Gemini, Google Sheets, WhatsApp, and Telegram components to test onboarding, registration, normal tutoring requests, empty-message handling, and webhook authentication/rejection paths.

## Limitations

- The pilot uses lightweight in-memory conversation context, which resets when the server restarts.
- The current evaluation is a pilot and should not be presented as a controlled causal study unless the study design supports that claim.
- WhatsApp availability depends on the selected Twilio/WhatsApp service configuration.
- Gemini responses can be imperfect; the tutor is scoped to the documented JSS2 Mathematics topics and encourages students to seek teacher support when appropriate.
- Financial Mathematics showed weaker post-test performance than baseline in the topic-level analysis and is a priority area for improvement.

## Roadmap

- Additional subjects and grade levels
- Richer multimedia tutoring
- AI voice and video experiences
- Local-language support
- Adaptive practice and progress tracking
- Low-data/offline-friendly access
- Deeper Google Cloud integration
- Expanded school-level reporting and learning analytics

## About Earlyon-Tech Brainery

Earlyon-Tech Brainery is a technology training and product initiative focused on expanding access to quality technical and digital education across Africa. Robo-Teacher applies that mission directly to classroom learning.

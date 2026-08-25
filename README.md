# Robo-Teacher

*An AI-powered Mathematics tutor for JSS2 students, built by Earlyon-Tech Brainery.*

## About

Robo-Teacher addresses a persistent gap in Nigerian classrooms: large class sizes can limit the individual attention students receive. It provides a patient, always-available Mathematics tutor through platforms students already use — WhatsApp and Telegram.

This pilot is intentionally focused on JSS2 Basic Mathematics and is aligned with the NERDC scheme of work. Future expansion can include additional subjects, grade levels, multimedia interactions, and platform integrations.

## How It Works

When a student sends a Mathematics question, Robo-Teacher:

1. Receives the question through WhatsApp or Telegram.
2. Uses Google's Gemini model to generate a curriculum-focused, step-by-step response.
3. Maintains lightweight conversation context for follow-up questions.
4. Records anonymized pilot interaction data in Google Sheets for evaluation.

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
FastAPI webhook (`main.py`)
   ↓
Student lookup / onboarding (`roster_sheet.py`)
   ↓
Gemini tutor (`tutor.py`)
   ↓
Response via WhatsApp / Telegram
   ↓
Anonymous interaction log → Google Sheets
```

The Student Roster and Interaction Log are separate. The roster contains the mapping needed to identify pilot participants, while the interaction log uses the anonymous Pilot ID and does not store phone numbers, Telegram usernames, or student names.

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

### Configuration

- `tutor.py` — Gemini model, tutor behaviour, curriculum scope, and conversation context
- `roster_sheet.py` — student onboarding and Google Sheets roster management
- `sheet_logger.py` — privacy-conscious interaction logging
- `whatsapp_adapter.py` — Twilio WhatsApp responses
- `telegram_adapter.py` — Telegram responses
- `main.py` — FastAPI webhooks and application flow

`roster.json` remains as a placeholder/example file only. Live pilot participant data should be maintained in the private Google Sheet, not committed to this public repository.

## Environment Variables

Use `.env.example` as the template. **Never commit `.env` or service-account credentials to GitHub.** The repository includes a `.gitignore` to help prevent accidental commits of local secrets.

## Data & Privacy

Robo-Teacher separates participant identity data from interaction data.

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

The interaction log does **not** store phone numbers, Telegram usernames, or student names. This separation reduces unnecessary exposure of personally identifiable information about student participants.

## Testing

`test_webhook.py` runs without live API credentials. It uses mocked Gemini, Google Sheets, WhatsApp, and Telegram components to test onboarding, registration, normal tutoring requests, and empty-message handling.

## Roadmap

- Additional subjects and grade levels
- Richer multimedia tutoring
- AI voice and video experiences
- Deeper Google Cloud integration
- Expanded school-level reporting and learning analytics

## About Earlyon-Tech Brainery

Earlyon-Tech Brainery is a technology training and product initiative focused on expanding access to quality technical and digital education across Africa. Robo-Teacher applies that mission directly to classroom learning.

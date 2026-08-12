# Robo-Teacher

*An AI-powered Mathematics tutor for JSS2 students, built by Earlyon-Tech Brainery.*

## About

Robo-Teacher exists to close a simple but persistent gap in Nigerian classrooms: not every student gets enough one-on-one attention to fully grasp a Maths concept before the class moves on. Built by Earlyon-Tech Brainery, an EdTech company committed to strengthening technical and academic education across Africa, Robo-Teacher brings a patient, always-available Maths tutor directly to students on the platforms they already use every day — WhatsApp and Telegram.

This first release is a focused, curriculum-aligned tutor for JSS2 Basic Mathematics, aligned with the NERDC scheme of work. It is intentionally scoped to do one thing well before expanding — additional subjects, richer multimedia interactions, and deeper platform integrations are part of the roadmap ahead.

## Why Robo-Teacher

- Large class sizes across many Nigerian secondary schools limit how much individual attention any one student can receive.
- Students who need extra help outside class hours often have limited access to affordable, reliable tutoring.
- Today's students are already comfortable communicating on WhatsApp and Telegram — meeting them there removes a barrier to actually asking for help.

Robo-Teacher offers step-by-step, encouraging guidance rather than just answers, aiming to build genuine understanding rather than dependency.

## How It Works

Robo-Teacher runs as a lightweight service connected to WhatsApp and Telegram. When a student sends a Maths question, the tutor:

1. Understands the question in context, remembering recent conversation so follow-up questions feel natural.
2. Responds with a step-by-step explanation grounded in the JSS2 curriculum.
3. Logs anonymized usage data — never full contact details — to support ongoing improvement.

Robo-Teacher is built on Google's Gemini models, with student privacy treated as a first-class design constraint rather than an afterthought.

## Curriculum Scope

The current release covers JSS2 Basic Mathematics, First Term, aligned with the NERDC scheme of work, including:

- Whole numbers and place value
- Factors, multiples, and prime numbers
- LCM and HCF
- Fractions and decimals
- Approximation and estimation
- Ratio, proportion, and rate
- Basic algebraic expressions and simple equations
- Everyday arithmetic (profit, loss, and percentages)

Educators adopting Robo-Teacher in their own classrooms should review `tutor.py` and adjust the topic list to match their school's specific scheme of work.

## Getting Started

### Prerequisites

- A Gemini API key (Google AI Studio)
- A Twilio account with WhatsApp Sandbox access (or a registered WhatsApp sender for production use)
- A Telegram bot token (via @BotFather)
- A Google Sheet and service account for usage logging
- A hosting environment capable of running a Python web service

### Setup

1. Clone this repository.
2. Copy `.env.example` to `.env` and fill in your credentials.
3. Install dependencies: `pip install -r requirements.txt`
4. Run the test suite: `python test_webhook.py`
5. Start the service locally: `uvicorn main:app --reload`
6. Deploy using:
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
7. Connect WhatsApp: in the Twilio Console, set the Sandbox's inbound webhook to `https://<your-deployed-url>/webhook/whatsapp`.
8. Connect Telegram: visit `https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://<your-deployed-url>/webhook/telegram` once in a browser.

### Configuration

- `tutor.py` — curriculum scope and tutor personality
- `roster.json` — maps participants to their school for usage reporting
- `sheet_logger.py` — privacy-conscious usage logging

## Data & Privacy

Robo-Teacher is designed with student privacy as a first principle. Interaction logs store only the last four digits of a student's contact identifier — never a full phone number or name — alongside the question, response, and timestamp. This is a deliberate choice: enough signal to understand usage and impact, without retaining identifying information about minors.

## Testing

A lightweight test suite (`test_webhook.py`) verifies the request and response logic for both WhatsApp and Telegram without requiring live API credentials — useful for quick verification after any code change.

## Roadmap

- Additional subjects and grade levels beyond JSS2 Basic Mathematics
- An AI avatar with voice and video for a more immersive tutoring experience
- Deeper integration with Google Cloud (Vertex AI, Firebase) as usage scales
- Expanded reporting and analytics for participating schools

## About Earlyon-Tech Brainery

Earlyon-Tech Brainery is a Lagos-based technology training and product company dedicated to expanding access to quality technical and digital education across Africa. Robo-Teacher reflects that mission applied directly to the classroom.

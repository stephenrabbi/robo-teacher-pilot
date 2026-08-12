# Robo-Teacher — WhatsApp Pilot Bot (JSS2 Basic Maths)

A lean, working WhatsApp tutor built on Gemini, scoped to JSS2 Basic Maths, for
a 2-school pilot ahead of the Google Africa Applied AI Lab application
(deadline: **August 31, 2026**).

This is deliberately minimal — text only, one subject, no avatar, no video,
no Firebase/Vertex AI enterprise setup. Get it live and in front of real
students first. Everything richer (avatar, Telegram, more subjects, full
Google Cloud stack) is a fast-follow once this works and you have data.

## What you need to create (none of this can be done for you — these require
your own accounts)

1. **A Gemini API key** — go to https://aistudio.google.com/apikey, sign in
   with a Google account, click "Create API key". Takes about 2 minutes.
2. **A Twilio account** — sign up free at https://www.twilio.com/try-twilio.
   In the Twilio Console, go to **Messaging → Try it out → Send a WhatsApp
   message** to activate your WhatsApp Sandbox. You'll get:
   - A sandbox number (e.g. `+1 415 523 8886`)
   - A join code (e.g. `join sunny-tiger`)
   Every pilot student/teacher must send that join message once from their
   own WhatsApp to the sandbox number before the bot can message them. This
   is Twilio's anti-spam requirement for sandbox mode — plan a 5-minute
   "everyone send this message" moment when you onboard each school.
3. **A Google Sheet for pilot data**:
   - Create a new Google Sheet (this becomes your data source for the
     application — usage counts, sample questions, engagement over time).
   - In Google Cloud Console (https://console.cloud.google.com), create a
     project, enable the **Google Sheets API**.
   - Create a **Service Account** (IAM & Admin → Service Accounts → Create),
     then create a JSON key for it and download it.
   - Open the downloaded JSON, copy the `client_email` field, and **share
     your Google Sheet with that email address** as an Editor.
   - Copy the Sheet ID from its URL (the long string between `/d/` and
     `/edit`).
4. **A place to host it** — I'd recommend **Render** (https://render.com) for
   speed: free tier, connects directly to a GitHub repo, live URL in
   minutes. Steps:
   - Push this folder to a new GitHub repo.
   - On Render: New → Web Service → connect the repo.
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Add the environment variables from `.env.example` in Render's
     dashboard (paste your real Gemini key, Sheet ID, and the full service
     account JSON as one line into `GOOGLE_SERVICE_ACCOUNT_JSON`).
   - Deploy. You'll get a public URL like `https://robo-teacher-xxxx.onrender.com`.

   Note: Render's free tier sleeps after inactivity and takes ~30-60s to
   wake on the next message — fine for a pilot, just expect the first
   message of the day to feel slow. If that's a problem, their $7/mo tier
   removes it.

## Setting up Telegram (no phone verification gate — good fallback if Twilio blocks you)

1. Open Telegram, search for **@BotFather**, and start a chat with it.
2. Send `/newbot`, give it a name (e.g. "Robo-Teacher") and a username ending in `bot` (e.g. `robo_teacher_pilot_bot`).
3. BotFather replies with a **token** — copy it into `.env` as `TELEGRAM_BOT_TOKEN`.
4. Once deployed (see below), tell Telegram where to send messages by visiting this URL once in your browser (replace both placeholders):
   ```
   https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://your-app-name.onrender.com/webhook/telegram
   ```
   You should see `{"ok":true,"result":true,...}`.
5. Message your bot directly on Telegram to test it.
6. To find a student's chat ID (for `roster.json`), have them message the bot once, then check the latest row in your Google Sheet — their masked ID is logged there.

## Wiring Twilio to your deployed bot

In the Twilio Console, under your WhatsApp Sandbox settings, set
**"When a message comes in"** to:

```
https://your-app-name.onrender.com/webhook/whatsapp
```

Method: `HTTP POST`. Save. That's it — messages sent to the sandbox number
now reach your bot.

## Before the pilot goes live

- [ ] Open `tutor.py` and check `CURRICULUM_TOPICS` against your school's
      actual JSS2 Maths scheme of work — edit the list to match.
- [ ] Open `roster.json` and replace the placeholder numbers with your real
      pilot students' WhatsApp numbers (with country code, digits only),
      mapped to `"School A"` / `"School B"` (or real school names) — this is
      what lets your pilot data be broken down by school.
- [ ] Get informal sign-off from each school's administration.
- [ ] Have every pilot participant send the Twilio join code once.
- [ ] Send yourself a few test questions first and read the replies for
      accuracy before students start using it.

## Running locally to test before deploying

```bash
cp .env.example .env   # fill in your real keys
pip install -r requirements.txt
python test_webhook.py        # sanity check, no API keys needed
uvicorn main:app --reload     # starts a local server on :8000
```

To test against real WhatsApp before deploying, use a tunnel tool like
`ngrok` (`ngrok http 8000`) and point Twilio's sandbox webhook at the
ngrok URL temporarily.

## What's intentionally NOT in this version (roadmap, not now)

- Telegram bot (easy to add later — same tutor logic, a second thin adapter)
- Voice notes / AI avatar video
- Full Google Cloud stack (Vertex AI, Firebase Auth, Cloud Monitoring)
- Multiple subjects/grade levels

These are the "future roadmap" items worth one line each in the Google Lab
application, not things to build before the pilot.

## Pulling data for the application

Everything logged to your Google Sheet (timestamp, school, masked student
ref, question, reply, latency) is your raw pilot evidence. Before writing
the application, pull from it: total interactions, unique students engaged,
interactions per school, and a handful of real (anonymized) example
exchanges that show the tutor working well.

"""One-shot live smoke test of the public preview; uses a synthetic JSS2 learner."""
import json
import os
import re
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

BASE = "https://robo-teacher-pitch-ui-preview.onrender.com"
QUESTION = "What is 3/4 + 1/8? Explain each step."

def post(path, payload, timeout):
    body = json.dumps(payload).encode("utf-8")
    request = Request(BASE + path, data=body, headers={
        "Content-Type": "application/json", "User-Agent": "RoboTeacher-Synthetic-CI/1.0"
    }, method="POST")
    with urlopen(request, timeout=timeout) as response:
        return response.status, json.load(response)

def main():
    try:
        status, session = post("/api/classroom/session",
            {"nickname": "Synthetic-Maths-QA", "class_level": "JSS2"}, 35)
        token = session.get("session_token")
        if status != 200 or not token:
            raise ValueError("The synthetic session was not issued")
        print("Synthetic JSS2 session: OK")
        status, answer = post("/api/classroom/chat",
            {"session_token": token, "message": QUESTION, "language": "English"}, 100)
        reply = str(answer.get("reply", ""))
        print("Maths chat HTTP status:", status)
        print("Reply received:", bool(reply.strip()))
        print("Reply length:", len(reply))
        print("Reported latency (seconds):", answer.get("latency_seconds"))
        correct = bool(re.search(r"(?<!\\d)7\\s*/\\s*8(?!\\d)", reply)
                       or re.search(r"(?<!\\d)0\\.875(?!\\d)", reply))
        print("Contains correct answer 7/8 or 0.875:", correct)
        print("Explains equivalent eighths:", any(x in reply.replace(" ", "") for x in ("6/8", "6⁄8")))
        if status != 200 or not reply.strip() or not correct:
            raise ValueError("The live tutoring response needs review")
    except HTTPError as exc:
        print("Live API returned HTTP", exc.code)
        sys.exit(1)
    except (URLError, TimeoutError, ValueError) as exc:
        print("Live Maths smoke test failed:", type(exc).__name__, str(exc)[:160])
        sys.exit(1)

if __name__ == "__main__":
    main()

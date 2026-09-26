#!/usr/bin/env python3
"""Staging-only synthetic learner runner for Robo-Teacher.

Default mode is dry-run. Pass --live to send synthetic requests to staging.
No real learner data is required or permitted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib import error, request

HERE = Path(__file__).resolve().parent
PERSONAS_PATH = HERE / "personas.json"
MATRIX_PATH = HERE / "test_matrix.json"
RESULTS_DIR = HERE / "results"
DEFAULT_BASE_URL = "https://robo-teacher-v25-staging.onrender.com"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def post_json(url: str, payload: dict, timeout: int = 60) -> tuple[int, dict, float]:
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "User-Agent": "robo-teacher-synthetic-lab/1.0"},
        method="POST",
    )
    start = time.perf_counter()
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            elapsed = time.perf_counter() - start
            return resp.status, json.loads(raw), elapsed
    except error.HTTPError as exc:
        elapsed = time.perf_counter() - start
        try:
            payload = json.loads(exc.read().decode("utf-8"))
        except Exception:
            payload = {"detail": str(exc)}
        return exc.code, payload, elapsed


def synthetic_learner_key(persona_id: str) -> str:
    # API requires a 32-64 lowercase hex key; this is deterministic and contains no PII.
    return hashlib.sha256(f"synthetic-lab-v1:{persona_id}".encode()).hexdigest()


def choose_language(persona: dict, interaction_type: str) -> str:
    if interaction_type == "language_context_challenge":
        return persona.get("secondary_language") or persona["preferred_language"]
    return persona["preferred_language"]


def build_cases(personas: list[dict], matrix: dict) -> list[dict]:
    cases = []
    for persona in personas:
        for topic in matrix["topics"]:
            for interaction in matrix["interaction_types"]:
                cases.append({
                    "persona": persona,
                    "topic": topic,
                    "interaction": interaction,
                    "language": choose_language(persona, interaction["id"]),
                })
    return cases


def make_prompt(case: dict) -> str:
    p = case["persona"]
    t = case["topic"]
    i = case["interaction"]
    context = (
        f"Synthetic learner profile for this test only: class {p['class_level']}; "
        f"ability {p['ability']}; confidence {p['confidence']}; "
        f"known misconception: {p['misconception']}. "
    )
    if i["id"] == "correct_path":
        return context + t["base_prompt"]
    return context + t["base_prompt"] + " " + i["follow_up"]


def run_case(base_url: str, case: dict) -> dict:
    persona = case["persona"]
    session_payload = {
        "learner_key": synthetic_learner_key(persona["persona_id"]),
        "nickname": persona["persona_id"],
        "class_level": persona["class_level"],
    }
    s_status, s_body, s_elapsed = post_json(f"{base_url}/api/classroom/session", session_payload)
    if s_status != 200 or "session_token" not in s_body:
        return {
            "status": "session_error",
            "session_http": s_status,
            "session_body": s_body,
            "session_wall_seconds": round(s_elapsed, 3),
        }

    chat_payload = {
        "message": make_prompt(case),
        "session_token": s_body["session_token"],
        "language": case["language"],
    }
    c_status, c_body, c_elapsed = post_json(f"{base_url}/api/classroom/chat", chat_payload)
    reply = str(c_body.get("reply", "")) if isinstance(c_body, dict) else ""
    return {
        "status": "ok" if c_status == 200 else "chat_error",
        "chat_http": c_status,
        "wall_seconds": round(c_elapsed, 3),
        "reported_latency_seconds": c_body.get("latency_seconds") if isinstance(c_body, dict) else None,
        "reply_chars": len(reply),
        "escalated": reply.startswith("[ESCALATE]"),
        "reply": reply,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Actually call the staging API.")
    parser.add_argument("--full", action="store_true", help="Run all 240 planned cases.")
    parser.add_argument("--max-cases", type=int, default=12, help="Maximum cases for a live smoke run.")
    parser.add_argument("--delay", type=float, default=5.5, help="Delay between live chat cases to respect tutor rate limits.")
    args = parser.parse_args()

    data = load_json(PERSONAS_PATH)
    matrix = load_json(MATRIX_PATH)
    cases = build_cases(data["personas"], matrix)

    if not args.full:
        cases = cases[: max(1, args.max_cases)]

    summary = {
        "mode": "live" if args.live else "dry-run",
        "planned_cases_this_run": len(cases),
        "full_design_cases": 12 * 5 * 4,
        "base_url": os.getenv("ROBO_TEACHER_BASE_URL", DEFAULT_BASE_URL),
    }
    print(json.dumps(summary, indent=2))

    if not args.live:
        for idx, case in enumerate(cases[:5], start=1):
            print(f"{idx:02d}. {case['persona']['persona_id']} | {case['topic']['id']} | {case['interaction']['id']} | {case['language']}")
        print("Dry-run complete. Add --live to call staging.")
        return 0

    base_url = os.getenv("ROBO_TEACHER_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    if "staging" not in base_url.lower():
        raise SystemExit("Refusing live run: base URL does not look like staging.")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = RESULTS_DIR / f"synthetic_run_{stamp}.jsonl"

    previous_reply_by_persona: dict[str, str] = {}
    with output_path.open("w", encoding="utf-8") as out:
        for idx, case in enumerate(cases, start=1):
            persona_id = case["persona"]["persona_id"]
            result = run_case(base_url, case)
            normalized_reply = " ".join(str(result.get("reply", "")).lower().split())
            repeated = bool(normalized_reply and previous_reply_by_persona.get(persona_id) == normalized_reply)
            previous_reply_by_persona[persona_id] = normalized_reply
            row = {
                "run_index": idx,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "persona_id": persona_id,
                "class_level": case["persona"]["class_level"],
                "topic": case["topic"]["id"],
                "interaction_type": case["interaction"]["id"],
                "language": case["language"],
                "possible_adjacent_repeat": repeated,
                **result,
            }
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            print(f"[{idx}/{len(cases)}] {persona_id} {case['topic']['id']} {case['interaction']['id']}: {row['status']}")
            if idx < len(cases):
                time.sleep(max(0.0, args.delay))

    print(f"Results written to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Staging-only synthetic learner runner for Robo-Teacher.

Default mode is dry-run. Pass --live to send synthetic requests to staging.
No real learner data is required or permitted.

Each scenario uses a fresh synthetic learner key so test conversations are isolated.
Multi-turn scenarios deliberately reuse the same classroom session within that scenario.
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


def post_json(url: str, payload: dict, timeout: int = 90) -> tuple[int, dict, float]:
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "User-Agent": "robo-teacher-synthetic-lab/1.1"},
        method="POST",
    )
    start = time.perf_counter()
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw), time.perf_counter() - start
    except error.HTTPError as exc:
        try:
            payload = json.loads(exc.read().decode("utf-8"))
        except Exception:
            payload = {"detail": str(exc)}
        return exc.code, payload, time.perf_counter() - start


def synthetic_learner_key(persona_id: str, topic_id: str, interaction_id: str) -> str:
    seed = f"synthetic-lab-v1:{persona_id}:{topic_id}:{interaction_id}"
    return hashlib.sha256(seed.encode()).hexdigest()


def scenario_turns(case: dict) -> list[dict]:
    persona = case["persona"]
    topic = case["topic"]
    interaction_id = case["interaction"]["id"]
    primary = persona["preferred_language"]
    secondary = persona.get("secondary_language") or primary

    first = {
        "language": primary,
        "message": topic["base_prompt"],
        "purpose": "initial_explanation",
    }

    if interaction_id == "correct_path":
        return [
            first,
            {
                "language": primary,
                "message": "I understand. Give me one similar question to try, but do not give the answer yet.",
                "purpose": "normal_follow_up",
            },
        ]

    if interaction_id == "wrong_answer":
        return [
            first,
            {
                "language": primary,
                "message": case["interaction"]["follow_up"],
                "purpose": "misconception_correction",
            },
        ]

    if interaction_id == "repeated_wrong_answer":
        return [
            first,
            {
                "language": primary,
                "message": "I think the answer is 12. Please check my thinking and teach me where I went wrong.",
                "purpose": "first_wrong_answer",
            },
            {
                "language": primary,
                "message": case["interaction"]["follow_up"],
                "purpose": "reteach_after_repeated_error",
            },
        ]

    if interaction_id == "language_context_challenge":
        return [
            first,
            {
                "language": secondary,
                "message": case["interaction"]["follow_up"],
                "purpose": "language_switch_context_retention",
            },
        ]

    raise ValueError(f"Unknown interaction type: {interaction_id}")


def build_cases(personas: list[dict], matrix: dict) -> list[dict]:
    cases = []
    for persona in personas:
        for topic in matrix["topics"]:
            for interaction in matrix["interaction_types"]:
                cases.append({"persona": persona, "topic": topic, "interaction": interaction})
    return cases


def create_session(base_url: str, case: dict) -> tuple[int, dict, float]:
    persona = case["persona"]
    payload = {
        "learner_key": synthetic_learner_key(
            persona["persona_id"], case["topic"]["id"], case["interaction"]["id"]
        ),
        "nickname": persona["persona_id"],
        "class_level": persona["class_level"],
    }
    return post_json(f"{base_url}/api/classroom/session", payload)


def run_scenario(base_url: str, case: dict, turn_delay: float) -> dict:
    s_status, s_body, s_elapsed = create_session(base_url, case)
    if s_status != 200 or "session_token" not in s_body:
        return {
            "scenario_status": "session_error",
            "session_http": s_status,
            "session_body": s_body,
            "session_wall_seconds": round(s_elapsed, 3),
            "turns": [],
        }

    token = s_body["session_token"]
    turns = []
    previous_normalized = ""

    for turn_index, scripted in enumerate(scenario_turns(case), start=1):
        payload = {
            "message": scripted["message"],
            "session_token": token,
            "language": scripted["language"],
        }
        status, body, elapsed = post_json(f"{base_url}/api/classroom/chat", payload)
        reply = str(body.get("reply", "")) if isinstance(body, dict) else ""
        normalized = " ".join(reply.lower().split())
        turns.append({
            "turn": turn_index,
            "purpose": scripted["purpose"],
            "language": scripted["language"],
            "prompt": scripted["message"],
            "http_status": status,
            "status": "ok" if status == 200 else "error",
            "wall_seconds": round(elapsed, 3),
            "reported_latency_seconds": body.get("latency_seconds") if isinstance(body, dict) else None,
            "reply_chars": len(reply),
            "escalated": reply.startswith("[ESCALATE]"),
            "possible_adjacent_repeat": bool(normalized and normalized == previous_normalized),
            "reply": reply,
        })
        previous_normalized = normalized

        if turn_index < len(scenario_turns(case)):
            time.sleep(max(0.0, turn_delay))

    scenario_status = "ok" if all(t["status"] == "ok" for t in turns) else "chat_error"
    return {"scenario_status": scenario_status, "turns": turns}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Actually call the staging API.")
    parser.add_argument("--full", action="store_true", help="Run all 240 planned scenarios.")
    parser.add_argument("--max-cases", type=int, default=12, help="Maximum scenarios for a live smoke run.")
    parser.add_argument("--delay", type=float, default=5.5, help="Delay between tutor turns to respect staging rate limits.")
    args = parser.parse_args()

    data = load_json(PERSONAS_PATH)
    matrix = load_json(MATRIX_PATH)
    cases = build_cases(data["personas"], matrix)
    if not args.full:
        cases = cases[: max(1, args.max_cases)]

    total_turns = sum(len(scenario_turns(case)) for case in cases)
    summary = {
        "mode": "live" if args.live else "dry-run",
        "planned_scenarios_this_run": len(cases),
        "planned_tutor_turns_this_run": total_turns,
        "full_design_scenarios": 12 * 5 * 4,
        "base_url": os.getenv("ROBO_TEACHER_BASE_URL", DEFAULT_BASE_URL),
    }
    print(json.dumps(summary, indent=2))

    if not args.live:
        for idx, case in enumerate(cases[:5], start=1):
            print(
                f"{idx:02d}. {case['persona']['persona_id']} | "
                f"{case['topic']['id']} | {case['interaction']['id']} | "
                f"{len(scenario_turns(case))} turns"
            )
        print("Dry-run complete. Add --live to call staging.")
        return 0

    base_url = os.getenv("ROBO_TEACHER_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    if "staging" not in base_url.lower():
        raise SystemExit("Refusing live run: base URL does not look like staging.")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = RESULTS_DIR / f"synthetic_run_{stamp}.jsonl"

    with output_path.open("w", encoding="utf-8") as out:
        for idx, case in enumerate(cases, start=1):
            result = run_scenario(base_url, case, args.delay)
            row = {
                "scenario_index": idx,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "persona_id": case["persona"]["persona_id"],
                "class_level": case["persona"]["class_level"],
                "topic": case["topic"]["id"],
                "interaction_type": case["interaction"]["id"],
                **result,
            }
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
            print(
                f"[{idx}/{len(cases)}] {row['persona_id']} "
                f"{row['topic']} {row['interaction_type']}: {row['scenario_status']}"
            )
            if idx < len(cases):
                time.sleep(max(0.0, args.delay))

    print(f"Results written to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Read-only check of the dedicated Robo-Teacher Supabase project.

No database writes or student data are accessed. An API key must be supplied
as an Actions secret. Only use a publishable/anon key, never a service-role key.
"""
from __future__ import annotations

import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

EXPECTED_PROJECT = "gpshctxxgjvzplrbegwf"
TIMEOUT_SECONDS = 15


def main() -> int:
    project_ref = os.environ.get("SUPABASE_HEALTH_PROJECT_REF", "")
    key = os.environ.get("SUPABASE_HEALTH_API_KEY", "")

    if project_ref != EXPECTED_PROJECT:
        print("ERROR: Ref does not match dedicated Robo-Teacher project.", file=sys.stderr)
        return 2
    if not key:
        print("ERROR: Configure GitHub Actions secret ROBO_SUPABASE_HEALTH_API_KEY (publishable/anon key).", file=sys.stderr)
        return 2
    if "service_role" in key:
        print("ERROR: Never use a service-role API key for this check.", file=sys.stderr)
        return 2

    endpoint = (
        f"https://{EXPECTED_PROJECT}.supabase.co/rest/v1/"
        "robo_schools?select=id&limit=1"
    )
    req = Request(
        endpoint,
        headers={
            "apikey": key,
            "Accept": "application/json",
            "User-Agent": "robo-teacher-readonly-health/1.0",
        },
        method="GET",
    )
    try:
        with urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            status = resp.status
            payload = resp.read(16384)
        if status != 200:
            print(f"ERROR: Supabase returned HTTP {status}", file=sys.stderr)
            return 1
        result = json.loads(payload)
        if not isinstance(result, list):
            print("ERROR: Unexpected Supabase response format", file=sys.stderr)
            return 1
        print("OK: Authenticated read-only database request succeeded; no records altered.")
        return 0
    except HTTPError as exc:
        print(f"ERROR: Supabase returned HTTP {exc.code} (check RLS, API key and project status).", file=sys.stderr)
    except (URLError, TimeoutError) as exc:
        print(f"ERROR: Supabase connection failed: {type(exc).__name__}", file=sys.stderr)
    except (ValueError, OSError) as exc:
        print(f"ERROR: Unexpected Supabase response: {type(exc).__name__}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())

"""Disabled-by-default learner-scoped Supabase progress reader.

Supabase REST authenticates the user's JWT and applies the database's RLS.
No service-role key, no user-provided owner ID, no fallback to privileged SQL.
Not mounted in the classroom application.
"""
import os
import httpx

PROJECT_URL = "https://gpshctxxgjvzplrbegwf.supabase.co"

def read_own_progress(access_token, *, enabled=False, client=None):
    if not enabled or os.getenv("ROBO_SUPABASE_LEARNER_READ_ENABLED") != "true":
        raise PermissionError("Learner progress integration disabled")
    if not isinstance(access_token,str) or len(access_token) < 20 or "\n" in access_token:
        raise PermissionError("Valid signed-in session required")
    key=os.getenv("ROBO_SUPABASE_PUBLISHABLE_KEY","")
    if not key or key.startswith("sb_secret_") or key.startswith("service_role"):
        raise RuntimeError("Publishable Supabase key required")
    headers={"apikey":key,"Authorization":"Bearer "+access_token}
    own_client=client is None
    session=client or httpx.Client(timeout=12)
    try:
        response=session.get(PROJECT_URL+"/rest/v1/robo_learning_progress",
            params={"select":"topic_code,mastery_score,updated_at","order":"updated_at.desc","limit":"100"},
            headers=headers)
        response.raise_for_status()
        rows=response.json()
        if not isinstance(rows,list):raise RuntimeError("Invalid progress response")
        return rows
    finally:
        if own_client:session.close()

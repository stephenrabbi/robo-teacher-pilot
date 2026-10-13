"""Unmounted Supabase Auth user verifier for staged integration.

Calls the project-pinned Supabase Auth /user endpoint. No JWT claim is trusted
without remote token verification. Never call directly from a browser.
"""
import json
import urllib.error
import urllib.request
from uuid import UUID


class SupabaseAuthVerificationError(ValueError):
    pass


def verify_supabase_user(access_token: str, *, project_url: str, publishable_key: str,
                         urlopen=urllib.request.urlopen) -> str:
    if not isinstance(access_token, str) or not (20 <= len(access_token) <= 8192):
        raise SupabaseAuthVerificationError("Invalid bearer token")
    if not isinstance(project_url, str) or not project_url.startswith("https://"):
        raise SupabaseAuthVerificationError("HTTPS Supabase project required")
    from urllib.parse import urlsplit
    parsed = urlsplit(project_url)
    if (parsed.username or parsed.password or parsed.port or parsed.path not in ("", "/") or
            parsed.query or parsed.fragment or not parsed.hostname or
            not parsed.hostname.endswith(".supabase.co")):
        raise SupabaseAuthVerificationError("Invalid project URL")
    if not isinstance(publishable_key, str) or not publishable_key.startswith("sb_publishable_"):
        raise SupabaseAuthVerificationError("Publishable project key required")
    request = urllib.request.Request(
        f"https://{parsed.hostname}/auth/v1/user",
        headers={"apikey": publishable_key, "Authorization": f"Bearer {access_token}",
                 "Accept": "application/json"},
        method="GET",
    )
    try:
        with urlopen(request, timeout=8) as response:
            if response.status != 200:
                raise SupabaseAuthVerificationError("Authentication rejected")
            body = response.read(16385)
            if len(body) > 16384:
                raise SupabaseAuthVerificationError("Unexpected authentication response")
            user = json.loads(body)
    except (OSError, urllib.error.HTTPError, ValueError, json.JSONDecodeError) as exc:
        raise SupabaseAuthVerificationError("Supabase user verification failed") from exc
    if not isinstance(user, dict) or not isinstance(user.get("id"), str):
        raise SupabaseAuthVerificationError("Missing verified user ID")
    try:
        uid = str(UUID(user["id"]))
    except ValueError as exc:
        raise SupabaseAuthVerificationError("Invalid verified user ID") from exc
    if uid != user["id"].lower():
        raise SupabaseAuthVerificationError("Noncanonical user ID")
    return uid

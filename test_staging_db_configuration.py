"""Unmounted configuration check for isolated Supabase enrollment testing.

Never print, log, serialize or return database DSNs: credentials can be embedded.
This only validates configuration and does not create a DB connection.
"""
from urllib.parse import urlsplit

TEST_PROJECT="drzaxpofuhqchmpkwhpy"
ALLOWED_HOSTS={
    f"db.{TEST_PROJECT}.supabase.co",
    # Supabase pooler hosts are not pinned here; require separate explicit review.
}


def validate_test_db_configuration(dsn: str, *, expected_database="postgres"):
    if not isinstance(dsn,str) or not dsn:
        raise ValueError("Missing staging database connection")
    try:
        p=urlsplit(dsn)
        host=p.hostname
        port=p.port
    except ValueError as exc:
        raise ValueError("Invalid staging database configuration") from exc
    if p.scheme not in ("postgresql","postgres"):
        raise ValueError("PostgreSQL connection required")
    if host not in ALLOWED_HOSTS or port not in (None,5432):
        raise ValueError("Only isolated test project database is allowed")
    if p.path != "/" + expected_database or not p.username or p.password is None:
        raise ValueError("Incomplete staging database connection")
    if p.fragment:
        raise ValueError("Invalid staging database configuration")
    # Caller must additionally require sslmode=verify-full and trusted CA,
    # verify actual role/current_user and enforce limited database privileges.
    return True

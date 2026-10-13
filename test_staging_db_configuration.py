"""Test-only Supabase destination validator. Never log database DSNs."""
from urllib.parse import parse_qs, urlsplit

PROJECT = "drzaxpofuhqchmpkwhpy"
LOGIN = "robo_test_staging_login"
DIRECT = f"db.{PROJECT}.supabase.co"
SESSION = "aws-1-eu-west-1.pooler.supabase.com"


def validate_test_db_configuration(dsn: str, *, expected_database="postgres"):
    if not isinstance(dsn, str) or not dsn:
        raise ValueError("Missing staging database connection")
    try:
        p = urlsplit(dsn)
        host, port, username, password = p.hostname, p.port, p.username, p.password
        opts = parse_qs(p.query, keep_blank_values=True, strict_parsing=True)
    except (ValueError, TypeError) as exc:
        raise ValueError("Invalid staging database configuration") from exc
    if p.scheme not in ("postgresql", "postgres") or p.fragment:
        raise ValueError("PostgreSQL configuration required")
    allowed_user = LOGIN if host == DIRECT else f"{LOGIN}.{PROJECT}" if host == SESSION else None
    if not allowed_user or username != allowed_user or port != 5432:
        raise ValueError("Isolated test host, user and port required")
    if p.path != "/" + expected_database or not password:
        raise ValueError("Incomplete staging database configuration")
    if opts != {"sslmode": ["verify-full"]}:
        raise ValueError("TLS certificate and hostname verification required")
    return True

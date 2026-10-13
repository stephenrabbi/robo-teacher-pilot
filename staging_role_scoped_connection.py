"""Test-only role-scoped connection factory; not activated or mounted.

Ensures PrivateTestEnrollmentStore uses the intended restricted role on every
transaction. This is not a substitute for testing a real Supabase connection.
"""
from contextlib import contextmanager
from staging_restricted_db_probe import EXPECTED_LOGIN, EXPECTED_EXECUTOR
from test_staging_db_configuration import validate_test_db_configuration


@contextmanager
def restricted_staging_connection(connect, dsn):
    validate_test_db_configuration(dsn)
    with connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_user, session_user")
            if tuple(cur.fetchone()) != (EXPECTED_LOGIN, EXPECTED_LOGIN):
                raise RuntimeError("Unexpected database login")
            cur.execute("SET LOCAL ROLE robo_test_enrollment_executor")
            cur.execute("SELECT current_user, session_user")
            if tuple(cur.fetchone()) != (EXPECTED_EXECUTOR, EXPECTED_LOGIN):
                raise RuntimeError("Restricted database role not active")
        yield conn


def build_test_connection_factory(connect, dsn):
    # Fail before creating a closure that could be invoked with a bad DSN.
    validate_test_db_configuration(dsn)

    def make_connection():
        return restricted_staging_connection(connect, dsn)

    return make_connection

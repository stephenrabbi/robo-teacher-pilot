"""Offline-by-default, read-only test connection probe.

Run only in the isolated Synthetic Lab after a password is stored privately.
No enrollment writes and no HTTP route. Errors intentionally omit DSN details.
"""
import os
import logging

logger = logging.getLogger('robo-teacher-staging-probe')
from test_staging_db_configuration import validate_test_db_configuration

EXPECTED_LOGIN = "robo_test_staging_login"
EXPECTED_EXECUTOR = "robo_test_enrollment_executor"


def check_restricted_connection(connect, dsn):
    validate_test_db_configuration(dsn)
    with connect(dsn) as connection:
        with connection.cursor() as cursor:
            logger.warning("Restricted staging probe stage: inspect_connected_identity")
            cursor.execute("SELECT current_user, session_user")
            login, session = cursor.fetchone()
            if (login, session) != (EXPECTED_LOGIN, EXPECTED_LOGIN):
                raise RuntimeError("Unexpected connected database role")
            logger.warning("Restricted staging probe stage: inspect_direct_privileges")
            cursor.execute(
                "SELECT has_schema_privilege(current_user, "
                "'robo_test_private', 'USAGE'), "
                "has_function_privilege(current_user, "
                "'robo_test_private.consume_and_enroll(uuid,bytea)', 'EXECUTE'), "
                "has_table_privilege(current_user, "
                "'public.robo_learning_progress', 'SELECT'), "
                "has_table_privilege(current_user, "
                "'public.robo_learning_progress', 'UPDATE')"
            )
            if any(cursor.fetchone()):
                raise RuntimeError("Staging login has unexpected direct privileges")
            logger.warning("Restricted staging probe stage: activate_restricted_executor")
            cursor.execute("SET LOCAL ROLE robo_test_enrollment_executor")
            logger.warning("Restricted staging probe stage: verify_executor_identity")
            cursor.execute("SELECT current_user, session_user")
            role, session_after = cursor.fetchone()
            if (role, session_after) != (EXPECTED_EXECUTOR, EXPECTED_LOGIN):
                raise RuntimeError("Restricted role activation failed")
            logger.warning("Restricted staging probe stage: verify_denied_progress_write")
            cursor.execute(
                "SELECT has_table_privilege(current_user, "
                "'public.robo_learning_progress', 'UPDATE')"
            )
            if cursor.fetchone()[0]:
                raise RuntimeError("Unsafe progress update permission")
        connection.rollback()  # SET LOCAL never persists
    return True


def main():
    dsn = os.environ.get("ROBO_TEST_DATABASE_URL")
    if not dsn:
        raise SystemExit("Missing ROBO_TEST_DATABASE_URL in isolated staging environment")
    try:
        import psycopg
        check_restricted_connection(psycopg.connect, dsn)
    except Exception as exc:
        # No DSN, password or driver exception messages: may contain sensitive data.
        raise SystemExit("Restricted test connection check failed") from None
    print("PASS: restricted test database role and denied progress update")


if __name__ == "__main__":
    main()

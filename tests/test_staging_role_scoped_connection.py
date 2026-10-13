import unittest
from staging_role_scoped_connection import build_test_connection_factory


DSN = ("postgresql://robo_test_staging_login:placeholder@"
       "aws-1-eu-west-1.pooler.supabase.com:5432/postgres?sslmode=verify-full")


class FakeCursor:
    def __init__(self, values):
        self.values = iter(values)
        self.commands = []
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def execute(self, statement): self.commands.append(statement)
    def fetchone(self): return next(self.values)


class FakeConnection:
    def __init__(self, results):
        self.cur = FakeCursor(results)
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def cursor(self): return self.cur


class TestRoleScopedDB(unittest.TestCase):
    def test_restricted_role_for_every_connection(self):
        instances = []
        def open_connection(dsn):
            conn = FakeConnection([
                ("robo_test_staging_login", "robo_test_staging_login"),
                ("robo_test_enrollment_executor", "robo_test_staging_login"),
            ])
            instances.append(conn)
            return conn
        factory = build_test_connection_factory(open_connection, DSN)
        for _ in range(2):
            with factory() as conn:
                self.assertEqual(conn.cur.commands[-1], "SELECT current_user, session_user")
        self.assertEqual(len(instances), 2)
        self.assertTrue(all("SET LOCAL ROLE robo_test_enrollment_executor" in
                            c.cur.commands for c in instances))

    def test_wrong_login_fails_before_enrollment(self):
        factory = build_test_connection_factory(
            lambda dsn: FakeConnection([("postgres", "postgres")]), DSN)
        with self.assertRaisesRegex(RuntimeError, "Unexpected database login"):
            with factory():
                self.fail("Should never allow enrollment")

    def test_role_switch_failure_is_fatal(self):
        factory = build_test_connection_factory(
            lambda dsn: FakeConnection([
                ("robo_test_staging_login", "robo_test_staging_login"),
                ("robo_test_staging_login", "robo_test_staging_login"),
            ]), DSN)
        with self.assertRaisesRegex(RuntimeError, "not active"):
            with factory():
                self.fail("Should never allow enrollment")

    def test_production_dsn_rejected_without_connecting(self):
        with self.assertRaises(ValueError):
            build_test_connection_factory(
                lambda dsn: self.fail("Should not connect"),
                DSN.replace("aws-1-eu-west-1.pooler.supabase.com",
                            "db.gpshctxxgjvzplrbegwf.supabase.co"))


if __name__ == "__main__":
    unittest.main()

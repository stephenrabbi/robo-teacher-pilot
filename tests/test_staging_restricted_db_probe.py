import unittest
from staging_restricted_db_probe import check_restricted_connection


class Cursor:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.sql = []
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def execute(self, sql): self.sql.append(sql)
    def fetchone(self): return next(self.responses)


class Connection:
    def __init__(self, responses):
        self.cur = Cursor(responses)
        self.rolled_back = False
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def cursor(self): return self.cur
    def rollback(self): self.rolled_back = True


class TestRestrictedProbe(unittest.TestCase):
    dsn = ("postgresql://robo_test_staging_login:placeholder@"
           "aws-1-eu-west-1.pooler.supabase.com:5432/postgres?sslmode=verify-full")

    def test_expected_restricted_role(self):
        conn = Connection([
            ("robo_test_staging_login", "robo_test_staging_login"),
            ("robo_test_enrollment_executor", "robo_test_staging_login"),
            (False,),
        ])
        self.assertTrue(check_restricted_connection(lambda dsn: conn, self.dsn))
        self.assertTrue(conn.rolled_back)

    def test_reject_admin_login(self):
        conn = Connection([("postgres", "postgres")])
        with self.assertRaisesRegex(RuntimeError, "Unexpected connected database role"):
            check_restricted_connection(lambda dsn: conn, self.dsn)

    def test_reject_broad_progress_update(self):
        conn = Connection([
            ("robo_test_staging_login", "robo_test_staging_login"),
            ("robo_test_enrollment_executor", "robo_test_staging_login"),
            (True,),
        ])
        with self.assertRaisesRegex(RuntimeError, "Unsafe progress update permission"):
            check_restricted_connection(lambda dsn: conn, self.dsn)


if __name__ == "__main__":
    unittest.main()

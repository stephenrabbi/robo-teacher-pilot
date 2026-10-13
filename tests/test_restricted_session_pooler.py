"""Additional test-only validation for the isolated IPv4 session pooler."""
import unittest
from test_staging_db_configuration import validate_test_db_configuration


class TestRestrictedSessionPooler(unittest.TestCase):
    def test_scoped_session_pooler(self):
        dsn = ("postgresql://robo_test_staging_login:placeholder@"
               "aws-1-eu-west-1.pooler.supabase.com:5432/postgres?sslmode=verify-full")
        self.assertTrue(validate_test_db_configuration(dsn))

    def test_reject_wrong_project_user(self):
        dsn = ("postgresql://robo_test_staging_login.otherproject:placeholder@"
               "aws-1-eu-west-1.pooler.supabase.com:5432/postgres?sslmode=verify-full")
        with self.assertRaises(ValueError):
            validate_test_db_configuration(dsn)

    def test_reject_unverified_tls(self):
        dsn = ("postgresql://robo_test_staging_login:placeholder@"
               "db.drzaxpofuhqchmpkwhpy.supabase.co:5432/postgres?sslmode=require")
        with self.assertRaises(ValueError):
            validate_test_db_configuration(dsn)

    def test_reject_default_admin(self):
        dsn = ("postgresql://postgres.drzaxpofuhqchmpkwhpy:placeholder@"
               "aws-1-eu-west-1.pooler.supabase.com:5432/postgres?sslmode=verify-full")
        with self.assertRaises(ValueError):
            validate_test_db_configuration(dsn)


if __name__ == "__main__":
    unittest.main()

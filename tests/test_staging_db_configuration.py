import unittest
from test_staging_db_configuration import validate_test_db_configuration


class TestStagingDBConfig(unittest.TestCase):
    def test_correct_test_project(self):
        self.assertTrue(validate_test_db_configuration(
            "postgresql://robo_test_staging_login:placeholder@db.drzaxpofuhqchmpkwhpy.supabase.co:5432/postgres?sslmode=verify-full"))

    def test_production_project_rejected(self):
        with self.assertRaises(ValueError):
            validate_test_db_configuration(
                "postgresql://x:y@db.gpshctxxgjvzplrbegwf.supabase.co:5432/postgres")

    def test_pooler_requires_separate_review(self):
        with self.assertRaises(ValueError):
            validate_test_db_configuration(
                "postgresql://x:y@aws-0-eu-west-1.pooler.supabase.com:6543/postgres")

    def test_no_credentials_rejected(self):
        with self.assertRaises(ValueError):
            validate_test_db_configuration("postgresql://db.drzaxpofuhqchmpkwhpy.supabase.co:5432/postgres")

    def test_wrong_scheme_rejected(self):
        with self.assertRaises(ValueError):
            validate_test_db_configuration("http://x:y@db.drzaxpofuhqchmpkwhpy.supabase.co/postgres")


if __name__=="__main__":
    unittest.main()

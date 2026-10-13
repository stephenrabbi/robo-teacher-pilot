"""Ensure stage-only database validation stays side-effect free."""
import unittest
from unittest.mock import patch
from test_staging_db_configuration import validate_test_db_configuration


class TestStageOnlyValidation(unittest.TestCase):
    def test_validation_rejects_prod_without_network_or_connection(self):
        dsn="postgresql://fake:fake@db.gpshctxxgjvzplrbegwf.supabase.co:5432/postgres"
        with patch("socket.create_connection", side_effect=AssertionError("Network attempted")):
            with self.assertRaises(ValueError):
                validate_test_db_configuration(dsn)

    def test_validation_is_offline_and_does_not_connect(self):
        dsn="postgresql://fake:fake@db.drzaxpofuhqchmpkwhpy.supabase.co:5432/postgres"
        with patch("socket.create_connection", side_effect=AssertionError("Network attempted")):
            self.assertTrue(validate_test_db_configuration(dsn))


if __name__ == "__main__":
    unittest.main()

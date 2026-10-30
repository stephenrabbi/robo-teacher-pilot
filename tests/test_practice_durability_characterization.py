"""Characterization tests for Google Sheets persistence failures.

All operations use synthetic records and mocks; no production Google Sheet is touched.
These tests document the current behavior before durable retry storage is introduced.
"""
import unittest
from unittest.mock import patch
import practice_progress as progress


class PracticePersistenceFailureTests(unittest.TestCase):
    def setUp(self):
        self.original_records = progress._memory_records
        self.original_unsynced = progress._unsynced_ids
        progress._memory_records = []
        progress._unsynced_ids = set()

    def tearDown(self):
        progress._memory_records = self.original_records
        progress._unsynced_ids = self.original_unsynced

    def test_sheets_write_failure_is_not_reported_as_saved(self):
        summary = {
            "session_id": "qa-durability-001",
            "topic": "Simple Equations",
            "difficulty": "easy",
            "score": 1,
            "attempted": 1,
            "percentage": 100,
            "class_level": "JSS2",
            "learner_code": "QA-DURABILITY",
        }
        with patch.object(progress, "_sheet_configured", return_value=True):
            with patch.object(progress, "_get_worksheet") as get_sheet:
                get_sheet.return_value.append_row.side_effect = OSError("synthetic Sheets outage")
                saved = progress.save_result("synthetic-owner", summary)
        self.assertIs(saved, False)
        self.assertIn(summary["session_id"], progress._unsynced_ids)
        self.assertEqual(progress._memory_records[0]["learner_id"], "synthetic-owner")

    def test_without_sheets_credentials_result_is_only_in_memory(self):
        summary = {
            "session_id": "qa-durability-002",
            "topic": "Simple Equations",
            "difficulty": "easy",
            "score": 1,
            "attempted": 1,
            "percentage": 100,
            "class_level": "JSS2",
        }
        with patch.object(progress, "_sheet_configured", return_value=False):
            self.assertIs(progress.save_result("synthetic-owner", summary), False)
        self.assertIn(summary["session_id"], progress._unsynced_ids)

    def test_process_restart_discards_unsynced_fallback_records(self):
        """Demonstrate why memory alone cannot be considered a durable queue."""
        summary = {
            "session_id": "qa-durability-restart",
            "topic": "Simple Equations",
            "difficulty": "easy",
            "score": 1,
            "attempted": 1,
            "percentage": 100,
            "class_level": "JSS2",
        }
        with patch.object(progress, "_sheet_configured", return_value=False):
            progress.save_result("synthetic-owner", summary)
            # Simulate a process restart by replacing the process-local state.
            progress._memory_records = []
            progress._unsynced_ids = set()
            records, durable = progress.get_records("synthetic-owner")
        self.assertEqual(records, [])
        self.assertIs(durable, False)

    def test_same_session_is_only_cached_once_locally(self):
        summary = {
            "session_id": "qa-durability-repeat",
            "topic": "Simple Equations",
            "difficulty": "easy",
            "score": 1,
            "attempted": 1,
            "percentage": 100,
            "class_level": "JSS2",
        }
        with patch.object(progress, "_sheet_configured", return_value=False):
            progress.save_result("synthetic-owner", summary)
            progress.save_result("synthetic-owner", summary)
        self.assertEqual(len(progress._memory_records), 1)


if __name__ == "__main__":
    unittest.main()

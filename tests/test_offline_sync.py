import unittest
from progress_store.offline_sync import PendingEvent, synchronize

def pending(identifier):
    return PendingEvent(identifier, {"event_id":identifier,"topic_key":"fractions"})

class OfflineSyncTests(unittest.TestCase):
    def test_successful_upload_removes_only_acknowledged_items(self):
        queue = (pending("one"), pending("two"))
        result = synchronize(queue, lambda _: True)
        self.assertEqual(result.acknowledged, ("one","two"))
        self.assertEqual(result.remaining, ())
        self.assertFalse(result.failed)

    def test_network_failure_retains_unsent_events(self):
        def send(event):
            if event["event_id"] == "two": raise ConnectionError()
            return True
        result = synchronize((pending("one"),pending("two"),pending("three")), send)
        self.assertEqual(result.acknowledged, ("one",))
        self.assertEqual(tuple(x.event_id for x in result.remaining), ("two","three"))
        self.assertEqual(result.remaining[0].attempts, 1)

    def test_idempotent_duplicate_response_is_acknowledged(self):
        result = synchronize((pending("one"),), lambda _: False)
        self.assertEqual(result.remaining, ())
        self.assertEqual(result.acknowledged, ("one",))

    def test_ambiguous_acknowledgment_keeps_event(self):
        result = synchronize((pending("one"),), lambda _: None)
        self.assertTrue(result.failed)
        self.assertEqual(result.remaining[0].event_id, "one")

    def test_invalid_identity_fails_closed(self):
        with self.assertRaises(ValueError):
            synchronize((PendingEvent("one", {"event_id":"two"}),), lambda _: True)

    def test_permanent_validation_error_is_not_silently_discarded(self):
        with self.assertRaises(ValueError):
            synchronize((pending("one"),), lambda _: (_ for _ in ()).throw(ValueError("Bad event")))

if __name__ == "__main__":
    unittest.main()

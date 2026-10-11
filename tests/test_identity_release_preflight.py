import unittest
from integration_research.release_preflight import REQUIRED, assess

class ReleasePreflightTests(unittest.TestCase):
    def test_missing_all_fails_closed(self):
        self.assertEqual(assess({}),list(REQUIRED))
    def test_single_missing_is_blocker(self):
        values={key:"true" for key in REQUIRED}
        for key in REQUIRED:
            altered=dict(values)
            altered[key]="false"
            self.assertEqual(assess(altered),[key])
    def test_only_exact_true_accepted(self):
        values={key:"true" for key in REQUIRED}
        self.assertEqual(assess(values),[])
        values[REQUIRED[0]]="TRUE"
        self.assertIn(REQUIRED[0],assess(values))
if __name__=="__main__":
    unittest.main()

import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("mte_runner", Path(__file__).parents[1] / "src" / "mte_runner.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class RunnerTests(unittest.TestCase):
    def test_empty_not_run(self):
        self.assertEqual(module.evaluate([]), "NOT_RUN")

    def test_pass_requires_evidence(self):
        self.assertEqual(module.evaluate([{"test_id":"T01","status":"PASS","reason":"ok"}]), "INVALID_EVIDENCE")

    def test_pass_with_evidence(self):
        self.assertEqual(module.evaluate([{"test_id":"T01","status":"PASS","reason":"checked","evidence_ref":"sha256:abc"}]), "CONFORMANT_WITHIN_TESTED_SCOPE")

    def test_unverified_never_conformant(self):
        self.assertEqual(module.evaluate([{"test_id":"T01","status":"UNVERIFIED","reason":"no validator"}]), "UNVERIFIED")

    def test_fail_dominates(self):
        self.assertEqual(module.evaluate([{"test_id":"T01","status":"PASS","reason":"ok","evidence_ref":"e1"},{"test_id":"T02","status":"FAIL","reason":"mismatch"}]), "NON_CONFORMANT")

if __name__ == "__main__":
    unittest.main()

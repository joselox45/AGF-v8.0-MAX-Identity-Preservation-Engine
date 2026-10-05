"""APCEGovernor v1.0 — unitarias (stdlib puro)."""
import sys, os, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from apce_governor import (APCEGovernor, AGFVerdict, APCE_BLOCKING_STATES,
                           APCE_VERSION)


class TestGovernance(unittest.TestCase):
    def test_g1_pass_without_evidence_blocked(self):
        d = APCEGovernor().review(AGFVerdict("EMBEDDING", "PASS", None, ""))
        self.assertEqual((d.outcome, d.final_state, d.rule),
                         ("DOWNGRADED", "BLOCKED", "G1"))

    def test_g1_pass_with_evidence_confirmed(self):
        d = APCEGovernor().review(AGFVerdict("MTE", "PASS",
                                             "ab12" * 16, "cos ok"))
        self.assertEqual((d.outcome, d.final_state), ("CONFIRMED", "PASS"))
        self.assertTrue(d.evidence_hash.startswith("ab12"))

    def test_g2_blocked_propagates(self):
        for closed in ("BLOCKED", "UNVERIFIED", "NOT_RUN"):
            d = APCEGovernor().review(AGFVerdict("IDENTITY", closed,
                                                 "ff" * 32, ""))
            self.assertEqual(d.final_state, "BLOCKED")
            self.assertEqual(d.rule, "G2")

    def test_g3_capability_highest(self):
        d = APCEGovernor(capability_ok=False).review(
            AGFVerdict("MTE", "PASS", "aa" * 32))
        self.assertEqual((d.outcome, d.rule), ("DOWNGRADED", "G3"))

    def test_g3_authorization(self):
        d = APCEGovernor(authorization_ok=False).review(
            AGFVerdict("MTE", "PASS", "aa" * 32))
        self.assertEqual((d.outcome, d.final_state), ("DOWNGRADED", "BLOCKED"))

    def test_g4_apce_blocking_state_vetoes(self):
        for st in APCE_BLOCKING_STATES:
            d = APCEGovernor(apce_state=st).review(
                AGFVerdict("CHAT_RUNTIME", "PASS", "aa" * 32))
            self.assertEqual((d.outcome, d.rule), ("VETOED", "G4"))

    def test_g6_assurance_gate(self):
        g = APCEGovernor()
        self.assertEqual(g.assurance_gate(False, True), "TESTED-BLOCKED")
        self.assertEqual(g.assurance_gate(True, False), "ELIGIBLE_FOR_TESTED")
        self.assertEqual(g.assurance_gate(True, True),
                         "ELIGIBLE_FOR_INDEPENDENT_ATTESTATION")

    def test_apce_version_canonical(self):
        self.assertEqual(APCE_VERSION, "8.1.0-CANONICAL")


if __name__ == "__main__":
    unittest.main()

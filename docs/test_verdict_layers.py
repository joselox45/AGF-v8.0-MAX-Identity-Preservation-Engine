"""VerdictLayers — la regla anti-confusion PASS-formal vs identidad."""
import sys, os, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from verdict_layers import VerdictLayers, IDENTITY_STATES


def base(**kw):
    d = dict(formal_status="PASS", biometric_status="PASS", cosine=0.9,
             threshold=0.65, provenance_declared=True, cross_person_tested=True,
             anti_replay_clean=True)
    d.update(kw)
    return d


class TestLayers(unittest.TestCase):
    vl = VerdictLayers()

    def test_todo_presente_soporta(self):
        v = self.vl.evaluate(**base())
        self.assertEqual(v.L3_identity, "SUPPORTED")

    def test_pass_formal_no_implica_identidad(self):
        # L1 PASS + L2 PASS pero SIN procedencia ni discriminacion
        v = self.vl.evaluate(**base(provenance_declared=False, cross_person_tested=False))
        self.assertEqual(v.L3_identity, "NOT_DETERMINED")
        self.assertIn("procedencia", v.reasons[-1])

    def test_cosine_alto_solo_no_basta(self):
        v = self.vl.evaluate(**base(formal_status="NOT_RUN", cross_person_tested=False))
        self.assertEqual(v.L3_identity, "NOT_DETERMINED")

    def test_biometric_fail_refuta(self):
        v = self.vl.evaluate(**base(biometric_status="FAIL", cosine=0.3))
        self.assertEqual(v.L3_identity, "REFUTED")

    def test_antireplay_falla_biometria(self):
        v = self.vl.evaluate(**base(anti_replay_clean=False))
        self.assertEqual(v.L2_biometric, "FAIL")

    def test_default_fail_closed(self):
        v = self.vl.evaluate(formal_status="BLOCKED", biometric_status="BLOCKED",
                             cosine=None, threshold=0.65,
                             provenance_declared=False, cross_person_tested=False)
        self.assertEqual(v.L3_identity, "NOT_DETERMINED")


if __name__ == "__main__":
    unittest.main()

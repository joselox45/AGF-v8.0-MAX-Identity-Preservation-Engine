"""T29/T30 + attestation — unitarias (stdlib + cryptography opcional)."""
import sys, os, json, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from evidence_taxonomy import EvidenceClassifier, EvidenceState, CONFORMANT_STATES
from face_detector import TFLiteFaceDetector, DetectionResult


class TestTaxonomy(unittest.TestCase):
    c = EvidenceClassifier()

    def test_all_six_states(self):
        cases = [
            (dict(present=False), EvidenceState.NO_EVIDENCE),
            (dict(present=False, unavailable_reason=True), EvidenceState.EVIDENCE_UNAVAILABLE),
            (dict(present=True, hash_format_ok=False), EvidenceState.EVIDENCE_INVALID),
            (dict(present=True, hash_format_ok=True, verified=False), EvidenceState.EVIDENCE_INSUFFICIENT),
            (dict(present=True, hash_format_ok=True, verified=True), EvidenceState.EVIDENCE_VALID),
            (dict(present=True, hash_format_ok=True, verified=True, independent=True),
             EvidenceState.EVIDENCE_INDEPENDENT),
        ]
        for kw, st in cases:
            r = self.c.classify(**kw)
            self.assertEqual(r.state, st, kw)
            self.assertEqual(r.conformant, st in CONFORMANT_STATES)

    def test_fail_closed_default(self):
        r = self.c.classify(present=False)
        self.assertFalse(r.conformant)


class TestDetector(unittest.TestCase):
    def test_blocked_without_model(self):
        r = TFLiteFaceDetector().detect([[[0,0,0]]])
        self.assertEqual(r.status, "BLOCKED")


class TestAttestation(unittest.TestCase):
    def test_roundtrip(self):
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import (
                Ed25519PrivateKey, Ed25519PublicKey)
        except ImportError:
            self.skipTest("sin cryptography")
        import subprocess, tempfile
        ev = {"verification": {"status": "PASS", "cosine": 0.9},
              "weights_sha256": "ab", "evidence_hash": "cd"}
        td = tempfile.mkdtemp()
        p = os.path.join(td, "ev.json")
        json.dump(ev, open(p, "w"))
        tool = os.path.join(os.path.dirname(__file__), "..", "tools", "attest.py")
        r = subprocess.run([sys.executable, tool, p], capture_output=True, text=True, cwd=td)
        self.assertIn('"verdict": "ATTESTED"', r.stdout)
        # verificacion de firma
        d = json.load(open(os.path.join(td, "evidence", "attestation_ev.json")))
        body = {k: v for k, v in d.items() if k not in ("attestor_ed25519", "signature")}
        pk = Ed25519PublicKey.from_public_bytes(bytes.fromhex(d["attestor_ed25519"]))
        pk.verify(bytes.fromhex(d["signature"]), json.dumps(body, sort_keys=True).encode())


if __name__ == "__main__":
    unittest.main()

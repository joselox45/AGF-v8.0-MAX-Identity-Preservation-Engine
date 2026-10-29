"""Unitarias v9.0 — ejecutables con stdlib puro (python -m unittest)."""
import sys, os, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from face_embedding import (OnnxFaceEmbedder, VectorComparator,
                            EmbeddingResult, EmbeddingStatus)
from evidence_signing import EvidenceChain, HMACFallbackSigner
from agent_identity import enroll_agent, verify_agent, AgentIdentity


class TestEmbeddings(unittest.TestCase):
    def test_arcface_blocked_without_weights(self):
        r = OnnxFaceEmbedder("arcface").embed(None)
        self.assertEqual(r.status, EmbeddingStatus.BLOCKED)
        self.assertIn("fail-closed", r.reason)

    def test_facenet_blocked_without_weights(self):
        r = OnnxFaceEmbedder("facenet").embed(None)
        self.assertEqual(r.status, EmbeddingStatus.BLOCKED)

    def test_cosine_fail_closed_y_threshold(self):
        c = VectorComparator(threshold=0.8)
        blocked = EmbeddingResult(EmbeddingStatus.BLOCKED, "arcface:x")
        out = c.verify(blocked, blocked)
        self.assertEqual(out["status"], "BLOCKED")
        self.assertNotIn("cosine", out)
        v1 = EmbeddingResult(EmbeddingStatus.PASS, "m", vector=[1.0, 0.0])
        v2 = EmbeddingResult(EmbeddingStatus.PASS, "m", vector=[0.9, 0.1])
        self.assertEqual(c.verify(v1, v2)["status"], "PASS")
        v3 = EmbeddingResult(EmbeddingStatus.PASS, "m", vector=[0.1, 0.9])
        self.assertEqual(c.verify(v1, v3)["status"], "FAIL")

    def test_antireplay_rejects_identical(self):
        c = VectorComparator()
        v = [0.6, 0.8]
        a = EmbeddingResult(EmbeddingStatus.PASS, "m", vector=v)
        b = EmbeddingResult(EmbeddingStatus.PASS, "m", vector=list(v))
        out = c.verify(a, b)
        self.assertEqual(out["status"], "FAIL")
        self.assertIn("replay", out["reason"])


class TestEvidence(unittest.TestCase):
    def test_chain_detects_tampering(self):
        ch = EvidenceChain(HMACFallbackSigner(b"sec"))
        ch.append({"evento": "captura"})
        ch.append({"evento": "embedding"})
        self.assertEqual(ch.verify()["status"], "UNVERIFIED")  # HMAC nunca PASS
        ch.records[0].payload["evento"] = "ALTERADO"
        v = ch.verify()
        self.assertEqual(v["status"], "FAIL")
        self.assertEqual(v["seq"], 1)

    def test_hmac_degrades_unverified(self):
        ch = EvidenceChain(HMACFallbackSigner(b"sec"))
        rec = ch.append({"k": 1})
        self.assertEqual(rec.status, "UNVERIFIED")
        self.assertNotEqual(rec.status, "PASS")


class TestAgentIdentity(unittest.TestCase):
    def test_enroll_blocked_without_crypto(self):
        idn = enroll_agent("example.org", "agent-1")
        if idn.status == "BLOCKED":
            self.assertIsNone(idn.did)  # host sin cryptography
        else:
            self.assertTrue(idn.did.startswith("did:key:z"))
            self.assertEqual(idn.spiffe_id, "spiffe://example.org/agent-1")

    def test_verify_agent_fail_closed(self):
        bad = AgentIdentity("spiffe://x/y", "did:key:zbogus",
                            {"id": "did:otro"}, None, "PASS")
        self.assertEqual(verify_agent(bad)["status"], "FAIL")
        none_id = AgentIdentity(None, None, None, None, "BLOCKED")
        self.assertEqual(verify_agent(none_id)["status"], "BLOCKED")

    def test_spiffe_validation(self):
        from agent_identity import make_spiffe_id
        self.assertEqual(make_spiffe_id("example.org", "a", "b"),
                         "spiffe://example.org/a/b")
        with self.assertRaises(ValueError):
            make_spiffe_id("DOMINIO MALO!")


if __name__ == "__main__":
    unittest.main()

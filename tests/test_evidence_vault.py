"""Evidence Vault — genesis, integridad, alteracion detectada."""
import sys, os, json, unittest, tempfile, shutil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from evidence_vault import EvidenceVault


class TestVault(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.mkdtemp()
        self.v = EvidenceVault(path=os.path.join(self.td, "vault.jsonl"))
        self.ev1 = os.path.join(self.td, "a.json")
        self.ev2 = os.path.join(self.td, "b.json")
        json.dump({"verdict": {"L3_identity": "SUPPORTED", "cosine": 0.93}},
                  open(self.ev1, "w"))
        json.dump({"verdict": {"L3_identity": "REFUTED", "cosine": 0.2}},
                  open(self.ev2, "w"))

    def tearDown(self):
        shutil.rmtree(self.td, ignore_errors=True)

    def test_genesis_chain_verify(self):
        self.v.append(self.ev1)
        self.v.append(self.ev2)
        v = self.v.verify()
        self.assertEqual(v["status"], "PASS")
        self.assertEqual(v["records"], 2)
        self.assertNotEqual(self.v.head(), "0" * 64)

    def test_alteracion_detectada(self):
        self.v.append(self.ev1)
        json.dump({"verdict": {"L3_identity": "FORGED", "cosine": 0.99}},
                  open(self.ev1, "w"))
        self.assertEqual(self.v.verify()["status"], "FAIL")

    def test_cadena_rota_detectada(self):
        self.v.append(self.ev1)
        self.v.append(self.ev2)
        recs = open(self.v.path).read().splitlines()
        r2 = json.loads(recs[1]); r2["cosine"] = 0.999
        recs[1] = json.dumps(r2)
        open(self.v.path, "w").write("\n".join(recs) + "\n")
        self.assertEqual(self.v.verify()["status"], "FAIL")

    def test_metrics(self):
        self.v.append(self.ev1)
        m = self.v.metrics()
        self.assertEqual(m["L3_SUPPORTED"], 1)
        self.assertEqual(m["chain_integrity"], "PASS")
        self.assertIn("moat_note", m)


if __name__ == "__main__":
    unittest.main()

"""Vault v1.1 — retrocompat (sin metrics) + snapshots encadenados."""
import sys, os, json, unittest, tempfile, shutil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from evidence_vault import EvidenceVault


class TestVaultMetrics(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.mkdtemp()
        self.v = EvidenceVault(path=os.path.join(self.td, "vault.jsonl"))
        self.ev = os.path.join(self.td, "a.json")
        json.dump({"verdict": {"L3_identity": "SUPPORTED", "cosine": 0.93}},
                  open(self.ev, "w"))

    def tearDown(self):
        shutil.rmtree(self.td, ignore_errors=True)

    def test_registro_sin_metrics_verifica(self):
        self.v.append(self.ev)
        self.assertEqual(self.v.verify()["status"], "PASS")

    def test_mezcla_viejo_nuevo_verifica(self):
        self.v.append(self.ev)                      # estilo pre-v1.1
        r = self.v.append_metrics({"F_cumplimiento": 1.0, "turnos": 3})
        self.assertEqual(self.v.verify()["status"], "PASS")
        self.assertTrue(r.metrics["_source"])

    def test_metrics_count(self):
        self.v.append(self.ev)
        self.v.append_metrics({"F_cumplimiento": 0.8, "tasa_CONFLICTO": 0.2})
        m = self.v.metrics()
        self.assertEqual(m["metric_snapshots"], 1)
        self.assertEqual(m["verified_pairs"], 1)

    def test_alteracion_snapshot_detectada(self):
        self.v.append_metrics({"F": 1.0})
        lines = open(self.v.path).read().splitlines()
        r = json.loads(lines[0]); r["metrics"]["F"] = 0.0
        lines[0] = json.dumps(r)
        open(self.v.path, "w").write("\n".join(lines) + "\n")
        self.assertEqual(self.v.verify()["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()

"""mte_runner_v2 — tests de los 3 P0."""
import sys, os, json, hashlib, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from mte_runner_v2 import MTERunnerV2, REQUIRED_TESTS


def ok(tid):
    return {"test_id": tid, "status": "PASS",
            "evidence_ref": "sha256:" + "ab" * 32, "reason": "ok"}


class TestP0Coverage(unittest.TestCase):
    def setUp(self):
        self.r = MTERunnerV2(repo_root=".")

    def full_pass(self):
        return [ok(t) for t in REQUIRED_TESTS]

    def test_full_coverage_passes(self):
        import hashlib, os, json
        payloads = {}
        recs = self.full_pass()
        for rec in recs:
            data = json.dumps({"t": rec["test_id"]}).encode()
            path = os.path.join("evidence", f"{rec['test_id']}.json")
            open(path, "wb").write(data)
            rec["evidence_ref"] = "sha256:" + hashlib.sha256(data).hexdigest()
            payloads[rec["test_id"]] = path
        try:
            v = self.r.evaluate(recs)
            self.assertEqual(v.status, "CONFORMANT_WITHIN_TESTED_SCOPE")
        finally:
            for p in payloads.values():
                os.unlink(p)

    def test_missing_rejected(self):
        recs = self.full_pass()[:-3]
        v = self.r.evaluate(recs)
        self.assertEqual(v.status, "NON_CONFORMANT")
        self.assertTrue(any("ausentes" in x for x in v.reasons))

    def test_duplicates_rejected(self):
        recs = self.full_pass()
        recs[0] = dict(recs[1])
        v = self.r.evaluate(recs)
        self.assertEqual(v.status, "NON_CONFORMANT")
        self.assertTrue(any("duplicados" in x for x in v.reasons))

    def test_unknown_rejected(self):
        recs = self.full_pass() + [{"test_id": "T99", "status": "PASS"}]
        v = self.r.evaluate(recs)
        self.assertTrue(any("desconocidos" in x for x in v.reasons))


class TestP0Evidence(unittest.TestCase):
    def setUp(self):
        self.r = MTERunnerV2(repo_root=".")

    def test_bad_format_rejected(self):
        v = self.r.evaluate([{"test_id": "T01", "status": "PASS",
                              "evidence_ref": "sha256:abc", "reason": "x"}])
        self.assertTrue(any("evidence_ref invalido" in x for x in v.reasons))

    def test_hash_mismatch_detected(self):
        os.makedirs("evidence", exist_ok=True)
        open("evidence/T01.json", "w").write('{"fake": true}')
        try:
            v = self.r.evaluate([{"test_id": "T01", "status": "PASS",
                                  "evidence_ref": "sha256:" + "ab" * 32,
                                  "reason": "x"}])
            self.assertTrue(any("no coincide" in x for x in v.reasons))
        finally:
            os.unlink("evidence/T01.json")

    def test_hash_match_accepted(self):
        os.makedirs("evidence", exist_ok=True)
        data = b'{"real": true}'
        open("evidence/T01.json", "wb").write(data)
        digest = hashlib.sha256(data).hexdigest()
        try:
            v = self.r.evaluate([{"test_id": "T01", "status": "PASS",
                                  "evidence_ref": f"sha256:{digest}",
                                  "reason": "x"}])
            self.assertFalse(any("no coincide" in x for x in v.reasons))
        finally:
            os.unlink("evidence/T01.json")


class TestP0Identity(unittest.TestCase):
    def test_verdict_identified(self):
        v = MTERunnerV2(repo_root=".").evaluate([])
        self.assertEqual(v.runner_version, "2.1")
        self.assertEqual(v.commit_sha != "", True)
        self.assertEqual(v.tests_required, len(REQUIRED_TESTS))
        self.assertEqual(v.tests_covered, 0)

class TestG04NAGovernance(unittest.TestCase):
    def setUp(self):
        self.r = MTERunnerV2(repo_root=".")

    def test_na_without_justification_rejected(self):
        v = self.r.evaluate([{"test_id": "T01", "status": "NOT_APPLICABLE",
                              "na_authority": "APCE"}])
        self.assertTrue(any("sin justificacion" in x for x in v.reasons))

    def test_na_without_authority_rejected(self):
        v = self.r.evaluate([{"test_id": "T01", "status": "NOT_APPLICABLE",
                              "na_justification": "sin host LLM"}])
        self.assertTrue(any("sin autoridad" in x for x in v.reasons))

    def test_na_governed_accepted(self):
        v = self.r.evaluate([{"test_id": "T01", "status": "NOT_APPLICABLE",
                              "na_justification": "sin host LLM en este entorno",
                              "na_authority": "APCE-G4"}])
        self.assertFalse(any("NOT_APPLICABLE" in x for x in v.reasons))

class TestStrictDisk(unittest.TestCase):
    def test_evidencia_ausente_bloquea_por_defecto(self):
        import uuid
        tid = "T" + uuid.uuid4().hex[:6].upper()
        v = MTERunnerV2(repo_root=".").evaluate(
            [{"test_id": tid, "status": "PASS",
              "evidence_ref": "sha256:" + "ab" * 32, "reason": "x"}])
        self.assertTrue(any("EVIDENCIA AUSENTE" in x for x in v.reasons))

    def test_modo_leniente_no_bloquea_ausencia(self):
        import uuid
        tid = "T" + uuid.uuid4().hex[:6].upper()
        r = MTERunnerV2(repo_root=".", strict_disk=False)
        v = r.evaluate([{"test_id": tid, "status": "PASS",
                         "evidence_ref": "sha256:" + "ab" * 32, "reason": "x"}])
        self.assertFalse(any("EVIDENCIA AUSENTE" in x for x in v.reasons))


if __name__ == "__main__":
    unittest.main()

"""mte_runner_v2 — tests de los 3 P0."""
import sys, os, json, hashlib, unittest, tempfile, shutil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from mte_runner_v2 import MTERunnerV2, REQUIRED_TESTS, EVIDENCE_MAP


def ok(tid):
    return {"test_id": tid, "status": "PASS",
            "evidence_ref": "sha256:" + "ab" * 32, "reason": "ok"}


class TestP0Coverage(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.td, "evidence"), exist_ok=True)
        self.r = MTERunnerV2(repo_root=self.td)

    def tearDown(self):
        shutil.rmtree(self.td, ignore_errors=True)

    def full_pass(self):
        return [ok(t) for t in REQUIRED_TESTS]

    def test_full_coverage_passes(self):
        recs = self.full_pass()
        # crear evidencia en disco; tests que comparten archivo (T26/T27)
        # reciben el mismo contenido y hash
        per_file = {}
        for rec in recs:
            fname = EVIDENCE_MAP.get(rec["test_id"], f"{rec['test_id']}.json")
            per_file.setdefault(fname, []).append(rec)
        for fname, group in per_file.items():
            data = json.dumps({"tests": [r["test_id"] for r in group]}).encode()
            path = os.path.join(self.td, "evidence", fname)
            open(path, "wb").write(data)
            digest = "sha256:" + hashlib.sha256(data).hexdigest()
            for rec in group:
                rec["evidence_ref"] = digest
        v = self.r.evaluate(recs)
        self.assertEqual(v.status, "CONFORMANT_WITHIN_TESTED_SCOPE")
        self.assertEqual(v.metrics["C_pass"], round(31/31, 4))

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
        self.td = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.td, "evidence"), exist_ok=True)
        self.r = MTERunnerV2(repo_root=self.td)

    def tearDown(self):
        shutil.rmtree(self.td, ignore_errors=True)

    def test_bad_format_rejected(self):
        v = self.r.evaluate([{"test_id": "T01", "status": "PASS",
                              "evidence_ref": "sha256:abc", "reason": "x"}])
        self.assertTrue(any("evidence_ref invalido" in x for x in v.reasons))

    def test_hash_mismatch_detected(self):
        os.makedirs("evidence", exist_ok=True)
        open(os.path.join(self.td, "evidence", "T01.json"), "w").write('{"fake": true}')
        try:
            v = self.r.evaluate([{"test_id": "T01", "status": "PASS",
                                  "evidence_ref": "sha256:" + "ab" * 32,
                                  "reason": "x"}])
            self.assertTrue(any("no coincide" in x for x in v.reasons))
        finally:
            pass  # tearDown limpia el dir temporal

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
            pass  # tearDown limpia el dir temporal


class TestP0Identity(unittest.TestCase):
    def test_verdict_identified(self):
        v = MTERunnerV2(repo_root=".").evaluate([])
        self.assertEqual(v.runner_version, "2.0")
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

class TestEvidenceMap(unittest.TestCase):
    def test_t21_mapea_a_t21_json_minuscula(self):
        import uuid, hashlib, json as j, tempfile, os, shutil
        td = tempfile.mkdtemp(); os.makedirs(f"{td}/evidence")
        data = j.dumps({"t": "T21"}).encode()
        open(f"{td}/evidence/t21.json", "wb").write(data)
        try:
            v = MTERunnerV2(repo_root=td).evaluate(
                [{"test_id": "T21", "status": "PASS",
                  "evidence_ref": "sha256:" + hashlib.sha256(data).hexdigest(),
                  "reason": "x"}])
            self.assertFalse(any("AUSENTE" in x for x in v.reasons))
            self.assertEqual(v.metrics["C_pass"], round(1/31, 4))
        finally:
            shutil.rmtree(td, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()

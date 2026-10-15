"""Corpus v1 — determinismo y manifest."""
import sys, os, json, hashlib, unittest, tempfile, shutil, subprocess

ROOT = os.path.join(os.path.dirname(__file__), "..")
GEN = os.path.join(ROOT, "tools", "corpus_generate.py")


class TestCorpus(unittest.TestCase):
    def _gen(self, out):
        r = subprocess.run([sys.executable, GEN, "--n", "3", "--out", out,
                            "--seed", "777"], capture_output=True, text=True, cwd=ROOT)
        self.assertIn('"status": "PASS"', r.stdout, r.stderr)

    def test_determinismo_byte_identico(self):
        d1, d2 = tempfile.mkdtemp(), tempfile.mkdtemp()
        try:
            self._gen(d1); self._gen(d2)
            m1 = json.load(open(os.path.join(d1, "manifest.json")))
            m2 = json.load(open(os.path.join(d2, "manifest.json")))
            self.assertEqual(m1["files"], m2["files"])
            self.assertEqual(len(m1["files"]), 15)      # 3 ids x 5 variantes
        finally:
            shutil.rmtree(d1); shutil.rmtree(d2)

    def test_manifest_hashes_validos(self):
        d = tempfile.mkdtemp()
        try:
            self._gen(d)
            m = json.load(open(os.path.join(d, "manifest.json")))
            self.assertIn("pipeline-validation ONLY", m["claims_habilitados"])
            for rel, meta in m["files"].items():
                p = os.path.join(d, rel)
                self.assertTrue(os.path.exists(p), rel)
                real = hashlib.sha256(open(p, "rb").read()).hexdigest()
                self.assertEqual(real, meta["sha256"], rel)
        finally:
            shutil.rmtree(d)


if __name__ == "__main__":
    unittest.main()

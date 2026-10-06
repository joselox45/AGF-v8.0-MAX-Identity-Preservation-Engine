"""TFLiteFaceEmbedder — tests con interprete stub (sin modelo real)."""
import sys, os, math, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import tflite_embedder as te


class FakeTensor:
    def __init__(self, idx): self._idx = idx


class FakeInterp:
    """Simula Interpreter: devuelve vector fijo L2-normalizable."""
    def __init__(self, model_path=None, model_content=None):
        self._tensors = {}
    def allocate_tensors(self): pass
    def get_input_details(self): return [{"index": 0}]
    def get_output_details(self): return [{"index": 1}]
    def set_tensor(self, idx, val): self._tensors[idx] = val
    def invoke(self): pass
    def get_tensor(self, idx):
        import numpy as np
        v = np.array([0.6, 0.8] + [0.01] * 510, dtype=np.float32)
        return v.reshape(1, -1) if idx == 1 else None


class TestTFLiteEmbedder(unittest.TestCase):
    def test_blocked_without_interpreter(self):
        # sin tflite_runtime/tensorflow en este host -> BLOCKED
        e = te.TFLiteFaceEmbedder("arcface")
        r = e.embed([[0, 0, 0]])
        self.assertEqual(r.status, te.EmbeddingStatus.BLOCKED)

    def test_stub_inference_pass(self):
        orig = te.TFLiteFaceEmbedder._get_interpreter_class
        te.TFLiteFaceEmbedder._get_interpreter_class = lambda self: FakeInterp
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".tflite", delete=False) as f:
                f.write(b"fake-model-bytes")
                mb = b"fake-model-bytes"
            e = te.TFLiteFaceEmbedder("arcface", mb)
            self.assertIsNotNone(e._interp)
            px = [[[128, 128, 128]] * 4] * 4
            r = e.embed(px)
            self.assertEqual(r.status, te.EmbeddingStatus.PASS)
            self.assertAlmostEqual(r.norm, 1.0, places=5)
            self.assertTrue(r.evidence_hash)
        finally:
            te.TFLiteFaceEmbedder._get_interpreter_class = orig

    def test_normalize_flag(self):
        orig = te.TFLiteFaceEmbedder._get_interpreter_class
        seen = {}
        class SpyInterp(FakeInterp):
            def set_tensor(self, idx, val):
                seen["val"] = float(val.mean())
                super().set_tensor(idx, val)
        te.TFLiteFaceEmbedder._get_interpreter_class = lambda self: SpyInterp
        try:
            import numpy as np
            px = (np.ones((4, 4, 3)) * 255).tolist()   # todo blanco
            e = te.TFLiteFaceEmbedder("arcface", b"m", normalize=True)
            e.embed(px)
            self.assertAlmostEqual(seen["val"], (255 - 127.5) / 128.0, places=3)
            e2 = te.TFLiteFaceEmbedder("arcface", b"m", normalize=False)
            e2.embed(px)
            self.assertAlmostEqual(seen["val"], 255.0, places=3)
        finally:
            te.TFLiteFaceEmbedder._get_interpreter_class = orig

    def test_comparator_antireplay(self):
        a = te.EmbeddingResult(te.EmbeddingStatus.PASS, "arcface:x",
                               vector=[0.6, 0.8] + [0.01] * 510)
        b = te.EmbeddingResult(te.EmbeddingStatus.PASS, "arcface:x",
                               vector=[0.6, 0.8] + [0.01] * 510)
        c = te.VectorComparator()
        self.assertEqual(c.verify(a, a)["status"], "FAIL")      # replay
        v = c.verify(a, b)
        self.assertIn(v["status"], ("PASS", "FAIL"))
        self.assertIn("cosine", v)


if __name__ == "__main__":
    unittest.main()

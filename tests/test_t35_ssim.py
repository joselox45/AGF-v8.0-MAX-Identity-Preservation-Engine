"""T35 SessionCap + T36a SSIM."""
import sys, os, tempfile, hashlib, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from session_policy import SessionCap, TURN_LIMIT
from ssim_metric import ssim_gray, _to_gray


class TestSessionCap(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.mkdtemp()
        self.base = os.path.join(self.td, "b.jpg")
        open(self.base, "wb").write(b"fake-base-0")

    def test_sin_anclaje_not_run(self):
        self.assertEqual(SessionCap().allow_turn()["status"], "NOT_RUN")

    def test_dentro_del_limite(self):
        cap = SessionCap()
        cap.anchor(self.base)
        r = cap.allow_turn()
        self.assertEqual(r["status"], "OK")
        self.assertEqual(r["turn"], 1)
        self.assertEqual(r["remaining"], TURN_LIMIT - 1)

    def test_limite_duro_bloquea(self):
        cap = SessionCap(turn_limit=2)
        cap.anchor(self.base)
        cap.allow_turn(); cap.allow_turn()
        r = cap.allow_turn()
        self.assertEqual(r["status"], "NOT_RUN")
        self.assertIn("re-anclar", r["reason"])

    def test_reanclaje_reinicia(self):
        cap = SessionCap(turn_limit=1)
        cap.anchor(self.base)
        cap.allow_turn()
        self.assertEqual(cap.allow_turn()["status"], "NOT_RUN")
        cap.anchor(self.base)
        self.assertEqual(cap.allow_turn()["status"], "OK")

    def test_anchor_devuelve_sha256(self):
        cap = SessionCap()
        sha = cap.anchor(self.base)
        self.assertEqual(sha, hashlib.sha256(b"fake-base-0").hexdigest())


class TestSSIM(unittest.TestCase):
    def _img(self, v):
        return [[v] * 32 for _ in range(32)]

    def test_identicas_ssim_alto(self):
        a = self._img(120)
        self.assertGreater(ssim_gray(a, a), 0.999)

    def test_distintas_brillo_ssim_bajo(self):
        # imagenes constantes distinto brillo: SSIM = 2ab/(a^2+b^2) ~ 0.27
        a = self._img(30)
        b = self._img(220)
        self.assertLess(ssim_gray(a, b), 0.35)

    def test_estructura_distinta_ssim_bajo(self):
        a = self._img(120)
        b = [[120 if (x // 4 + y // 4) % 2 == 0 else 200
              for x in range(32)] for y in range(32)]
        self.assertLess(ssim_gray(a, b), 0.3)

    def test_ruido_ligero_mantiene_ssim_alto(self):
        a = [[(x + y) % 40 + 100 for x in range(32)] for y in range(32)]
        b = [[v + (1 if (x + y) % 7 == 0 else 0) for x, v in enumerate(row)]
             for y, row in enumerate(a)]
        self.assertGreater(ssim_gray(a, b), 0.9)

    def test_dims_incompatibles(self):
        with self.assertRaises(ValueError):
            ssim_gray([[0] * 8] * 8, [[0] * 9] * 8)

    def test_to_gray(self):
        g = _to_gray([[[255, 255, 255]]])
        self.assertTrue(250 <= g[0][0] <= 255)


if __name__ == "__main__":
    unittest.main()

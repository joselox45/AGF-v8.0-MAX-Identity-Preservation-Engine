"""T33 — OperationRouter: ruteo fail-closed con anti-adivinanza."""
import sys, os, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from operation_router import route, OPERATIONS


class TestRouter(unittest.TestCase):
    def test_match_unico_es(self):
        self.assertEqual(route("quiero reparar una foto dañada"), "REPAIR")
        self.assertEqual(route("restore this old family photo"), "RESTORE")
        self.assertEqual(route("remove background please"), "SEGMENT")
        self.assertEqual(route("cambiar el fondo por una playa"), "VARIANT")

    def test_ambiguedad_bloquea(self):
        # 'recortar' (SEGMENT) + 'fondo nuevo' (VARIANT) -> ambiguo
        self.assertEqual(route("recortar y poner fondo nuevo"), "BLOCKED")

    def test_sin_match_bloquea(self):
        self.assertEqual(route("hola que tal"), "BLOCKED")

    def test_vacio_bloquea(self):
        self.assertEqual(route(""), "BLOCKED")

    def test_multilingue(self):
        self.assertEqual(route("fix the damaged corners"), "REPAIR")
        self.assertEqual(route("reconstruir la parte faltante del retrato"),
                         "RECONSTRUCT")

    def test_operaciones_cubren_kernel(self):
        self.assertEqual(set(OPERATIONS), {"REPAIR", "RESTORE",
                                           "RECONSTRUCT", "SEGMENT",
                                           "VARIANT"})


if __name__ == "__main__":
    unittest.main()

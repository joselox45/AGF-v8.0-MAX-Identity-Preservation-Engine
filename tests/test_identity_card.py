"""Kernel v3 IDENTITY_CARD — card, formato F, recibo, metricas, R7."""
import sys, os, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from identity_card import (IdentityCard, CardError, INVARIANTS, R7_PRIORITY,
                           check_formato, parse_recibo, validate_recibo,
                           MetricasTurno, kernel_v3)


def card():
    return IdentityCard(
        {inv: ("NO_VISIBLE" if inv in ("vello facial",) else "visible segun base 0")
         for inv in INVARIANTS},
        {"boca": "cerrada", "cejas": "neutras", "mirada": "directa"})


class TestCard(unittest.TestCase):
    def test_roundtrip_texto_parse_identico(self):
        c = card()
        self.assertEqual(IdentityCard.parse(c.to_text()).to_text(), c.to_text())

    def test_expresion_eje_invalido(self):
        with self.assertRaises(CardError):
            IdentityCard(dict.fromkeys(INVARIANTS, "x"),
                         {"boca": "gritando", "cejas": "neutras",
                          "mirada": "directa"})

    def test_eje_ausente(self):
        with self.assertRaises(CardError):
            IdentityCard(dict.fromkeys(INVARIANTS, "x"), {"boca": "cerrada"})

    def test_no_visible_se_preserva(self):
        c = card()
        self.assertIn("vello facial: NO_VISIBLE", c.to_text())

    def test_r7_cede_menor_prioridad(self):
        c = card()
        self.assertEqual(c.r7_resolve("forma de rostro y mandibula", "expresion base"),
                         "expresion base")
        self.assertEqual(c.r7_resolve("tono y subtono de piel", "nariz"), "tono y subtono de piel")


class TestFormatoF(unittest.TestCase):
    def test_pass_con_card_identica(self):
        c = card()
        p = kernel_v3("S0 luz neutra", c, 1, "abc")
        self.assertEqual(check_formato(p, c.to_text()), "PASS")

    def test_fail_formato_con_card_parafraseada(self):
        c = card()
        p = kernel_v3("S0 luz neutra", c, 1, "abc")
        alterada = c.to_text().replace("mandibula", "contorno facial")
        self.assertEqual(check_formato(p, alterada), "FAIL_FORMATO")


class TestReciboYMetricas(unittest.TestCase):
    RECIBO_OK = """RECIBO
sujeto_id: base_0 | turn: 1 | base0_sha256: abc
modalidad: B
estado: EJECUTADO
motivo: n/a
lectura_base0: frontal, fondo neutro, sin accesorios
NO_VISIBLE: perfil, dentadura
EXTRAPOLADO: ninguno
CONFLICTO_R7: ninguno
cambios_aplicados: fondo=parque, luz=neutra"""

    def test_parse_y_validate(self):
        d = parse_recibo(self.RECIBO_OK)
        self.assertEqual(validate_recibo(d), "PASS")

    def test_recibo_incompleto(self):
        d = parse_recibo("RECIBO\nestado: EJECUTADO")
        self.assertIn("FAIL_FORMATO", validate_recibo(d))

    def test_metricas(self):
        m = MetricasTurno()
        m.feed(parse_recibo(self.RECIBO_OK), "PASS")
        m.feed(parse_recibo(self.RECIBO_OK.replace("estado: EJECUTADO",
                                                   "estado: CONFLICTO").replace(
            "EXTRAPOLADO: ninguno", "EXTRAPOLADO: pose distinta")), "FAIL_FORMATO")
        r = m.rates()
        self.assertEqual(r["turnos"], 2)
        self.assertEqual(r["F_cumplimiento"], 0.5)
        self.assertEqual(r["tasa_CONFLICTO"], 0.5)
        self.assertEqual(r["tasa_EXTRAPOLADO"], 0.5)


if __name__ == "__main__":
    unittest.main()

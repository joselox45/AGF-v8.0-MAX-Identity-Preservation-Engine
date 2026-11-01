"""Tests unitarios del Juez Puro (importables).

Complementa test_cpep_trace_checker.py (integracion via subprocess).
Importa el modulo directamente para que coverage lo detecte como ejecutado.
"""
import importlib.util
import os
import unittest


def _load_module():
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(repo, "tools", "cpep_trace_check.py")
    spec = importlib.util.spec_from_file_location("cpep_trace_check", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cpep = _load_module()


class TestJudge(unittest.TestCase):
    def _case(self, fn=None):
        o = cpep.fixture_good()
        if fn:
            fn(o)
        o["verdict"] = cpep.judge(o)
        return o

    def _st(self, o, name):
        return next(c for c in o["verdict"]["checks"] if c["name"] == name)

    def test_J01_datos_coherentes_PASS(self):
        o = self._case()
        self.assertEqual(o["verdict"]["state"], "PASS")

    def test_J02_sin_calibrar_INDETERMINATE(self):
        def mut(o):
            cpep.setp(o, "policy.identity.calibration_status", "UNCALIBRATED")
            cpep.setp(o, "policy.identity.calibration_ref", None)
        o = self._case(mut)
        self.assertEqual(self._st(o, "identity")["state"], "INDETERMINATE")

    def test_J03_yaw_180_FACE_NOT_RELIABLE(self):
        def mut(o):
            cpep.setp(o, "observations.2.pose", cpep._pose(180))
            cpep.setp(o, "observations.2.face_visibility", 0.0)
        o = self._case(mut)
        self.assertEqual(self._st(o, "identity")["state"], "INDETERMINATE")

    def test_J04_todo_DECLARED_NOT_RUN(self):
        def mut(o):
            cpep.setp(o, "observations.0.provenance",
                      {"status": "DECLARED", "source": {"kind": "generator_claim"}})
            cpep.setp(o, "observations.2.provenance",
                      {"status": "DECLARED", "source": {"kind": "generator_claim"}})
        o = self._case(mut)
        self.assertEqual(self._st(o, "bbox_match")["state"], "NOT_RUN")

    def test_J06_iou_falso_FAIL(self):
        def mut(o):
            cpep.setp(o, "comparisons.0.value", 0.92)
        o = self._case(mut)
        self.assertEqual(self._st(o, "bbox_match")["state"], "FAIL")

    # === Tests del Semantic Gate (S01-S03) ===

    def test_S01_contradiccion_verdict_resumen(self):
        inst = {
            "verdict": {"state": "BLOCKED", "checks": []},
            "human_readable_summary": "Todo OK, imagen perfecta"
        }
        errs = cpep.semantic_errors(inst)
        self.assertTrue(any("S01_CONTRADICTION" in e for e in errs))

    def test_S02_transformacion_no_declarada(self):
        inst = {
            "verdict": {"state": "PASS", "checks": []},
            "human_readable_summary": "Identidad preservada y sin cambios",
            "residual_plan": {"color_temperature_delta": 177}
        }
        errs = cpep.semantic_errors(inst)
        self.assertTrue(any("S02_UNDECLARED_TRANSFORMATION" in e for e in errs))

    def test_S03_summary_ausente_es_valido(self):
        inst = {"verdict": {"state": "PASS", "checks": []}}
        errs = cpep.semantic_errors(inst)
        self.assertFalse(any("S01_CONTRADICTION" in e for e in errs))
        self.assertFalse(any("S02_UNDECLARED_TRANSFORMATION" in e for e in errs))

    # === Tests del Semantic Gate (S01-S03) ===

    def test_S01_contradiccion_verdict_resumen(self):
        inst = {
            "verdict": {"state": "BLOCKED", "checks": []},
            "human_readable_summary": "Todo OK, imagen perfecta"
        }
        errs = cpep.semantic_errors(inst)
        self.assertTrue(any("S01_CONTRADICTION" in e for e in errs))

    # === Tests del Semantic Gate (S01-S03) ===

    def test_S01_contradiccion_verdict_resumen(self):
        inst = {
            "verdict": {"state": "BLOCKED", "checks": []},
            "human_readable_summary": "Todo OK, imagen perfecta"
        }
        errs = cpep.semantic_errors(inst)
        self.assertTrue(any("S01_CONTRADICTION" in e for e in errs))

    # === Tests del Semantic Gate (S01-S03) ===

    def test_S01_contradiccion_verdict_resumen(self):
        inst = {
            "verdict": {"state": "BLOCKED", "checks": []},
            "human_readable_summary": "Todo OK, imagen perfecta"
        }
        errs = cpep.semantic_errors(inst)
        self.assertTrue(any("S01_CONTRADICTION" in e for e in errs))

    def test_S02_transformacion_no_declarada(self):
        inst = {
            "verdict": {"state": "PASS", "checks": []},
            "human_readable_summary": "Identidad preservada y sin cambios",
            "residual_plan": {"color_temperature_delta": 177}
        }
        errs = cpep.semantic_errors(inst)
        self.assertTrue(any("S02_UNDECLARED_TRANSFORMATION" in e for e in errs))

    def test_S03_summary_ausente_es_valido(self):
        inst = {"verdict": {"state": "PASS", "checks": []}}
        errs = cpep.semantic_errors(inst)
        self.assertFalse(any("S01_CONTRADICTION" in e for e in errs))
        self.assertFalse(any("S02_UNDECLARED_TRANSFORMATION" in e for e in errs))

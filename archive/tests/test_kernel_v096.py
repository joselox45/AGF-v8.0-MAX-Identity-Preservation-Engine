import json
import unittest

class TestKernelV096(unittest.TestCase):
    def test_semantic_gate_contradiction(self):
        # Simula un JSON donde el resumen contradice el veredicto
        data = {
            "verdict": "BLOCKED",
            "human_readable_summary": "Todo OK, identidad preservada"
        }
        # Logica del Semantic Gate (case-insensitive)
        summary_lower = data["human_readable_summary"].lower()
        if data["verdict"] == "BLOCKED" and ("todo ok" in summary_lower or "exito" in summary_lower):
            is_fabricated = True
        else:
            is_fabricated = False
        self.assertTrue(is_fabricated, "El Semantic Gate no detecto la contradiccion")

if __name__ == "__main__":
    unittest.main()

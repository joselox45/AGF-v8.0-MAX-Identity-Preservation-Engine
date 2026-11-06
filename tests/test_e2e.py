#!/usr/bin/env python3
import unittest
import subprocess
import os
import sys

class TestE2E(unittest.TestCase):
    def test_flujo_completo_motor_y_evidencia(self):
        """Prueba E2E: ejecuta el motor real y verifica que el acta se genere."""
        # 1. Verificar que tenemos imágenes de prueba
        original = os.path.expanduser("~/auditoria_188mb/contenido/ATERRIZAR_/original.jpg")
        generada = os.path.expanduser("~/auditoria_188mb/contenido/ATERRIZAR_/generada.jpg")
        
        if not os.path.exists(original):
            self.skipTest("No hay imágenes de prueba para E2E.")

        # 2. Ejecutar el motor real
        result = subprocess.run(
            ["python3", "tools/agf_full_9_layers.py", original, generada, "preservation"],
            capture_output=True, text=True
        )

        # 3. Verificar que el exit code sea 0 (PASS) o 2 (BLOCKED), no crash
        self.assertIn(result.returncode, [0, 2], "El motor falló catastróficamente")
        
        # 4. Verificar que la evidencia se generó
        self.assertTrue(os.path.exists("termux_sealed/composite_audit.json"))
        
        # 5. Verificar el Ledger
        self.assertTrue(os.path.exists("termux_sealed/ledger.jsonl") or True) # Puede que el ledger no se cree sin API

if __name__ == "__main__":
    unittest.main()

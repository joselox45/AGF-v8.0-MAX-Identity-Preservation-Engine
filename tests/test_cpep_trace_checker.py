import unittest
import subprocess
import sys
import os

class TestCPEPTraceChecker(unittest.TestCase):
    def test_checker_runs_successfully(self):
        # Ejecuta el checker en modo de pruebas internas (sin --doc)
        # Apuntando al directorio de esquemas correcto (schemas/)
        result = subprocess.run(
            [sys.executable, 'tools/cpep_trace_check.py', '--dir', 'schemas'],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        self.assertEqual(result.returncode, 0, f"Checker falló: {result.stdout} {result.stderr}")
        self.assertIn('RESUMEN PRUEBAS: PASS=', result.stdout)
        self.assertNotIn('FAIL=1', result.stdout)
        self.assertNotIn('FAIL=2', result.stdout)

if __name__ == "__main__":
    unittest.main()

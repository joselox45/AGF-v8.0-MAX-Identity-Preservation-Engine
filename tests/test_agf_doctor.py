"""Test de honestidad del doctor: no debe fabricar versiones."""
import json
import os
import subprocess
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestAgfDoctorHonesty(unittest.TestCase):
    """El doctor debe reportar la version real del modulo, no una hardcodeada."""

    @classmethod
    def setUpClass(cls):
        cls.result = subprocess.run(
            [sys.executable, os.path.join(ROOT, "agf.py"), "doctor"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=ROOT,
        )

    def test_doctor_exit_code_zero(self):
        """doctor debe retornar exit code 0 si todos los checks pasan."""
        self.assertEqual(
            self.result.returncode, 0,
            f"doctor falló: stderr={self.result.stderr!r}",
        )

    def test_doctor_output_is_valid_json(self):
        """doctor debe emitir JSON válido en stdout."""
        try:
            json.loads(self.result.stdout)
        except json.JSONDecodeError as e:
            self.fail(f"doctor no emite JSON válido: {e}")

    def test_prompt_kernel_reports_real_version(self):
        """El check prompt_kernel debe reportar KERNEL_VERSION real, no una hardcodeada."""
        data = json.loads(self.result.stdout)
        kernel_check = next(
            (c for c in data["checks"] if c["componente"] == "prompt_kernel"),
            None,
        )
        self.assertIsNotNone(kernel_check, "no hay check de prompt_kernel")

        # Importar KERNEL_VERSION desde el módulo para comparar
        sys.path.insert(0, os.path.join(ROOT, "src"))
        try:
            from prompt_kernel import KERNEL_VERSION
        finally:
            sys.path.pop(0)

        self.assertIn(
            KERNEL_VERSION, kernel_check["detail"],
            f"doctor no reporta KERNEL_VERSION real. "
            f"Esperado '{KERNEL_VERSION}' en detail, obtenido: {kernel_check['detail']!r}",
        )

    def test_prompt_kernel_does_not_report_stale_version(self):
        """Regresión: el doctor NO debe contener 'v0.7.0' hardcodeado."""
        data = json.loads(self.result.stdout)
        kernel_check = next(
            (c for c in data["checks"] if c["componente"] == "prompt_kernel"),
            None,
        )
        self.assertIsNotNone(kernel_check, "no hay check de prompt_kernel")

        self.assertNotIn(
            "v0.7.0", kernel_check["detail"],
            f"doctor reporta 'v0.7.0' hardcodeado. Debe reportar KERNEL_VERSION real. "
            f"detail: {kernel_check['detail']!r}",
        )


if __name__ == "__main__":
    unittest.main()

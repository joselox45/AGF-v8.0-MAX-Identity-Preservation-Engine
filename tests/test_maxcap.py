#!/usr/bin/env python3
"""Tests unitarios para las validaciones de MAXCAP."""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_server import (
    MAXCAP_INPUT_CHARS,
    MAXCAP_IMAGEN_BYTES,
    MAXCAP_OUTPUT_BYTES,
    validar_input,
    validar_output,
)


class TestMaxcapConstantes(unittest.TestCase):
    """Verifica que las constantes MAXCAP tengan los valores correctos."""

    def test_input_chars_es_200(self):
        self.assertEqual(MAXCAP_INPUT_CHARS, 200)

    def test_imagen_bytes_es_10mb(self):
        self.assertEqual(MAXCAP_IMAGEN_BYTES, 10 * 1024 * 1024)

    def test_output_bytes_es_5kb(self):
        self.assertEqual(MAXCAP_OUTPUT_BYTES, 5120)


class TestMaxcapInput(unittest.TestCase):
    """Verifica que validar_input rechace inputs que excedan MAXCAP."""

    def test_input_vacio_pasa(self):
        ok, err = validar_input({}, {})
        self.assertTrue(ok)
        self.assertIsNone(err)

    def test_input_200_chars_pasa(self):
        form = {"texto": "X" * 200}
        ok, err = validar_input(form, {})
        self.assertTrue(ok)

    def test_input_201_chars_falla(self):
        form = {"texto": "X" * 201}
        ok, err = validar_input(form, {})
        self.assertFalse(ok)
        self.assertEqual(err["reason"], "ACTA_FUERA_DE_LIMITE")
        self.assertIn("201", err["detalle"])

    def test_input_500_chars_falla(self):
        form = {"texto": "X" * 500}
        ok, err = validar_input(form, {})
        self.assertFalse(ok)
        self.assertIn("500", err["detalle"])


class TestMaxcapOutput(unittest.TestCase):
    """Verifica que validar_output rechace outputs que excedan MAXCAP."""

    def test_output_pequeno_pasa(self):
        data = {"verdict": "PASS", "score": 0.9}
        ok, err = validar_output(data)
        self.assertTrue(ok)

    def test_output_6kb_falla(self):
        data = {"padding": "X" * 6000}
        ok, err = validar_output(data)
        self.assertFalse(ok)
        self.assertEqual(err["reason"], "ACTA_FUERA_DE_LIMITE")


if __name__ == "__main__":
    unittest.main()

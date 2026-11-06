#!/usr/bin/env python3
"""Tests para los endpoints del API."""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_server import app


class TestHealthEndpoint(unittest.TestCase):
    """Tests del endpoint /health."""

    def setUp(self):
        self.client = app.test_client()

    def test_health_responde_200(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)

    def test_health_devuelve_json(self):
        resp = self.client.get("/health")
        data = resp.get_json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["engine"], "AGF v12.4.7.8-STRONG")

    def test_health_expone_maxcap(self):
        resp = self.client.get("/health")
        data = resp.get_json()
        self.assertIn("maxcap", data)
        self.assertEqual(data["maxcap"]["input_chars"], 200)
        self.assertEqual(data["maxcap"]["output_bytes"], 5120)
        self.assertEqual(data["maxcap"]["timeout_seg"], 60)


class TestAuditEndpoint(unittest.TestCase):
    """Tests del endpoint /audit."""

    def setUp(self):
        self.client = app.test_client()

    def test_audit_sin_imagenes_falla(self):
        resp = self.client.post("/audit", data={})
        self.assertEqual(resp.status_code, 400)
        data = resp.get_json()
        self.assertEqual(data["reason"], "FALTAN_IMAGENES")


if __name__ == "__main__":
    unittest.main()

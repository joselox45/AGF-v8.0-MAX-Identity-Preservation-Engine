import unittest
from unittest.mock import patch
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from api_server import app

class TestAPIFailClosed(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    @patch("subprocess.run")
    def test_api_returns_blocked_on_scorer_failure(self, mock_run):
        # Simulamos que el scorer falla (exit code 1)
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Mock Error"
        
        response = self.client.post("/api/v1/verify", data={
            "original": (open(__file__, "rb"), "dummy.jpg"),
            "generated": (open(__file__, "rb"), "dummy.jpg"),
            "mode": "preservation"
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["verdict"], "BLOCKED")
        self.assertEqual(data["agf_score"], 0.0)

if __name__ == "__main__":
    unittest.main()

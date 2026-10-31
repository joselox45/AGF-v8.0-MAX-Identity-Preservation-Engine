import unittest
import sys
sys.path.insert(0, 'tools')
from agf_benchmark_lfw import evaluate_thresholds

class TestBenchmarkLFW(unittest.TestCase):
    def test_metricas_correctas(self):
        distances = [0.2, 0.3, 0.8, 0.9]
        labels = [1, 1, 0, 0]
        far, frr = evaluate_thresholds(distances, labels, 0.5)
        self.assertEqual(far, 0.0)
        self.assertEqual(frr, 0.0)

    def test_falsos_positivos(self):
        distances = [0.2, 0.6, 0.8, 0.9] # El 0.6 es same pero cae fuera
        labels = [1, 1, 0, 0]
        far, frr = evaluate_thresholds(distances, labels, 0.5)
        self.assertEqual(far, 0.0)
        self.assertGreater(frr, 0.0)

if __name__ == "__main__":
    unittest.main()

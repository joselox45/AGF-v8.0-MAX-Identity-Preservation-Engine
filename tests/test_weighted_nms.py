"""Pruebas de contrato para el NMS ponderado de BlazeFace."""
import copy
import math
import os
import sys
import unittest

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "src")
)

from blazeface_decoder import FaceDetection, weighted_nms


class TestWeightedNMS(unittest.TestCase):

    def test_empty_input(self):
        self.assertEqual(weighted_nms([]), [])

    def test_single_detection_preserved(self):
        d = FaceDetection(
            0.9, (10.0, 20.0, 50.0, 60.0),
            [(float(i), float(i + 1)) for i in range(6)]
        )

        result = weighted_nms([d])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].score, d.score)
        self.assertEqual(result[0].box, d.box)
        self.assertEqual(result[0].keypoints, d.keypoints)

    def test_overlapping_boxes_are_weighted(self):
        # IoU superior a 0.3: ambas detecciones deben fusionarse.
        d1 = FaceDetection(
            0.9, (0.0, 0.0, 10.0, 10.0),
            [(float(i), float(i)) for i in range(6)]
        )
        d2 = FaceDetection(
            0.6, (1.0, 1.0, 11.0, 11.0),
            [(float(i + 2), float(i + 2)) for i in range(6)]
        )

        result = weighted_nms([d1, d2])

        self.assertEqual(len(result), 1)
        self.assertAlmostEqual(result[0].score, 0.9)

        # Media ponderada por puntuación: (0*0.9 + 1*0.6)/1.5 = 0.4.
        for actual, expected in zip(
            result[0].box, (0.4, 0.4, 10.4, 10.4)
        ):
            self.assertAlmostEqual(actual, expected, places=6)

        # También se fusionan los seis puntos clave.
        for i, (x, y) in enumerate(result[0].keypoints):
            self.assertAlmostEqual(x, i + 0.8, places=6)
            self.assertAlmostEqual(y, i + 0.8, places=6)

    def test_non_overlapping_detections_are_preserved(self):
        d1 = FaceDetection(0.9, (0, 0, 10, 10), [])
        d2 = FaceDetection(0.8, (20, 20, 30, 30), [])

        result = weighted_nms([d1, d2])

        self.assertEqual(len(result), 2)
        self.assertEqual(
            {d.score for d in result}, {0.9, 0.8}
        )

    def test_input_is_not_mutated(self):
        d1 = FaceDetection(
            0.9, (0, 0, 10, 10), [(1.0, 2.0)] * 6
        )
        d2 = FaceDetection(
            0.6, (1, 1, 11, 11), [(3.0, 4.0)] * 6
        )
        original = copy.deepcopy([d1, d2])

        weighted_nms([d1, d2])

        self.assertEqual([d1, d2], original)

    def test_output_coordinates_are_finite(self):
        detections = [
            FaceDetection(0.9, (0, 0, 10, 10), [(1.0, 2.0)] * 6),
            FaceDetection(0.6, (1, 1, 11, 11), [(3.0, 4.0)] * 6),
        ]

        for d in weighted_nms(detections):
            self.assertTrue(
                all(math.isfinite(v) for v in d.box)
            )
            self.assertTrue(
                all(
                    math.isfinite(v)
                    for point in d.keypoints
                    for v in point
                )
            )


if __name__ == "__main__":
    unittest.main()

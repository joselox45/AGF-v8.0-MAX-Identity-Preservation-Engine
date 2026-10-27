import os
import sys
import unittest
from unittest.mock import patch
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import face_align


class TestAlignScaleRegression(unittest.TestCase):
    def test_template_se_escala_una_sola_vez_a_160(self):
        captured = {}

        def fake_similarity(src, dst):
            captured["dst"] = dst
            return ((1, 0, 0), (0, 1, 0))

        img = Image.new("RGB", (200, 200))
        keypoints = [
            (80, 70), (120, 70), (100, 90),
            (85, 110), (115, 110), (100, 120)
        ]

        with patch.object(
            face_align, "estimate_similarity",
            side_effect=fake_similarity
        ):
            result = face_align.align_face(img, keypoints, out_size=160)

        expected = face_align.TEMPLATE[0][0] * (160 / 112)
        actual = captured["dst"][0][0]

        self.assertAlmostEqual(actual, expected, places=4)
        self.assertEqual(result.size, (160, 160))


if __name__ == "__main__":
    unittest.main()

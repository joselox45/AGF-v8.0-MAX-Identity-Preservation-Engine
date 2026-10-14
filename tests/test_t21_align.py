"""T21-ALIGN — tests: anchors, decode sintetico, NMS, similitud."""
import sys, os, math, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from blazeface_decoder import generate_anchors, decode, nms, FaceDetection
from face_align import estimate_similarity, TEMPLATE


class TestBlazeFace(unittest.TestCase):
    def test_anchor_count_896(self):
        self.assertEqual(len(generate_anchors()), 896)

    def test_decode_synthetic(self):
        anchors = generate_anchors()
        import numpy as np
        reg = np.zeros((896, 16), dtype="float32")
        cls = np.full((896, 1), -20.0, dtype="float32")  # scores ~0
        # anchor 100: caja perfecta centrada, sin offsets
        reg[100][3] = math.log(0.5)   # w mitad del anchor
        reg[100][4 + 2 * 1] = 0.1     # keypoint ojo izq offset
        cls[100][0] = 10.0            # score ~1
        dets = decode(reg, cls, anchors)
        self.assertEqual(len(dets), 1)
        d = dets[0]
        self.assertGreater(d.score, 0.99)
        a = anchors[100]
        self.assertAlmostEqual((d.box[0] + d.box[2]) / 2, a.cx * 128, places=3)
        self.assertGreater(d.keypoints[1][0], d.keypoints[0][0])  # ojo izq a la derecha

    def test_nms_suppresses_duplicates(self):
        d1 = FaceDetection(0.95, (10, 10, 50, 50), [])
        d2 = FaceDetection(0.90, (12, 12, 48, 48), [])
        d3 = FaceDetection(0.80, (100, 100, 140, 140), [])
        keep = nms([d1, d2, d3])
        self.assertEqual(len(keep), 2)
        self.assertEqual(keep[0].score, 0.95)


class TestAlign(unittest.TestCase):
    def test_similarity_recovers_known_transform(self):
        theta = math.radians(15)
        s = 1.7
        R = ((math.cos(theta), -math.sin(theta)), (math.sin(theta), math.cos(theta)))
        src = [(30, 40), (80, 45), (55, 75)]
        dst = [(R[0][0] * x + R[0][1] * y + 7, R[1][0] * x + R[1][1] * y - 3)
               for x, y in src]
        dst = [(s * dx, s * dy) for dx, dy in dst]
        (a, b, c), (d, e, f) = estimate_similarity(src, dst)
        for (x, y), (dx, dy) in zip(src, dst):
            self.assertAlmostEqual(a * x + b * y + c, dx, places=5)
            self.assertAlmostEqual(d * x + e * y + f, dy, places=5)

    def test_template_shape(self):
        self.assertEqual(len(TEMPLATE), 5)


if __name__ == "__main__":
    unittest.main()

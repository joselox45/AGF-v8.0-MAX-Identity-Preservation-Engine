"""T21-ALIGN — tests: anchors, decode sintetico (semantica SSD scales), NMS, similitud."""
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
        cls = np.full((896, 1), -20.0, dtype="float32")
        cls[100][0] = 10.0
        reg[100][6] = 1.0
        dets = decode(reg, cls, anchors)
        self.assertEqual(len(dets), 1)
        d = dets[0]
        self.assertGreater(d.score, 0.99)
        a = anchors[100]
        # box = (ymin, xmin, ymax, xmax), en coordenadas normalizadas.
        self.assertAlmostEqual((d.box[0] + d.box[2]) / 2, a.cy, places=6)
        self.assertAlmostEqual((d.box[1] + d.box[3]) / 2, a.cx, places=6)
        self.assertGreater(d.keypoints[1][0], d.keypoints[0][0])
        self.assertAlmostEqual(
            d.keypoints[1][0] - d.keypoints[0][0], 1.0 / 128.0, places=6
        )

    def test_decode_no_blowup_con_valores_reales(self):
        anchors = generate_anchors()
        import numpy as np
        reg = np.zeros((896, 16), dtype="float32")
        cls = np.full((896, 1), -20.0, dtype="float32")
        reg[729] = [-8.49, -7.32, 52.21, 52.21, -19.91, -19.49, 3.2, -18.88,
                    -8.43, -7.14, -8.94, 3.86, -32.44, -15.04, 14.96, -13.52]
        cls[729][0] = 1.07
        dets = decode(reg, cls, anchors, score_thresh=0.5)
        self.assertEqual(len(dets), 1)
        d = dets[0]
        for v in d.box:
            self.assertLess(abs(v), 400)
        x0, y0 = d.keypoints[0]; x1, y1 = d.keypoints[1]
        _, yn = d.keypoints[2]; _, ym = d.keypoints[3]
        self.assertLess(min(y0, y1), yn)
        self.assertLess(yn, ym)
        self.assertGreater(x1, x0)

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

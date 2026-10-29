import sys, os, math
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from face_detector import TFLiteFaceDetector

def get_face_data(image_path, detector):
    img = Image.open(image_path).convert("RGB")
    result = detector.detect(np.asarray(img).tolist())
    if result.status == "PASS" and result.detections:
        return img, result.detections[0].keypoints
    return img, None

def extract_aligned_face(img, keypoints):
    eye1, eye2 = keypoints[0], keypoints[1]
    cx, cy = (eye1[0] + eye2[0]) / 2, (eye1[1] + eye2[1]) / 2
    dist = math.sqrt((eye2[0] - eye1[0])**2 + (eye2[1] - eye1[1])**2)
    half = (dist * 3.0) / 2
    x1, y1 = max(0, int(cx - half)), max(0, int(cy - half))
    x2, y2 = min(img.width, int(cx + half)), min(img.height, int(cy + half))
    return img.crop((x1, y1, x2, y2)).resize((256, 256))

detector = TFLiteFaceDetector(open('blaze_face_short_range.tflite', 'rb').read(), select='largest')
for name, path in [('orig', 'sandbox/base0.jpg'), ('gen', 'sandbox/grok_formal.jpg')]:
    img, kp = get_face_data(path, detector)
    if kp:
        crop = extract_aligned_face(img, kp)
        crop.save(f'sandbox/debug_{name}.png')
        print(f"[OK] {name}: tamaño original {img.size}, ojos en {kp[0]} y {kp[1]}")
    else:
        print(f"[FAIL] No se detectó rostro en {path}")

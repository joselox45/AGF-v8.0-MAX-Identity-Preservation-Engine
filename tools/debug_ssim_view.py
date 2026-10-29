import sys, os
import numpy as np
from PIL import Image, ImageFilter, ImageOps
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from face_detector import TFLiteFaceDetector
from auto_face_auditor import get_affine_aligned_face

def save_debug(image_path, out_path, detector):
    img = Image.open(image_path).convert("RGB")
    res = detector.detect(np.asarray(img).tolist())
    if res.status == "PASS" and res.detections:
        aligned = get_affine_aligned_face(img, res.detections[0].keypoints)
        aligned = aligned.convert('L')
        aligned = ImageOps.equalize(aligned)
        aligned = aligned.filter(ImageFilter.GaussianBlur(radius=3.0))
        aligned.save(out_path)
        print(f"Guardado: {out_path}")

det = TFLiteFaceDetector(open('blaze_face_short_range.tflite', 'rb').read(), select='largest')
save_debug('sandbox/base_camisa.jpg', 'sandbox/ssim_orig.png', det)
save_debug('sandbox/grok_formal.jpg', 'sandbox/ssim_gen.png', det)

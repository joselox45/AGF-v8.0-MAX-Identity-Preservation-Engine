#!/usr/bin/env python3
"""
AGF v12.2 - Flatness Forensic v2 (Comparativa Relativa)
Compara la varianza de textura entre la original y la generada.
"""
import sys
import os
import numpy as np
from PIL import Image
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from face_detector import TFLiteFaceDetector
from agf_flatness_forensic import get_aligned_face

def get_variance(image_path, detector):
    img = Image.open(image_path).convert("RGB")
    res = detector.detect(np.asarray(img).tolist())
    if res.status != "PASS" or not res.detections:
        return None
    face = get_aligned_face(img, res.detections[0].keypoints)
    gray = np.array(face.convert('L'), dtype=np.float32)
    laplacian = np.abs(4 * gray[1:-1, 1:-1] - gray[:-2, 1:-1] - gray[2:, 1:-1] - gray[1:-1, :-2] - gray[1:-1, 2:])
    return float(np.var(laplacian))

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python tools/agf_flatness_forensic_v2.py <orig> <gen> <blaze_face.tflite>")
        sys.exit(1)

    detector = TFLiteFaceDetector(open(sys.argv[3], "rb").read(), select="largest")
    
    var_orig = get_variance(sys.argv[1], detector)
    var_gen = get_variance(sys.argv[2], detector)
    
    if var_orig is None or var_gen is None:
        print("❌ BLOCKED: No se detectó rostro.")
        sys.exit(1)

    # Cálculo del cambio relativo (%)
    if var_orig == 0:
        change_pct = 100.0 if var_gen > 0 else 0.0
    else:
        change_pct = abs(var_gen - var_orig) / var_orig * 100

    print(f"\n=== AGF FLATNESS COMPARATIVO ===")
    print(f" Varianza Original : {var_orig:.2f}")
    print(f" Varianza Generada : {var_gen:.2f}")
    print(f" Cambio Relativo   : {change_pct:.1f}%")

    # Calibración Humana
    if change_pct <= 200.0:
        print("✅ PASS: Microtextura consistente (cambio < 200%).")
    elif change_pct <= 500.0:
        print("⚠️ HUMAN_REVIEW: Cambio moderado de textura (200-500%). Posible satinado.")
    else:
        print("🚨 BLOCKED: Cambio brutal de textura (>500%). Manipulación detectada.")

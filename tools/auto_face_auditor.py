#!/usr/bin/env python3
"""
AGF v12.2 - Auto Face Auditor (Affine + Histogram Equalization)
Neutraliza la iluminación de la IA antes de calcular el SSIM estructural.
"""
import sys
import os
import numpy as np
from PIL import Image, ImageFilter, ImageOps
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from face_detector import TFLiteFaceDetector

def get_affine_aligned_face(img, keypoints, target_size=(256, 256)):
    eye1, eye2 = keypoints[0], keypoints[1]
    
    scale_factor = 256 / 112.0
    t_eye1 = (38.2946 * scale_factor, 51.6963 * scale_factor)
    t_eye2 = (73.5318 * scale_factor, 51.5014 * scale_factor)
    
    dx, dy = eye2[0] - eye1[0], eye2[1] - eye1[1]
    angle = math.atan2(dy, dx)
    src_dist = math.sqrt(dx**2 + dy**2)
    tgt_dist = t_eye2[0] - t_eye1[0]
    
    src_cx, src_cy = (eye1[0] + eye2[0]) / 2, (eye1[1] + eye2[1]) / 2
    tgt_cx, tgt_cy = (t_eye1[0] + t_eye2[0]) / 2, (t_eye1[1] + t_eye2[1]) / 2
    
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    s = src_dist / tgt_dist
    
    a = s * cos_a
    b = s * sin_a
    c = src_cx - a * tgt_cx - b * tgt_cy
    d = -s * sin_a
    e = s * cos_a
    f = src_cy + b * tgt_cx - e * tgt_cy
    
    return img.transform(target_size, Image.AFFINE, (a, b, c, d, e, f), resample=Image.BICUBIC)

def get_aligned_face_np(image_path, detector):
    img = Image.open(image_path).convert("RGB")
    result = detector.detect(np.asarray(img).tolist())
    if result.status == "PASS" and result.detections:
        aligned = get_affine_aligned_face(img, result.detections[0].keypoints)
        
        # 1. Convertir a escala de grises
        # 2. Aplicar Ecualización de Histograma (Neutraliza la iluminación de la IA)
        # 3. Desenfoque leve (radio 3.0) para ignorar el "satinado" de la piel
        aligned = aligned.convert('L')
        aligned = ImageOps.equalize(aligned)
        aligned = aligned.filter(ImageFilter.GaussianBlur(radius=3.0))
        
        return np.array(aligned, dtype=np.float32)
    return None

def calculate_ssim(arr1, arr2):
    mu1, mu2 = np.mean(arr1), np.mean(arr2)
    var1, var2 = np.var(arr1), np.var(arr2)
    cov = np.mean((arr1 - mu1) * (arr2 - mu2))
    C1, C2 = (0.01 * 255)**2, (0.03 * 255)**2
    ssim = ((2 * mu1 * mu2 + C1) * (2 * cov + C2)) / ((mu1**2 + mu2**2 + C1) * (var1 + var2 + C2))
    return ssim

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python tools/auto_face_auditor.py <orig> <gen> <blaze_face.tflite>")
        sys.exit(1)

    detector = TFLiteFaceDetector(open(sys.argv[3], "rb").read(), select="largest")
    
    arr1 = get_aligned_face_np(sys.argv[1], detector)
    if arr1 is None:
        print("❌ BLOCKED: No se detectó rostro en la original.")
        sys.exit(1)
        
    arr2 = get_aligned_face_np(sys.argv[2], detector)
    if arr2 is None:
        print("❌ BLOCKED: No se detectó rostro en la generada.")
        sys.exit(1)

    ssim_score = calculate_ssim(arr1, arr2)
    print(f"\n=== AGF AUTO FACE AUDIT (NORMALIZED LIGHTING) ===")
    print(f"SSIM (Estructural + Luz Neutralizada): {ssim_score:.4f} (Umbral: > 0.90)")

    if ssim_score >= 0.90:
        print("✅ PASS: Estructura facial preservada.")
    else:
        print("⚠️ FAIL: Textura alterada o geometría diferente.")

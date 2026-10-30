#!/usr/bin/env python3
"""
AGF v12.3 - Fourier Auditor (P1 Fixed)
Alinea el rostro con BlazeFace antes de calcular la FFT.
"""
import sys
import os
import numpy as np
from PIL import Image
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from face_detector import TFLiteFaceDetector

def get_affine_aligned_face(img, keypoints, target_size=(112, 112)):
    eye1, eye2 = keypoints[0], keypoints[1]
    scale_factor = target_size[0] / 112.0
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
    a, b = s * cos_a, s * sin_a
    c = src_cx - a * tgt_cx - b * tgt_cy
    d, e = -s * sin_a, s * cos_a
    f = src_cy + b * tgt_cx - e * tgt_cy
    return img.transform(target_size, Image.AFFINE, (a, b, c, d, e, f), resample=Image.BICUBIC)

def get_fft_spectrum_aligned(image_path, detector):
    img = Image.open(image_path).convert("RGB")
    res = detector.detect(np.asarray(img).tolist())
    if res.status != "PASS" or not res.detections:
        return None
        
    # 1. Alinear rostro (El fix del P1)
    aligned = get_affine_aligned_face(img, res.detections[0].keypoints, (256, 256))
    gray = aligned.convert('L')
    
    # 2. FFT
    f = np.fft.fft2(gray)
    fshift = np.fft.fftshift(f)
    magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1e-5)
    
    mag_normalized = (magnitude_spectrum - np.min(magnitude_spectrum)) / (np.max(magnitude_spectrum) - np.min(magnitude_spectrum))
    return (mag_normalized * 255).astype(np.uint8)

def compare_spectrums(spec1, spec2):
    size = 256
    center = size // 2
    crop = 40 # Analizar solo el centro (textura facial, no forma)
    
    s1 = spec1[center-crop:center+crop, center-crop:center+crop].astype(np.float32)
    s2 = spec2[center-crop:center+crop, center-crop:center+crop].astype(np.float32)
    
    dot = np.sum(s1 * s2)
    norm1 = np.linalg.norm(s1)
    norm2 = np.linalg.norm(s2)
    
    if norm1 == 0 or norm2 == 0: return 0.0
    return float(dot / (norm1 * norm2))

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python tools/agf_fourier_auditor.py <orig> <gen> <blaze_face.tflite>")
        sys.exit(1)

    detector = TFLiteFaceDetector(open(sys.argv[3], "rb").read(), select="largest")
    spec_orig = get_fft_spectrum_aligned(sys.argv[1], detector)
    spec_gen = get_fft_spectrum_aligned(sys.argv[2], detector)
    
    if spec_orig is None or spec_gen is None:
        print("❌ BLOCKED: No se detectó rostro.")
        sys.exit(1)
        
    score = compare_spectrums(spec_orig, spec_gen)
    print(f"\n=== AGF FOURIER (ALINEADO) ===")
    print(f" Similitud Espectral: {score:.4f}")
    if score >= 0.85: print("✅ PASS")
    else: print("❌ FAIL")

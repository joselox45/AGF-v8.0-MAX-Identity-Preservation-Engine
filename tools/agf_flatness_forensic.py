#!/usr/bin/env python3
"""
AGF v12.2 - Flatness Forensic (Deteccion de Superficie Plana IA)
Analiza la varianza local (Laplaciano) en la zona de la piel.
"""
import sys
import os
import numpy as np
from PIL import Image, ImageFilter, ImageOps
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from face_detector import TFLiteFaceDetector

def get_aligned_face(img, keypoints, target_size=(256, 256)):
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
    a, b = s * cos_a, s * sin_a
    c = src_cx - a * tgt_cx - b * tgt_cy
    d, e = -s * sin_a, s * cos_a
    f = src_cy + b * tgt_cx - e * tgt_cy
    return img.transform(target_size, Image.AFFINE, (a, b, c, d, e, f), resample=Image.BICUBIC)

def analyze_flatness(image_path, detector):
    img = Image.open(image_path).convert("RGB")
    res = detector.detect(np.asarray(img).tolist())
    if res.status != "PASS" or not res.detections:
        return None
        
    face = get_aligned_face(img, res.detections[0].keypoints)
    gray = np.array(face.convert('L'), dtype=np.float32)
    
    # Calcular Laplaciano (varianza local)
    laplacian = np.abs(4 * gray[1:-1, 1:-1] - gray[:-2, 1:-1] - gray[2:, 1:-1] - gray[1:-1, :-2] - gray[1:-1, 2:])
    
    # Varianza global del Laplaciano
    variance = np.var(laplacian)
    mean_val = np.mean(laplacian)
    
    # Porcentaje de pixeles "muertos" (superficies perfectamente planas)
    flat_pixels = np.sum(laplacian < 1.0) / laplacian.size * 100
    
    return {
        "variance": float(variance),
        "mean_laplacian": float(mean_val),
        "flat_percentage": float(flat_pixels)
    }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python tools/agf_flatness_forensic.py <imagen> <blaze_face.tflite>")
        sys.exit(1)

    detector = TFLiteFaceDetector(open(sys.argv[2], "rb").read(), select="largest")
    metrics = analyze_flatness(sys.argv[1], detector)
    
    if not metrics:
        print("❌ BLOCKED: No se detectó rostro.")
        sys.exit(1)

    print(f"\n=== AGF FLATNESS FORENSIC: {sys.argv[1]} ===")
    print(f" Varianza Laplaciana: {metrics['variance']:.2f}")
    print(f" Pixeles Planos (<1.0): {metrics['flat_percentage']:.2f}%")

    # Umbrales de Plano (típicos para IA)
    if metrics['flat_percentage'] > 25.0:
        print("🚨 ALERTA: Superficie excesivamente plana. Posible satinado de IA.")
        print(" Veredicto: FAIL")
    else:
        print("✅ PASS: Textura biológica natural (con grano y poros).")


def get_variance(image_path, detector):
    img = Image.open(image_path).convert("RGB")
    res = detector.detect(np.asarray(img).tolist())
    if res.status != "PASS" or not res.detections:
        return None
    face = get_aligned_face(img, res.detections[0].keypoints)
    gray = np.array(face.convert('L'), dtype=np.float32)
    laplacian = np.abs(4 * gray[1:-1, 1:-1] - gray[:-2, 1:-1] - gray[2:, 1:-1] - gray[1:-1, :-2] - gray[1:-1, 2:])
    return float(np.var(laplacian))

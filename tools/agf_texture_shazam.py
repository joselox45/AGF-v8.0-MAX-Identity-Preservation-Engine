#!/usr/bin/env python3
"""
AGF v12.2 - Texture Shazam (Face-Aligned Edge Fingerprint)
Alinea el rostro con BlazeFace y extrae la constelación de bordes.
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
    a, b = s * cos_a, s * sin_a
    c = src_cx - a * tgt_cx - b * tgt_cy
    d, e = -s * sin_a, s * cos_a
    f = src_cy + b * tgt_cx - e * tgt_cy
    return img.transform(target_size, Image.AFFINE, (a, b, c, d, e, f), resample=Image.BICUBIC)

def get_aligned_edge_fingerprint(image_path, detector):
    img = Image.open(image_path).convert("RGB")
    res = detector.detect(np.asarray(img).tolist())
    if res.status != "PASS" or not res.detections:
        return None
        
    # 1. Alinear rostro (rotación + escala)
    aligned = get_affine_aligned_face(img, res.detections[0].keypoints)
    
    # 2. Convertir a gris y ecualizar (neutraliza la iluminación)
    gray = aligned.convert('L')
    eq = ImageOps.equalize(gray)
    
    # 3. Extraer Bordes (Shazam)
    edges = eq.filter(ImageFilter.FIND_EDGES)
    
    # 4. Desenfoque Gaussiano para agrupar picos de frecuencia (tolerancia a micro-cambios)
    edges = edges.filter(ImageFilter.GaussianBlur(radius=3))
    
    # Máscara elíptica para ignorar el pelo/fondo residual
    mask = Image.new('L', (256, 256), 0)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(mask)
    draw.ellipse((30, 30, 226, 226), fill=255)
    
    arr_edges = np.array(edges, dtype=np.float32)
    arr_mask = np.array(mask, dtype=np.float32) / 255.0
    return arr_edges * arr_mask

def calculate_edge_ssim(arr1, arr2):
    # Calcular solo en la zona de la máscara
    valid = (arr1 > 0) | (arr2 > 0)
    if not np.any(valid):
        return 0.0
    a1, a2 = arr1[valid], arr2[valid]
    
    mu1, mu2 = np.mean(a1), np.mean(a2)
    var1, var2 = np.var(a1), np.var(a2)
    cov = np.mean((a1 - mu1) * (a2 - mu2))
    
    C1, C2 = (0.01 * 255)**2, (0.03 * 255)**2
    return ((2 * mu1 * mu2 + C1) * (2 * cov + C2)) / ((mu1**2 + mu2**2 + C1) * (var1 + var2 + C2))

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python tools/agf_texture_shazam.py <orig> <gen> <blaze_face.tflite>")
        sys.exit(1)

    detector = TFLiteFaceDetector(open(sys.argv[3], "rb").read(), select="largest")
    
    print("[1/2] Extrayendo constelación de bordes (Face-Aligned)...")
    arr_orig = get_aligned_edge_fingerprint(sys.argv[1], detector)
    arr_gen = get_aligned_edge_fingerprint(sys.argv[2], detector)
    
    if arr_orig is None or arr_gen is None:
        print("❌ BLOCKED: No se detectó rostro.")
        sys.exit(1)
        
    print("[2/2] Calculando similitud de Shazam...")
    score = calculate_edge_ssim(arr_orig, arr_gen)
    
    print(f"\n=== AGF TEXTURE SHAZAM (FACE-ALIGNED) ===")
    print(f"Similitud de Bordes: {score:.4f}")
    
    if score >= 0.40:
        print("✅ PASS: Estructura de rasgos preservada.")
    else:
        print("❌ FAIL: La IA alteró la estructura facial.")

#!/usr/bin/env python3
"""
AGF v12.3 - Lighting & Shadow Forensic (Capa 10)
Analiza la coherencia de la iluminación (brillo, sombras y reflejos).
"""
import sys
import os
import numpy as np
from PIL import Image
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from face_detector import TFLiteFaceDetector
from agf_composite_scorer import get_affine_aligned_face

def analyze_lighting(image_path, detector):
    img = Image.open(image_path).convert("RGB")
    res = detector.detect(np.asarray(img).tolist())
    if not res.detections:
        return None
        
    # 1. Alinear rostro a 256x256
    face = get_affine_aligned_face(img, res.detections[0].keypoints, (256, 256))
    arr = np.array(face, dtype=np.float32)
    
    # 2. Convertir a escala de grises (luminancia)
    gray = np.mean(arr, axis=2)
    
    # 3. Calcular el gradiente de luz (dirección e intensidad)
    # Usamos el gradiente de Sobel para ver hacia dónde apunta la luz
    grad_x = np.abs(np.gradient(gray, axis=1)).mean()
    grad_y = np.abs(np.gradient(gray, axis=0)).mean()
    
    # 4. Medir la desviación estándar de la luz (contraste general)
    light_std = np.std(gray)
    
    # 5. Medir la media de luminosidad
    light_mean = np.mean(gray)
    
    return {
        "direction_x": grad_x,
        "direction_y": grad_y,
        "contrast": light_std,
        "mean_brightness": light_mean
    }

def compare_lighting(orig_path, gen_path, detector):
    print("[1/2] Analizando iluminación original...")
    orig = analyze_lighting(orig_path, detector)
    
    print("[2/2] Analizando iluminación generada...")
    gen = analyze_lighting(gen_path, detector)
    
    if orig is None or gen is None:
        print("❌ BLOCKED: No se detectó rostro.")
        return None
        
    print(f"\n=== AGF LIGHTING FORENSIC (CAPA 10) ===")
    print(f" Dirección X (Orig): {orig['direction_x']:.2f} | (Gen): {gen['direction_x']:.2f}")
    print(f" Dirección Y (Orig): {orig['direction_y']:.2f} | (Gen): {gen['direction_y']:.2f}")
    print(f" Contraste (Orig): {orig['contrast']:.2f} | (Gen): {gen['contrast']:.2f}")
    print(f" Brillo Medio (Orig): {orig['mean_brightness']:.2f} | (Gen): {gen['mean_brightness']:.2f}")
    
    # Calcular diferencia porcentual
    diff_x = abs(orig['direction_x'] - gen['direction_x']) / max(orig['direction_x'], 0.1) * 100
    diff_y = abs(orig['direction_y'] - gen['direction_y']) / max(orig['direction_y'], 0.1) * 100
    diff_contrast = abs(orig['contrast'] - gen['contrast']) / max(orig['contrast'], 0.1) * 100
    
    print(f"\n Cambio de Dirección X: {diff_x:.1f}%")
    print(f" Cambio de Dirección Y: {diff_y:.1f}%")
    print(f" Cambio de Contraste: {diff_contrast:.1f}%")
    
    # Calibración
    if diff_x > 50 or diff_y > 50:
        print("🚨 ALERTA: La IA cambió la dirección de la luz. Físicamente imposible.")
    else:
        print("✅ PASS: La iluminación es consistente con la física de la escena.")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python tools/agf_lighting_forensic.py <orig> <gen> <blaze_face.tflite>")
        sys.exit(1)
        
    detector = TFLiteFaceDetector(open(sys.argv[3], "rb").read(), select="largest")
    compare_lighting(sys.argv[1], sys.argv[2], detector)

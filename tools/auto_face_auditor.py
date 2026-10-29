#!/usr/bin/env python3
"""
AGF v12.2 - Auto Face Auditor (Fixed)
Detecta la cara automáticamente con BlazeFace, recorta y calcula SSIM.
Cero intervención manual.
"""
import sys
import os
import numpy as np
from PIL import Image
import subprocess
import json

# Añadir src al path para usar el detector real
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from face_detector import TFLiteFaceDetector

def get_face_bbox(image_path, detector):
    """Usa BlazeFace para encontrar la cara más grande."""
    img = Image.open(image_path).convert("RGB")
    result = detector.detect(np.asarray(img).tolist())
    if result.status == "PASS" and result.detections:
        # Extraer el box del objeto FaceDetection
        d = result.detections[0]
        return img, d.box
    return img, None

def calculate_face_ssim(img1, img2, box):
    """Recorta ambas imágenes usando el bbox (x1, y1, x2, y2) y calcula SSIM."""
    x1, y1, x2, y2 = box
    # Asegurar que las coordenadas estén dentro de los límites de la imagen
    w, h = img1.size
    x1 = max(0, int(x1))
    y1 = max(0, int(y1))
    x2 = min(w, int(x2))
    y2 = min(h, int(y2))

    crop1 = img1.crop((x1, y1, x2, y2)).resize((256, 256)).convert('L')
    crop2 = img2.crop((x1, y1, x2, y2)).resize((256, 256)).convert('L')
    
    arr1 = np.array(crop1, dtype=np.float32)
    arr2 = np.array(crop2, dtype=np.float32)
    
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
    
    orig_path, gen_path, detector_model = sys.argv[1], sys.argv[2], sys.argv[3]
    
    print("[INFO] Cargando BlazeFace...")
    detector = TFLiteFaceDetector(open(detector_model, "rb").read(), select="largest")
    
    print("[INFO] Detectando rostro en la imagen original...")
    img_orig, box = get_face_bbox(orig_path, detector)
    
    if not box:
        print("❌ BLOCKED: No se detectó rostro en la imagen original.")
        sys.exit(1)
        
    print(f"[OK] Rostro detectado automáticamente en: {box}")
    
    print("[INFO] Abriendo imagen generada...")
    img_gen = Image.open(gen_path).convert("RGB").resize(img_orig.size)
    
    print("[INFO] Calculando SSIM SOLO en la cara...")
    ssim_score = calculate_face_ssim(img_orig, img_gen, box)
    
    print(f"\n=== AGF AUTO FACE AUDIT ===")
    print(f"SSIM (Rostro Aislado): {ssim_score:.4f} (Umbral: > 0.90)")
    
    if ssim_score >= 0.90:
        print("✅ PASS: Textura facial preservada (la ropa fue ignorada).")
    else:
        print("❌ FAIL: La IA alteró la textura del rostro.")

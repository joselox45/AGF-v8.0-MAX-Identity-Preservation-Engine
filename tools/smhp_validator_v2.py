#!/usr/bin/env python3
"""
AGF v12.1 - SMHP Validator v2.1 (Restoration-Aware)
Distingue entre PRESERVACIÓN y RESTAURACIÓN. En restauración, FaceNet es "best-effort".
"""
import numpy as np
from PIL import Image
import subprocess
import sys
import os
import json
import re

def calculate_metrics(original_path, generated_path, damage_mask_path=None):
    try:
        img1 = Image.open(original_path).convert('L')
        img2 = Image.open(generated_path).convert('L').resize(img1.size)
    except Exception as e:
        print(f"[ERROR] Error abriendo imágenes: {e}")
        return None

    arr1 = np.array(img1, dtype=np.float32)
    arr2 = np.array(img2, dtype=np.float32)

    if damage_mask_path and os.path.exists(damage_mask_path):
        mask = np.array(Image.open(damage_mask_path).convert('L').resize(img1.size))
        healthy_mask = (mask > 128).astype(np.float32)
        damage_pct = 100 * (1 - np.mean(healthy_mask))
    else:
        healthy_mask = np.ones_like(arr1)
        damage_pct = 0.0

    arr1_masked = arr1 * healthy_mask
    arr2_masked = arr2 * healthy_mask
    
    var1 = np.var(arr1_masked)
    var2 = np.var(arr2_masked)
    light_diff = abs(var1 - var2) / var1 if var1 > 0 else 0

    mu1, mu2 = np.mean(arr1_masked), np.mean(arr2_masked)
    cov = np.mean((arr1_masked - mu1) * (arr2_masked - mu2))
    C1, C2 = (0.01 * 255)**2, (0.03 * 255)**2
    ssim = ((2 * mu1 * mu2 + C1) * (2 * cov + C2)) / ((mu1**2 + mu2**2 + C1) * (var1 + var2 + C2))

    return light_diff, ssim, damage_pct

def run_facenet(original, generated, model):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    agf_path = os.path.join(project_root, "agf.py")
    cmd = ["python", agf_path, "closure", original, generated, model, "facenet", "norm"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        match = re.search(r'\{.*\}', result.stdout, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return None
    except Exception:
        return None

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python tools/smhp_validator_v2.py <original> <generada> <facenet.tflite> [damage_mask.png]")
        sys.exit(1)

    orig, gen, model = sys.argv[1], sys.argv[2], sys.argv[3]
    mask = sys.argv[4] if len(sys.argv) > 4 else None

    metrics = calculate_metrics(orig, gen, mask)
    if not metrics:
        sys.exit(1)

    light_diff, ssim, damage_pct = metrics
    
    # Umbral estricto al 20%
    if damage_pct < 20.0:
        mode = "PRESERVATION"
        ssim_threshold = 0.90
    else:
        mode = "RESTORATION"
        ssim_threshold = 0.60 # Más permisivo en restauración

    print(f"=== AGF v12.1 SMHP VALIDATOR v2.1 ===")
    print(f"[MODO] {mode} (Damage: {damage_pct:.1f}%)")
    print(f"1. LIGHTING_VARIANCE_SHIFT: {light_diff*100:.2f}% (Umbral: < 5%)")
    print(f"2. TEXTURE_SSIM (solo zonas sanas): {ssim:.4f} (Umbral: > {ssim_threshold})")

    face_result = run_facenet(orig, gen, model)
    cosine = 0
    status = "FAIL"
    if face_result:
        cosine = face_result.get("verification", {}).get("cosine", 0)
        status = face_result.get("verification", {}).get("status", "FAIL")
        print(f"3. FACENET COSINE: {cosine:.4f} (Umbral: 0.79)")

    print(f"\n=== VEREDICTO FINAL ===")
    if mode == "PRESERVATION":
        if status == "PASS" and ssim > ssim_threshold and light_diff < 0.05:
            print("✅ PASS: Identidad y textura preservadas.")
        else:
            print("❌ BLOCKED: Alteración detectada en modo preservación.")
    else:
        print(f"⚠️ HUMAN_REVIEW: Operación de {mode} (Daño: {damage_pct:.1f}%).")
        print(f"   -> La imagen original está rota. FaceNet no es concluyente.")
        print(f"   -> El operador debe inspeccionar visualmente el resultado.")
        if ssim > ssim_threshold:
            print(f"   -> SSIM en zonas sanas es ACEPTABLE ({ssim:.2f}).")
        else:
            print(f"   -> SSIM en zonas sanas es BAJO ({ssim:.2f}). La IA tocó zonas no dañadas.")

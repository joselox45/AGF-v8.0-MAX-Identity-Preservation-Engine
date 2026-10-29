#!/usr/bin/env python3
"""
AGF v0.7.0 - SMHP Validator (Semantic-Math Handshake Protocol)
Calcula SSIM (Textura), Varianza (Luz) y ejecuta FaceNet (Identidad).
"""
import numpy as np
from PIL import Image
import subprocess
import sys
import os
import json
import re

def calculate_metrics(original_path, generated_path):
    try:
        img1 = Image.open(original_path).convert('L').resize((512, 512))
        img2 = Image.open(generated_path).convert('L').resize((512, 512))
    except Exception as e:
        print(f"[ERROR] Error abriendo imágenes: {e}")
        return None

    arr1 = np.array(img1, dtype=np.float32)
    arr2 = np.array(img2, dtype=np.float32)

    # 1. Varianza de Luminancia
    var1 = np.var(arr1)
    var2 = np.var(arr2)
    light_diff = abs(var1 - var2) / var1 if var1 > 0 else 0

    # 2. SSIM Simplificado
    mu1, mu2 = np.mean(arr1), np.mean(arr2)
    cov = np.mean((arr1 - mu1) * (arr2 - mu2))
    C1, C2 = (0.01 * 255)**2, (0.03 * 255)**2
    ssim = ((2 * mu1 * mu2 + C1) * (2 * cov + C2)) / ((mu1**2 + mu2**2 + C1) * (var1 + var2 + C2))

    return light_diff, ssim

def run_facenet(original, generated, model):
    print("\n[INFO] Ejecutando FaceNet (Llamando a agf.py)...")
    
    # CORRECCIÓN: Buscar agf.py en la raíz del proyecto (un nivel arriba de tools/)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    agf_path = os.path.join(project_root, "agf.py")
    
    if not os.path.exists(agf_path):
        print(f"[ERROR] No se encontró agf.py en: {agf_path}")
        return None

    cmd = ["python", agf_path, "closure", original, generated, model, "facenet", "norm"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        stdout = result.stdout
        
        # Buscar el bloque JSON con Regex (ignora warnings de TensorFlow)
        match = re.search(r'\{.*\}', stdout, re.DOTALL)
        if match:
            clean_json = match.group(0)
            return json.loads(clean_json)
        else:
            print(f"[ERROR] No se encontró un bloque JSON válido en la salida de agf.py")
            print(f"[DEBUG] Salida de agf.py:\n{stdout[:500]}...")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] agf.py falló con código de error {e.returncode}")
        print(f"Salida de error: {e.stderr}")
        return None
    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python tools/smhp_validator.py <original> <generada> <modelo.tflite>")
        sys.exit(1)

    orig, gen, model = sys.argv[1], sys.argv[2], sys.argv[3]

    metrics = calculate_metrics(orig, gen)
    if not metrics:
        sys.exit(1)

    light_diff, ssim = metrics
    print(f"=== RESULTADOS MATEMÁTICOS SMHP ===")
    print(f"1. LIGHTING_VARIANCE_SHIFT: {light_diff*100:.2f}% (Umbral sugerido: < 5%)")
    print(f"2. TEXTURE_SSIM: {ssim:.4f} (Umbral: > 0.90)")

    # Alertas visuales
    if light_diff > 0.05:
        print("   ⚠️ ALERTA: Cambio de iluminación detectado. Ejecuta lighting_normalizer.py")
    if ssim < 0.90:
        print("   ⚠️ ALERTA: Pérdida de textura detectada (Generative Smoothing).")

    # Ejecutar FaceNet
    face_result = run_facenet(orig, gen, model)
    if face_result:
        print("\n=== RESULTADO FACENET ===")
        print(json.dumps(face_result, indent=2))
        
        # Veredicto final
        cosine = face_result.get("verification", {}).get("cosine", 0)
        status = face_result.get("verification", {}).get("status", "FAIL")
        
        print("\n=== VEREDICTO FINAL (SMHP) ===")
        if status == "PASS" and ssim > 0.90:
            print("✅ PASS: Identidad preservada, textura intacta.")
        elif status == "PASS" and ssim <= 0.90:
            print("⚠️ HUMAN_REVIEW: Identidad PASS, pero hubo suavizado (SSIM bajo).")
        else:
            print("❌ BLOCKED: Identidad alterada (Cosine bajo).")

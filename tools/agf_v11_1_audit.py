#!/usr/bin/env python3
"""
AGF v11.1 - Hybrid Auditor (FaceNet Cosine + Laplacian Variance)
Zero-Scipy version (uses PIL + NumPy)
"""
import sys
import os
import numpy as np
from PIL import Image, ImageFilter

def laplacian_variance(image_path):
    """Mide la nitidez/textura usando el filtro FIND_EDGES de PIL y la varianza de NumPy."""
    img = Image.open(image_path).convert('L')
    
    # PIL nos da un filtro Laplaciano integrado: FIND_EDGES
    edges = img.filter(ImageFilter.FIND_EDGES)
    
    # Convertimos a array y calculamos la varianza
    img_array = np.array(edges, dtype=float)
    return img_array.var()

def main(original, generated):
    print(f"=== AGF v11.1 HYBRID AUDIT ===")
    print(f"Original: {original}")
    print(f"Generada: {generated}")
    
    # 1. Medir Varianza del Laplaciano (Textura)
    lap_orig = laplacian_variance(original)
    lap_gen = laplacian_variance(generated)
    
    print(f"\n[1] TEXTURE METRICS (Laplacian Variance):")
    print(f"  Original: {lap_orig:.2f}")
    print(f"  Generada: {lap_gen:.2f}")
    
    # Si la generada tiene MENOS varianza que la original, es "Generative Smoothing"
    if lap_gen < lap_orig * 0.8:
        print(f"  ⚠️ ALERTA: Pérdida de textura detectada. La IA suavizó la piel.")
        print(f"  La generada tiene un {(1 - lap_gen/lap_orig)*100:.1f}% menos de textura.")
    else:
        print(f"  ✅ Textura preservada o mejorada.")
    
    # 2. Ejecutar FaceNet (Identidad)
    print(f"\n[2] IDENTITY METRICS (FaceNet Cosine):")
    print("  Ejecutando FaceNet (esto puede tardar)...")
    os.system(f"python agf.py closure {original} {generated} facenet.tflite facenet norm blaze_face_short_range.tflite")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python tools/agf_v11_1_audit.py <original.jpg> <generada.jpg>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])

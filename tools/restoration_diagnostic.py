#!/usr/bin/env python3
"""
AGF v12.2 - Diagnosticador de Daños (Paso 1)
"""
import sys
import numpy as np
from PIL import Image

def diagnose(image_path):
    img = Image.open(image_path).convert("RGB")
    arr = np.array(img, dtype=np.float32)
    
    r, g, b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
    color_diff = np.mean(np.abs(r - g)) + np.mean(np.abs(g - b)) + np.mean(np.abs(r - b))
    is_bw = color_diff < 10.0
    is_sepia = (np.mean(r) > np.mean(b) * 1.15) and not is_bw
    
    gray = np.mean(arr, axis=2)
    laplacian = np.abs(4 * gray[1:-1, 1:-1] - gray[:-2, 1:-1] - gray[2:, 1:-1] - gray[1:-1, :-2] - gray[1:-1, 2:])
    blur_score = np.var(laplacian)
    noise_score = np.std(gray - np.mean(gray))
    
    print(f"\n=== DIAGNÓSTICO RESTORATION: {image_path} ===")
    print(f"1. Color:      {'B/N (Blanco y Negro)' if is_bw else 'Amarillento/Sepia' if is_sepia else 'A Color'}")
    print(f"2. Nitidez:    {blur_score:.2f} {'(Borroso)' if blur_score < 100 else '(Aceptable)' if blur_score < 300 else '(Nítido)'}")
    print(f"3. Grano/Ruido:{noise_score:.2f} {'(Muy alto)' if noise_score > 70 else '(Moderado)' if noise_score > 40 else '(Bajo)'}")
    print(f"4. Resolución: {img.width}x{img.height}")
    print("----------------------------------------")
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python tools/restoration_diagnostic.py <imagen_danada>")
        sys.exit(1)
    diagnose(sys.argv[1])

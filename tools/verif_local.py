#!/usr/bin/env python3
"""
AGF v11.0 - Local Verifier (No OpenCV required)
Calcula Laplacian Variance (Textura) y Similitud Estructural (SSIM) usando solo NumPy y Pillow.
"""
import numpy as np
from PIL import Image
import argparse
import os

def to_grayscale_np(image_path):
    """Carga una imagen y la convierte a un array 2D de escala de grises."""
    try:
        img = Image.open(image_path).convert('L')
        return np.array(img, dtype=np.float32)
    except Exception as e:
        print(f"[ERROR] No se pudo cargar {image_path}: {e}")
        return None

def calculate_laplacian_variance(img_array):
    """Aplica el operador Laplaciano manualmente con NumPy para medir textura."""
    if img_array is None:
        return 0.0
    
    # Kernel Laplaciano 3x3
    kernel = np.array([[0, 1, 0],
                       [1, -4, 1],
                       [0, 1, 0]], dtype=np.float32)
    
    # Convolución manual (padding de ceros para mantener tamaño)
    h, w = img_array.shape
    padded = np.pad(img_array, pad_width=1, mode='constant', constant_values=0)
    laplacian = np.zeros_like(img_array)
    
    for i in range(h):
        for j in range(w):
            region = padded[i:i+3, j:j+3]
            laplacian[i, j] = np.sum(region * kernel)
    
    # Varianza del Laplaciano
    return np.var(laplacian)

def calculate_ssim_simple(orig_array, gen_array):
    """SSIM simplificado usando NumPy."""
    if orig_array is None or gen_array is None:
        return 0.0
    
    # Redimensionar la generada al tamaño de la original
    if orig_array.shape != gen_array.shape:
        gen_img = Image.fromarray(gen_array.astype(np.uint8))
        gen_img = gen_img.resize((orig_array.shape[1], orig_array.shape[0]))
        gen_array = np.array(gen_img, dtype=np.float32)
    
    mu1 = np.mean(orig_array)
    mu2 = np.mean(gen_array)
    var1 = np.var(orig_array)
    var2 = np.var(gen_array)
    cov = np.mean((orig_array - mu1) * (gen_array - mu2))
    
    C1 = (0.01 * 255)**2
    C2 = (0.03 * 255)**2
    
    ssim = ((2 * mu1 * mu2 + C1) * (2 * cov + C2)) / ((mu1**2 + mu2**2 + C1) * (var1 + var2 + C2))
    return ssim

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AGF v11.0 Local Verifier")
    parser.add_argument("original", help="Imagen original (Referencia)")
    parser.add_argument("generated", help="Imagen generada")
    args = parser.parse_args()

    print("=== AGF v11.0 LOCAL VERIFIER (Pillow + NumPy) ===")
    
    orig_arr = to_grayscale_np(args.original)
    gen_arr = to_grayscale_np(args.generated)
    
    if orig_arr is None or gen_arr is None:
        exit(1)

    lap_orig = calculate_laplacian_variance(orig_arr)
    lap_gen = calculate_laplacian_variance(gen_arr)
    ssim_score = calculate_ssim_simple(orig_arr, gen_arr)

    print(f"1. LAPLACIAN VARIANCE (Original): {lap_orig:.2f}")
    print(f"2. LAPLACIAN VARIANCE (Generada): {lap_gen:.2f}")
    
    loss = 0.0
    if lap_orig > 0:
        loss = ((lap_orig - lap_gen) / lap_orig) * 100
        print(f"   -> Pérdida de Textura: {loss:.2f}% (Umbral: < 10%)")
        if loss > 10:
            print("   ⚠️ ALERTA: Generative Smoothing detectado.")
    
    print(f"3. SSIM GLOBAL: {ssim_score:.4f} (Umbral: > 0.90)")
    
    print("\n=== VEREDICTO LOCAL ===")
    if ssim_score > 0.90 and loss < 10:
        print("✅ PASS: Identidad y textura preservadas.")
    else:
        print("❌ HUMAN_REVIEW: La IA alteró la textura o la estructura.")

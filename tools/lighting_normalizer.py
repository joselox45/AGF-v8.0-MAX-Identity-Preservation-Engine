#!/usr/bin/env python3
"""
AGF v9.0 - Lighting Normalizer (No OpenCV required)
Ajusta la iluminación de la imagen generada para que coincida con la original
utilizando estadísticas de píxeles (Media y Desviación Estándar).
"""
import numpy as np
from PIL import Image
import argparse
import os

def normalize_image(original_path, generated_path, output_path):
    try:
        ref_img = Image.open(original_path).convert("RGB")
        gen_img = Image.open(generated_path).convert("RGB")
    except Exception as e:
        print(f"[ERROR] No se pudieron cargar las imágenes: {e}")
        return

    # Redimensionar la generada al tamaño de la original
    gen_img = gen_img.resize(ref_img.size)
    
    # Convertir a matrices NumPy
    ref_arr = np.array(ref_img, dtype=np.float32)
    gen_arr = np.array(gen_img, dtype=np.float32)
    
    # Calcular Media y Desviación Estándar por canal (R, G, B)
    ref_mean = np.mean(ref_arr, axis=(0, 1), keepdims=True)
    ref_std = np.std(ref_arr, axis=(0, 1), keepdims=True)
    gen_mean = np.mean(gen_arr, axis=(0, 1), keepdims=True)
    gen_std = np.std(gen_arr, axis=(0, 1), keepdims=True)
    
    # Evitar división por cero
    gen_std = np.where(gen_std == 0, 1, gen_std)
    
    # Aplicar normalización (Ajuste de histograma)
    normalized_arr = (gen_arr - gen_mean) * (ref_std / gen_std) + ref_mean
    
    # Recortar valores entre 0 y 255
    normalized_arr = np.clip(normalized_arr, 0, 255).astype(np.uint8)
    
    # Guardar
    out_img = Image.fromarray(normalized_arr)
    out_img.save(output_path)
    print(f"[OK] Imagen normalizada guardada en: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AGF Lighting Normalizer")
    parser.add_argument("original", help="Imagen original (Referencia)")
    parser.add_argument("generated", help="Imagen generada (A normalizar)")
    parser.add_argument("output", help="Imagen de salida normalizada")
    args = parser.parse_args()

    if not os.path.exists(args.original) or not os.path.exists(args.generated):
        print("[ERROR] Archivos no encontrados.")
        exit(1)

    print("[INFO] Aplicando Normalización de Iluminación (Pillow + NumPy)...")
    normalize_image(args.original, args.generated, args.output)

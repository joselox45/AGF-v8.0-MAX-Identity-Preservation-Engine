#!/usr/bin/env python3
"""
AGF v12.2 - Scale Normalizer (Pre-procesamiento Forense)
Fuerza a que la imagen original y la generada compartan la misma resolución (x2 o tamaño máximo).
"""
import sys
import os
from PIL import Image

def normalize_scale(orig_path, gen_path, output_dir="sandbox"):
    img_orig = Image.open(orig_path)
    img_gen = Image.open(gen_path)
    
    # Tomamos el tamaño de la imagen más grande (para no perder calidad)
    max_width = max(img_orig.width, img_gen.width)
    max_height = max(img_orig.height, img_gen.height)
    
    # Si quieres forzar un x2 exacto, descomenta estas líneas:
    # max_width = img_orig.width * 2
    # max_height = img_orig.height * 2
    
    print(f"[1/2] Normalizando ambas imágenes a {max_width}x{max_height}...")
    
    # Usamos LANCZOS (el estándar de oro para preservar bordes y texturas)
    img_orig_resized = img_orig.resize((max_width, max_height), Image.Resampling.LANCZOS)
    img_gen_resized = img_gen.resize((max_width, max_height), Image.Resampling.LANCZOS)
    
    orig_out = os.path.join(output_dir, "normalized_orig.jpg")
    gen_out = os.path.join(output_dir, "normalized_gen.jpg")
    
    img_orig_resized.convert("RGB").save(orig_out, quality=95)
    img_gen_resized.convert("RGB").save(gen_out, quality=95)
    
    print(f"✅ Imágenes normalizadas y guardadas en {output_dir}/")
    return orig_out, gen_out

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python tools/agf_scale_normalizer.py <orig> <gen>")
        sys.exit(1)
        
    orig_out, gen_out = normalize_scale(sys.argv[1], sys.argv[2])
    print(f"👉 Ahora puedes auditar: ./agf.sh preservation {orig_out} {gen_out}")

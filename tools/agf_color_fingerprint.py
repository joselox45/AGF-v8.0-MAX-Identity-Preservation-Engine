#!/usr/bin/env python3
"""
AGF v12.2 - Color Fingerprint (Huella Cromática)
Compara los colores dominantes de la imagen original y la generada.
"""
import sys
import os
import numpy as np
from PIL import Image
import colorsys

def get_dominant_colors(image_path, num_colors=3):
    img = Image.open(image_path).convert('RGB')
    # Reducir a 50x50 para análisis rápido
    img = img.resize((50, 50), Image.Resampling.LANCZOS)
    
    # Usar cuantización para agrupar colores similares
    quantized = img.quantize(colors=num_colors, method=Image.Quantize.MEDIANCUT)
    palette = quantized.getpalette()
    color_counts = sorted(quantized.getcolors(), reverse=True)
    
    dominant = []
    for count, index in color_counts[:num_colors]:
        r, g, b = palette[index*3 : index*3+3]
        # Convertir a Hexadecimal
        hex_color = f"#{r:02X}{g:02X}{b:02X}"
        # Convertir a HSV para comparar sin importar el brillo
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        dominant.append({
            "hex": hex_color,
            "hsv": (h * 360, s * 100, v * 100),
            "count": count
        })
    return dominant

def compare_color_fingerprints(orig_colors, gen_colors, mode="preservation"):
    # Extraer matices (Hue) de los colores dominantes
    hue_orig = [c["hsv"][0] for c in orig_colors]
    hue_gen = [c["hsv"][0] for c in gen_colors]
    
    # Calcular diferencia de matiz promedio
    min_diffs = []
    for h_gen in hue_gen:
        diff = min(abs(h_gen - h_orig) for h_orig in hue_orig)
        # Manejar el círculo cromático (0-360)
        if diff > 180:
            diff = 360 - diff
        min_diffs.append(diff)
        
    avg_hue_diff = sum(min_diffs) / len(min_diffs)
    return avg_hue_diff

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python tools/agf_color_fingerprint.py <orig> <gen> [--mode preservation|restoration]")
        sys.exit(1)
        
    mode = "preservation"
    if "--mode" in sys.argv:
        mode = sys.argv[sys.argv.index("--mode") + 1]

    print(f"[1/2] Extrayendo huella cromática...")
    orig_colors = get_dominant_colors(sys.argv[1])
    gen_colors = get_dominant_colors(sys.argv[2])
    
    print(f"\n--- COLORES ORIGINAL ---")
    for c in orig_colors: print(f"  {c['hex']} (H: {c['hsv'][0]:.1f}°)")
    print(f"\n--- COLORES GENERADA ---")
    for c in gen_colors: print(f"  {c['hex']} (H: {c['hsv'][0]:.1f}°)")
    
    print(f"\n[2/2] Calculando distancia cromática...")
    hue_diff = compare_color_fingerprints(orig_colors, gen_colors, mode)
    print(f"Diferencia promedio de Matiz (Hue): {hue_diff:.2f} grados")
    
    # Umbrales: En preservación la paleta debe ser muy similar (< 30°). En restauración permitimos hasta 60°.
    threshold = 60 if mode == "restoration" else 30
    
    if hue_diff <= threshold:
        print(f"✅ PASS: La paleta cromática es consistente (ΔH < {threshold}°).")
    else:
        print(f"❌ FAIL: La paleta cromática cambió drásticamente (ΔH > {threshold}°).")

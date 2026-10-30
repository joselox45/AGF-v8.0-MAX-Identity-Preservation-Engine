#!/usr/bin/env python3
"""
AGF v12.3.8 - Full Forensic Audit (Hierarchical)
Muestra las 9 capas pero respeta la jerarquia:
- Capas 1-2: Filtros (Metadata, Tiling)
- Capas 3-4: Diagnostico (Lighting, Base64)
- Capas 5-9: Juez Final (Score Ponderado)
"""
import sys
import os
import subprocess

def run(cmd, desc, is_judge=False):
    print(f"\n{'='*60}")
    print(f" {desc}")
    print('='*60)
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if is_judge:
        return result.returncode == 0
    return True

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python tools/agf_full_9_layers.py <orig> <gen> <mode>")
        sys.exit(1)

    orig = sys.argv[1]
    gen = sys.argv[2]
    mode = sys.argv[3]
    tflite = "blaze_face_short_range.tflite"

    print("\n" + "█" * 60)
    print(" 🛡️  AGF v12.3.8 - FULL FORENSIC AUDIT (9 LAYERS)")
    print("█" * 60)

    print("\n🔍 FASE 1: FILTROS DE SEGURIDAD (NO BLOQUEAN)")
    print("   Nota: La metadata de la ORIGINAL se ignora porque las redes sociales (Facebook, WhatsApp) borran el EXIF original y añaden el suyo (FBMD).")
    run(["python", "tools/agf_metadata_forensic.py", gen], "CAPA 1: Metadata de la GENERADA (Solo diagnostico)")
    print("\n   Nota: El Tiling es un filtro de deteccion. Si falla, el Juez Final dara BLOCKED.")
    run(["python", "tools/agf_tiling_detector.py", orig, tflite], "CAPA 2: Tiling Original (Deteccion)")
    run(["python", "tools/agf_tiling_detector.py", gen, tflite], "CAPA 2: Tiling Generada (Deteccion)")

    print("\n🔬 FASE 2: DIAGNOSTICO FORENSE (No pondera)")
    run(["python", "tools/agf_lighting_forensic.py", orig, gen, tflite], "CAPA 3: Lighting (Solo diagnostico)")
    run(["python", "tools/agf_base64_diff.py", orig, gen], "CAPA 4: Base64 Differential (Solo diagnostico)")

    print("\n⚖️ FASE 3: JUEZ FINAL (Score Ponderado)")
    print("   Las 5 capas ponderadas son las unicas que dictan PASS/BLOCKED.")
    is_pass = run(["python", "tools/agf_composite_scorer.py", orig, gen, tflite, "--mode", mode], "CAPAS 5-9: Composite (ArcFace + Fourier + Shazam + SSIM + Color + Overlay)", is_judge=True)

    print("\n" + "█" * 60)
    if is_pass:
        print(" ✅ VEREDICTO FINAL: PASS (Juez: Score Ponderado)")
    else:
        print(" 🚨 VEREDICTO FINAL: BLOCKED (Juez: Score Ponderado)")
    print("█" * 60)

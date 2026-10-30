#!/usr/bin/env python3
"""
AGF v12.3 - Base64 Differential Engine (Capa 9 - Sin Matplotlib)
Analiza el flujo crudo de bytes y genera un mapa de calor usando solo PIL.
"""
import sys
import os
import base64
import numpy as np
from PIL import Image, ImageDraw

def get_base64_chunks(file_path, chunk_size=1024):
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode('ascii')
    chunks = [b64[i:i+chunk_size] for i in range(0, len(b64), chunk_size)]
    return chunks

def calculate_chunk_entropy(chunk):
    if not chunk: return 0
    freq = {}
    for c in chunk:
        freq[c] = freq.get(c, 0) + 1
    entropy = -sum((count / len(chunk)) * np.log2(count / len(chunk)) for count in freq.values())
    return entropy

def diff_engine(orig_path, gen_path):
    print("[1/3] Extrayendo flujos Base64...")
    orig_chunks = get_base64_chunks(orig_path)
    gen_chunks = get_base64_chunks(gen_path)
    
    max_chunks = max(len(orig_chunks), len(gen_chunks))
    print(f"[2/3] Comparando {max_chunks} bloques de memoria...")
    
    entropy_orig = []
    entropy_gen = []
    diff_map = []
    
    for i in range(max_chunks):
        c_orig = orig_chunks[i] if i < len(orig_chunks) else ""
        c_gen = gen_chunks[i] if i < len(gen_chunks) else ""
        
        e_orig = calculate_chunk_entropy(c_orig)
        e_gen = calculate_chunk_entropy(c_gen)
        
        entropy_orig.append(e_orig)
        entropy_gen.append(e_gen)
        diff_map.append(abs(e_orig - e_gen))

    print("[3/3] Generando Mapa de Calor Base64 (PIL)...")
    
    # Crear imagen de 800x400
    width, height = 800, 400
    img = Image.new('RGB', (width, height), color='black')
    draw = ImageDraw.Draw(img)
    
    # Escalar los bloques para que quepan en el ancho
    x_scale = width / max_chunks
    y_max = max(max(entropy_orig), max(entropy_gen), 1)
    
    # Dibujar líneas de entropía
    for i in range(max_chunks):
        x = int(i * x_scale)
        
        # Línea azul (Original)
        y_orig = height - int((entropy_orig[i] / y_max) * height)
        draw.line([(x, height), (x, y_orig)], fill='blue', width=1)
        
        # Línea verde (Generada)
        y_gen = height - int((entropy_gen[i] / y_max) * height)
        draw.line([(x, height), (x, y_gen)], fill='green', width=1)
        
        # Zonas rojas (Diferencia alta)
        if diff_map[i] > 0.5:
            y_diff = height - int((diff_map[i] / y_max) * height)
            draw.rectangle([x, min(height, y_diff), x+2, max(height, y_diff)], fill='red')

    output_path = "sandbox/base64_heatmap.png"
    img.save(output_path)
    os.system(f'cp {output_path} ~/storage/downloads/')
    
    print(f"\n✅ Mapa de manipulación guardado en: {output_path} (y en tu galería).")
    print("👉 Las zonas rojas indican dónde la IA inyectó alucinaciones de píxeles.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python tools/agf_base64_diff.py <orig> <gen>")
        sys.exit(1)
    diff_engine(sys.argv[1], sys.argv[2])

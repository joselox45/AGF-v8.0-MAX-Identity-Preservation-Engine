#!/usr/bin/env python3
"""
AGF v12.2 - Pre-Seal Protocol
Sella la imagen ANTES de enviarla al LLM. Borra la original por seguridad.
"""
import sys
import os
import json
import hashlib
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont

def get_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def apply_visual_mark(image_path, text, output_path):
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size
    txt_layer = Image.new('RGBA', img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)
    
    try:
        font_size = max(15, int(height * 0.03))
        font = ImageFont.truetype("/system/fonts/Roboto-Regular.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), text, font=font)
    x = width - (bbox[2] - bbox[0]) - 15
    y = height - (bbox[3] - bbox[1]) - 15
    
    draw.text((x + 1, y + 1), text, font=font, fill=(0, 0, 0, 150))
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 200))
    
    watermarked = Image.alpha_composite(img, txt_layer)
    watermarked.convert("RGB").save(output_path, quality=95)
    return get_sha256(output_path)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python tools/agf_pre_seal.py <imagen_cruda> <autor>")
        sys.exit(1)
        
    raw_path = sys.argv[1]
    author = sys.argv[2]
    
    if not os.path.exists(raw_path):
        print(f"❌ ERROR: No existe {raw_path}")
        sys.exit(1)
        
    print(f"[1/4] Calculando SHA-256 de la imagen original...")
    hash_original = get_sha256(raw_path)
    
    print(f"[2/4] Aplicando marca de agua y sellando...")
    sealed_path = os.path.splitext(raw_path)[0] + "_SEALED.jpg"
    hash_sealed = apply_visual_mark(raw_path, f"{author} | AGF", sealed_path)
    
    print(f"[3/4] Generando certificado pre-generación...")
    timestamp = datetime.now(timezone.utc).isoformat()
    cert = {
        "agf_protocol": "AGF-PRE-SEAL-v1",
        "timestamp_utc": timestamp,
        "author": author,
        "original_file": os.path.basename(raw_path),
        "original_sha256": hash_original,
        "sealed_file": os.path.basename(sealed_path),
        "sealed_sha256": hash_sealed,
        "status": "READY_FOR_LLM"
    }
    cert_path = os.path.splitext(raw_path)[0] + "_SEALED.agf.json"
    with open(cert_path, "w") as f:
        json.dump(cert, f, indent=4)
        
    print(f"[4/4] Borrando imagen original por seguridad...")
    os.remove(raw_path)
    
    print(f"\n=== ✅ PRE-SELLO COMPLETADO ===")
    print(f"Imagen para subir al LLM: {sealed_path}")
    print(f"Certificado de origen:    {cert_path}")
    print(f"⚠️ La imagen original '{raw_path}' ha sido destruida.")
    print(f"⚠️ SHA-256 Original (Guardado): {hash_original}")

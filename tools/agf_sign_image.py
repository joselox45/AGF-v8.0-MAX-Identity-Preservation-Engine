#!/usr/bin/env python3
"""
AGF Sign Image — Vincula criptograficamente un JSON de trazabilidad a una imagen.
Incrustando el hash SHA-256 y la firma Ed25519 en los metadatos EXIF.
"""
import sys
import json
import hashlib
from PIL import Image
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

def sign_and_embed(image_path, json_path, output_path):
    # 1. Leer y hashear el JSON (la evidencia)
    with open(json_path, "rb") as f:
        json_bytes = f.read()
    json_hash = hashlib.sha256(json_bytes).hexdigest()
    
    # 2. Generar par de llaves Ed25519 (en prod, esto debe ser una llave privada persistente)
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    
    # 3. Firmar el hash
    signature = private_key.sign(json_hash.encode('utf-8'))
    signature_hex = signature.hex()
    public_key_hex = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    ).hex()
    
    # 4. Incrustar en metadatos EXIF
    img = Image.open(image_path)
    exif = img.getexif()
    
    # Usamos tags EXIF de usuario (0x9286 es UserComment)
    # Formato: AGF_SHA256:<hash>|AGF_SIG:<sig>|AGF_PUBKEY:<pubkey>
    agf_metadata = f"AGF_SHA256:{json_hash}|AGF_SIG:{signature_hex}|AGF_PUBKEY:{public_key_hex}"
    exif[0x9286] = agf_metadata
    
    # 5. Guardar la imagen con la firma incrustada
    img.save(output_path, exif=exif)
    print(f"[OK] Imagen firmada y vinculada al JSON. Hash: {json_hash[:16]}...")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python tools/agf_sign_image.py <imagen.jpg> <trace.json> <salida.jpg>")
        sys.exit(1)
    sign_and_embed(sys.argv[1], sys.argv[2], sys.argv[3])

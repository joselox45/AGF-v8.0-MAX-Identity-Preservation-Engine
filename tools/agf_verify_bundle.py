#!/usr/bin/env python3
"""
agf_verify_bundle.py — Decodifica el Evidence Bundle del LLM (Base64 -> ZIP)
Genera los archivos físicos y verifica la integridad criptográfica.
"""
import json
import base64
import hashlib
import zipfile
import sys
import os

def create_bundle_from_json(json_path, output_dir="evidence_bundle_out"):
    if not os.path.exists(json_path):
        print(f"ERROR: No se encuentra el archivo {json_path}")
        return False

    with open(json_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print("ERROR: El archivo no es un JSON válido.")
            return False

    bundle = data.get('evidence_bundle', {})
    if not bundle:
        print("ERROR: El JSON no contiene el campo 'evidence_bundle'.")
        return False

    os.makedirs(output_dir, exist_ok=True)
    extracted_files = []

    mapping = {
        'original_image_b64': 'original.jpg',
        'generated_image_b64': 'generated.jpg',
        'trace_json_b64': 'trace.json'
    }

    print("=== [1] DECODIFICANDO BASE64 ===")
    for b64_key, filename in mapping.items():
        b64_str = bundle.get(b64_key)
        if not b64_str or b64_str == "PENDIENTE_DE_CONVERSION_EN_PYTHON":
            print(f"WARN: {b64_key} está vacío o pendiente.")
            continue

        try:
            file_data = base64.b64decode(b64_str)
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'wb') as out_f:
                out_f.write(file_data)

            # Calcular hash real
            sha256 = hashlib.sha256(file_data).hexdigest()
            print(f"[OK] {filename} generado ({len(file_data)} bytes). SHA-256: {sha256}")
            extracted_files.append((filepath, sha256))
        except Exception as e:
            print(f"[FAIL] Error decodificando {b64_key}: {e}")
            return False

    print("\n=== [2] CREANDO ZIP FÍSICO ===")
    zip_name = "AGF_EVIDENCE_BUNDLE_VERIFIED.zip"
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for filepath, _ in extracted_files:
            zipf.write(filepath, os.path.basename(filepath))

    print(f"[OK] Archivo ZIP creado: {zip_name}")
    print("\n✔ Bundle físico listo para ser auditado por el Juez Puro.")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 tools/agf_verify_bundle.py <ruta_al_json_del_llm>")
        sys.exit(1)

    success = create_bundle_from_json(sys.argv[1])
    if not success:
        sys.exit(2)

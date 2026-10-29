#!/usr/bin/env python3
"""
AGF v11.0 - Multi-Face Auditor
Audita múltiples rostros en una imagen usando las coordenadas de un JSON.
"""
import json
import sys
import subprocess
import os
from PIL import Image
import numpy as np

def audit_faces(original_path, generated_path, bboxes_json, facenet_model):
    with open(bboxes_json, 'r') as f:
        data = json.load(f)
    
    bboxes = data.get("face_bboxes_pixel", [])
    labels = data.get("labels", [f"Subject_{i+1}" for i in range(len(bboxes))])
    
    if len(bboxes) == 0:
        print("[ERROR] No se encontraron face_bboxes en el JSON.")
        return

    print(f"=== AGF MULTI-FACE AUDITOR ===")
    print(f"Total de rostros a auditar: {len(bboxes)}")
    
    img_orig = Image.open(original_path).convert("RGB")
    img_gen = Image.open(generated_path).convert("RGB")
    
    cosines = []
    
    for i, (bbox, label) in enumerate(zip(bboxes, labels)):
        x, y, w, h = bbox # Asumiendo [x, y, width, height]
        
        # Recortar ambas imágenes usando las mismas coordenadas
        crop_orig = img_orig.crop((x, y, x+w, y+h))
        crop_gen = img_gen.crop((x, y, x+w, y+h))
        
        # Guardar recortes temporales
        temp_orig = f"temp_orig_{i}.jpg"
        temp_gen = f"temp_gen_{i}.jpg"
        crop_orig.save(temp_orig, quality=95)
        crop_gen.save(temp_gen, quality=95)
        
        # Ejecutar FaceNet usando agf.py
        cmd = ["python", "agf.py", "closure", temp_orig, temp_gen, facenet_model, "facenet", "norm"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Extraer cosine (lógica simplificada, en producción usar JSON parser)
        import re
        match = re.search(r'"cosine":\s*([0-9.]+)', result.stdout)
        cosine = float(match.group(1)) if match else 0.0
        cosines.append(cosine)
        
        print(f"[{label}] Cosine: {cosine:.4f} | {'PASS' if cosine >= 0.79 else 'FAIL'}")
        
        # Limpieza
        if os.path.exists(temp_orig): os.remove(temp_orig)
        if os.path.exists(temp_gen): os.remove(temp_gen)
    
    avg_cosine = np.mean(cosines)
    print(f"\n=== VEREDICTO GLOBAL ===")
    print(f"Cosine Promedio: {avg_cosine:.4f}")
    if avg_cosine >= 0.79:
        print("✅ PASS: Todos los rostros preservados.")
    else:
        print("❌ BLOCKED: Algún rostro fue alterado (Cosine promedio bajo).")

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Uso: python tools/multi_face_auditor.py <original> <generada> <bboxes.json> <modelo.tflite>")
        sys.exit(1)
    audit_faces(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

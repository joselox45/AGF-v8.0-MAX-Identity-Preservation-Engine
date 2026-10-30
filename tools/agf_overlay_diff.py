#!/usr/bin/env python3
"""
AGF v12.2 - Overlay Diff Forensic (Capa 7)
Superpone la imagen original sobre la generada para detectar cambios estructurales.
"""
import sys
import os
import numpy as np
from PIL import Image, ImageOps
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from face_detector import TFLiteFaceDetector
from agf_composite_scorer import get_affine_aligned_face

def generate_overlay_diff(orig_path, gen_path, detector, output_path="overlay_diff.png"):
    img1 = Image.open(orig_path).convert("RGB")
    img2 = Image.open(gen_path).convert("RGB")
    
    res1 = detector.detect(np.asarray(img1).tolist())
    res2 = detector.detect(np.asarray(img2).tolist())
    
    if not res1.detections or not res2.detections:
        return None

    # 1. Alinear ambas caras a 256x256
    face1 = get_affine_aligned_face(img1, res1.detections[0].keypoints, (256, 256)).convert('L')
    face2 = get_affine_aligned_face(img2, res2.detections[0].keypoints, (256, 256)).convert('L')
    
    # 2. Ecualizar para neutralizar la iluminación (si no, todo se ve como un cambio)
    face1_eq = np.array(ImageOps.equalize(face1), dtype=np.float32)
    face2_eq = np.array(ImageOps.equalize(face2), dtype=np.float32)
    
    # 3. Calcular la Diferencia Absoluta
    diff = np.abs(face1_eq - face2_eq)
    
    # 4. Calcular el porcentaje de "Deriva" (píxeles que cambiaron más de 30 niveles de gris)
    drift_mask = diff > 30
    drift_percentage = (np.sum(drift_mask) / diff.size) * 100
    
    # 5. Crear Mapa de Calor Visual
    # Base: La imagen original en tonos oscuros
    heatmap = np.stack([face1_eq * 0.3, face1_eq * 0.3, face1_eq * 0.3], axis=-1).astype(np.uint8)
    
    # Resaltar en ROJO los píxeles donde la IA cambió la estructura
    # Rojo puro (255, 0, 0)
    heatmap[drift_mask, 0] = 255 # Canal R
    heatmap[drift_mask, 1] = 0   # Canal G
    heatmap[drift_mask, 2] = 0   # Canal B
    
    # Guardar
    Image.fromarray(heatmap).save(output_path)
    
    return drift_percentage, output_path

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python tools/agf_overlay_diff.py <orig> <gen> <blaze_face.tflite>")
        sys.exit(1)

    detector = TFLiteFaceDetector(open(sys.argv[3], "rb").read(), select="largest")
    
    print("[1/2] Generando mapa de superposición...")
    result = generate_overlay_diff(sys.argv[1], sys.argv[2], detector)
    
    if not result:
        print("❌ BLOCKED: No se detectó rostro.")
        sys.exit(1)
        
    drift, path = result
    
    # Copiar a descargas para que el humano lo vea
    os.system(f'cp {path} ~/storage/downloads/agf_overlay_diff.png')
    
    print(f"[2/2] Imagen guardada en: {path} (y en tu galería).")
    print(f"\n=== AGF OVERLAY DIFF (CAPA 7) ===")
    print(f" Deriva Estructural (Drift): {drift:.2f}%")
    
    # Calibración
    if drift < 15.0:
        print("✅ PASS: La estructura facial es casi idéntica (Drift < 15%).")
    elif drift < 35.0:
        print("⚠️ HUMAN_REVIEW: Cambio estructural moderado. Revisa el mapa de calor.")
    else:
        print("🚨 BLOCKED: La IA alteró drásticamente la estructura (Drift > 35%).")

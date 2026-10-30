#!/usr/bin/env python3
"""
AGF v12.2 - Overlay Diff Forensic (Capa 7 - Autocontenido)
Genera un mapa de calor y lo guarda directamente en Descargas.
"""
import sys
import os
import numpy as np
from PIL import Image, ImageOps
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from face_detector import TFLiteFaceDetector

# Función de alineación copiada localmente para evitar dependencias circulares
def get_affine_aligned_face(img, keypoints, target_size=(256, 256)):
    eye1, eye2 = keypoints[0], keypoints[1]
    scale_factor = target_size[0] / 112.0
    t_eye1 = (38.2946 * scale_factor, 51.6963 * scale_factor)
    t_eye2 = (73.5318 * scale_factor, 51.5014 * scale_factor)
    dx, dy = eye2[0] - eye1[0], eye2[1] - eye1[1]
    angle = math.atan2(dy, dx)
    src_dist = math.sqrt(dx**2 + dy**2)
    tgt_dist = t_eye2[0] - t_eye1[0]
    src_cx, src_cy = (eye1[0] + eye2[0]) / 2, (eye1[1] + eye2[1]) / 2
    tgt_cx, tgt_cy = (t_eye1[0] + t_eye2[0]) / 2, (t_eye1[1] + t_eye2[1]) / 2
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    s = src_dist / tgt_dist
    a, b = s * cos_a, s * sin_a
    c = src_cx - a * tgt_cx - b * tgt_cy
    d, e = -s * sin_a, s * cos_a
    f = src_cy + b * tgt_cx - e * tgt_cy
    return img.transform(target_size, Image.AFFINE, (a, b, c, d, e, f), resample=Image.BICUBIC)

def generate_overlay_diff(orig_path, gen_path, detector):
    img1 = Image.open(orig_path).convert("RGB")
    img2 = Image.open(gen_path).convert("RGB")
    
    res1 = detector.detect(np.asarray(img1).tolist())
    res2 = detector.detect(np.asarray(img2).tolist())
    
    if not res1.detections or not res2.detections:
        return None

    # Alinear y ecualizar
    face1 = get_affine_aligned_face(img1, res1.detections[0].keypoints, (256, 256)).convert('L')
    face2 = get_affine_aligned_face(img2, res2.detections[0].keypoints, (256, 256)).convert('L')
    
    face1_eq = np.array(ImageOps.equalize(face1), dtype=np.float32)
    face2_eq = np.array(ImageOps.equalize(face2), dtype=np.float32)
    
    # Diferencia absoluta
    diff = np.abs(face1_eq - face2_eq)
    drift_mask = diff > 30
    drift_percentage = (np.sum(drift_mask) / diff.size) * 100
    
    # Crear mapa de calor
    heatmap = np.stack([face1_eq * 0.3, face1_eq * 0.3, face1_eq * 0.3], axis=-1).astype(np.uint8)
    heatmap[drift_mask, 0] = 255 # Rojo
    heatmap[drift_mask, 1] = 0
    heatmap[drift_mask, 2] = 0
    
    # Guardar en Descargas para acceso directo desde la galería
    download_dir = os.path.expanduser("~/storage/downloads")
    output_path = os.path.join(download_dir, "agf_overlay_diff.png")
    
    try:
        Image.fromarray(heatmap).save(output_path)
        print(f"✅ Mapa de calor guardado en: {output_path}")
    except Exception as e:
        print(f"⚠️ No se pudo guardar en Descargas: {e}")
        # Fallback a la carpeta local
        output_path = "overlay_diff.png"
        Image.fromarray(heatmap).save(output_path)
    
    return drift_percentage

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python tools/agf_overlay_diff.py <orig> <gen> <blaze_face.tflite>")
        sys.exit(1)

    detector = TFLiteFaceDetector(open(sys.argv[3], "rb").read(), select="largest")
    
    print("[1/2] Generando mapa de superposición...")
    drift = generate_overlay_diff(sys.argv[1], sys.argv[2], detector)
    
    if drift is None:
        print("❌ BLOCKED: No se detectó rostro.")
        sys.exit(1)
        
    print(f"\n=== AGF OVERLAY DIFF (CAPA 7) ===")
    print(f" Deriva Estructural (Drift): {drift:.2f}%")
    
    if drift < 15.0:
        print("✅ PASS: La estructura facial es casi idéntica.")
    elif drift < 35.0:
        print("⚠️ HUMAN_REVIEW: Cambio estructural moderado. Revisa la galería.")
    else:
        print("🚨 BLOCKED: La IA alteró drásticamente la estructura.")

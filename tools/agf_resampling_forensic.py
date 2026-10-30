#!/usr/bin/env python3
"""
AGF v12.2 - Resampling Forensic (Capa 8)
Detecta la firma de interpolación (upscaling) típica de las IAs.
"""
import sys
import os
import numpy as np
from PIL import Image
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from face_detector import TFLiteFaceDetector
from agf_composite_scorer import get_affine_aligned_face

def get_resampling_error(image_path, detector):
    img = Image.open(image_path).convert("RGB")
    res = detector.detect(np.asarray(img).tolist())
    if not res.detections:
        return None
    
    # 1. Alinear rostro a 256x256
    face = get_affine_aligned_face(img, res.detections[0].keypoints, (256, 256))
    arr_orig = np.array(face, dtype=np.float32)
    
    # 2. Reducir a 128x128 (Downscale)
    face_down = face.resize((128, 128), Image.BICUBIC)
    
    # 3. Volver a escalar a 256x256 (Upscale)
    face_up = face_down.resize((256, 256), Image.BICUBIC)
    arr_up = np.array(face_up, dtype=np.float32)
    
    # 4. Calcular el Error Absoluto Medio (MAE)
    error = np.mean(np.abs(arr_orig - arr_up))
    
    # 5. Calcular la Varianza del Error (distribución del ruido)
    error_map = np.abs(arr_orig - arr_up).mean(axis=2)
    error_var = np.var(error_map)
    
    return error, error_var

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python tools/agf_resampling_forensic.py <orig> <gen> <blaze_face.tflite>")
        sys.exit(1)

    detector = TFLiteFaceDetector(open(sys.argv[3], "rb").read(), select="largest")
    
    print("[1/2] Analizando firma de escalado (Original)...")
    err_orig, var_orig = get_resampling_error(sys.argv[1], detector)
    
    print("[2/2] Analizando firma de escalado (Generada)...")
    err_gen, var_gen = get_resampling_error(sys.argv[2], detector)
    
    if err_orig is None or err_gen is None:
        print("❌ BLOCKED: No se detectó rostro.")
        sys.exit(1)
        
    print(f"\n=== AGF RESAMPLING FORENSIC (CAPA 8) ===")
    print(f" Error de Resampling (Original) : {err_orig:.4f} (Var: {var_orig:.4f})")
    print(f" Error de Resampling (Generada) : {err_gen:.4f} (Var: {var_gen:.4f})")
    
    # Calibración: Las IAs suelen tener un error de resampling MUY BAJO en la piel (porque nacen de un upscaler)
    # Las cámaras reales tienen un error más alto por el ruido del sensor.
    if err_gen < err_orig * 0.8:
        print("🚨 ALERTA: La imagen generada tiene una firma de upscaling de IA (demasiado limpia).")
    else:
        print("✅ PASS: El ruido de resampling es consistente con una cámara física.")

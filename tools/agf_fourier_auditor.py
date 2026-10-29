#!/usr/bin/env python3
"""
AGF v12.2 - 2D Fourier Spectrum Auditor
Analiza la firma de frecuencia de la piel para detectar satinado o artefactos IA.
"""
import sys
import os
import numpy as np
from PIL import Image, ImageOps
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from face_detector import TFLiteFaceDetector
from agf_texture_shazam import get_affine_aligned_face

def get_fft_spectrum(image_path, detector):
    img = Image.open(image_path).convert("RGB")
    res = detector.detect(np.asarray(img).tolist())
    if res.status != "PASS" or not res.detections:
        return None
        
    # 1. Alinear rostro
    aligned = get_affine_aligned_face(img, res.detections[0].keypoints)
    
    # 2. Convertir a gris y normalizar
    gray = aligned.convert('L')
    
    # 3. Aplicar FFT 2D
    f = np.fft.fft2(gray)
    fshift = np.fft.fftshift(f)
    
    # 4. Calcular magnitud y aplicar escala logarítmica (para ver el espectro)
    magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1e-5)
    
    # Normalizar a 0-255 para visualización y comparación
    mag_normalized = (magnitude_spectrum - np.min(magnitude_spectrum)) / (np.max(magnitude_spectrum) - np.min(magnitude_spectrum))
    mag_normalized = (mag_normalized * 255).astype(np.uint8)
    
    return mag_normalized

def compare_spectrums(spec1, spec2):
    # Recortar el centro para ignorar los bordes negros del padding de la FFT
    size = 256
    center = size // 2
    crop = 80 # Analizar el área central de frecuencias
    
    s1 = spec1[center-crop:center+crop, center-crop:center+crop].astype(np.float32)
    s2 = spec2[center-crop:center+crop, center-crop:center+crop].astype(np.float32)
    
    # Similitud de Coseno en el dominio de la frecuencia
    dot = np.sum(s1 * s2)
    norm1 = np.linalg.norm(s1)
    norm2 = np.linalg.norm(s2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
        
    cos_sim = dot / (norm1 * norm2)
    return cos_sim

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python tools/agf_fourier_auditor.py <orig> <gen> <blaze_face.tflite>")
        sys.exit(1)

    detector = TFLiteFaceDetector(open(sys.argv[3], "rb").read(), select="largest")
    
    print("[1/3] Extrayendo Espectro de Fourier (Orig)...")
    spec_orig = get_fft_spectrum(sys.argv[1], detector)
    
    print("[2/3] Extrayendo Espectro de Fourier (Gen)...")
    spec_gen = get_fft_spectrum(sys.argv[2], detector)
    
    if spec_orig is None or spec_gen is None:
        print("❌ BLOCKED: No se detectó rostro.")
        sys.exit(1)
        
    # Guardar imágenes del espectro para auditoría visual
    Image.fromarray(spec_orig).save("sandbox/fourier_orig.png")
    Image.fromarray(spec_gen).save("sandbox/fourier_gen.png")
    os.system('cp sandbox/fourier_orig.png ~/storage/downloads/')
    os.system('cp sandbox/fourier_gen.png ~/storage/downloads/')

    print("[3/3] Comparando firmas de frecuencia...")
    score = compare_spectrums(spec_orig, spec_gen)
    
    print(f"\n=== AGF 2D FOURIER AUDITOR ===")
    print(f"Similitud Espectral: {score:.4f}")
    
    if score >= 0.85:
        print("✅ PASS: Firma de frecuencia natural (textura preservada).")
    else:
        print("❌ FAIL: Artefactos de IA detectados (satinado o alucinación).")

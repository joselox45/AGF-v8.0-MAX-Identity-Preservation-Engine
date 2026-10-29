#!/usr/bin/env python3
"""
AGF v8.0-MAX - Forensic Analyzer (Classical CV + Math Vectors)
Analiza imágenes usando Haar Cascade (OpenCV) y matemáticas puras (NumPy/SciPy).
"""
import cv2
import numpy as np
import argparse
import json
from scipy.spatial.distance import cosine, euclidean
from PIL import Image

def detect_haar_faces(image_path):
    """Detecta rostros usando el clasificador clásico Haar Cascade de OpenCV."""
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    img = cv2.imread(image_path)
    if img is None:
        return {"status": "ERROR", "reason": "No se pudo leer la imagen"}
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    return {
        "faces_detected": len(faces),
        "boxes": faces.tolist() if len(faces) > 0 else []
    }

def compare_pixels(img_path_a, img_path_b):
    """Calcula Cosine Similarity y Distancia Euclidiana de los píxeles aplanados."""
    # Cargar y redimensionar a un tamaño común para comparar (ej. 512x512)
    img_a = Image.open(img_path_a).convert("RGB").resize((512, 512))
    img_b = Image.open(img_path_b).convert("RGB").resize((512, 512))
    
    # Aplanar y normalizar a [0,1]
    vec_a = np.asarray(img_a).flatten().astype(float) / 255.0
    vec_b = np.asarray(img_b).flatten().astype(float) / 255.0
    
    cos_sim = 1 - cosine(vec_a, vec_b) # Scipy cosine returns distance, so 1 - dist = similarity
    euc_dist = euclidean(vec_a, vec_b)
    
    return {
        "cosine_similarity_pixels": float(cos_sim),
        "euclidean_distance": float(euc_dist)
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AGF Forensic Analyzer")
    parser.add_argument("image_a", help="Imagen Original (Base 0)")
    parser.add_argument("image_b", help="Imagen Generada/Editada")
    args = parser.parse_args()

    print(f"--- AGF FORENSIC ANALYZER ---")
    
    # 1. Detección Clásica
    haar_a = detect_haar_faces(args.image_a)
    haar_b = detect_haar_faces(args.image_b)
    
    # 2. Matemáticas de Píxeles
    pixel_metrics = compare_pixels(args.image_a, args.image_b)
    
    report = {
        "protocol": "AGF-FORENSIC-MULTILAYER",
        "haar_cascade": {
            "base_0_faces": haar_a,
            "target_faces": haar_b
        },
        "pixel_math": pixel_metrics,
        "note": "Este análisis no evalúa identidad facial. Para eso, usar agf.py closure con FaceNet."
    }
    
    print(json.dumps(report, indent=2))

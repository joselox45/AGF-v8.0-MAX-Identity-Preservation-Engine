#!/usr/bin/env python3
"""
AGF v12.2 - ArcFace ONNX Validator (Aligned)
Usa BlazeFace para detectar ojos, alinea el rostro y luego calcula embedding con ArcFace.
"""
import numpy as np
from PIL import Image
import onnxruntime as ort
import sys
import os
import math

sys.path.insert(0, os.path.dirname(__file__))
from face_detector import TFLiteFaceDetector

def get_aligned_face(image_path, detector):
    """Detecta ojos, rota y recorta el rostro a 112x112 alineado."""
    img = Image.open(image_path).convert('RGB')
    result = detector.detect(np.asarray(img).tolist())
    if result.status != "PASS" or not result.detections:
        return None
    
    kp = result.detections[0].keypoints
    eye1, eye2 = kp[0], kp[1]
    
    # Calcular ángulo de inclinación
    dx = eye2[0] - eye1[0]
    dy = eye2[1] - eye1[1]
    angle = math.degrees(math.atan2(dy, dx))
    
    # Rotar para enderezar los ojos
    rotated = img.rotate(-angle, resample=Image.BICUBIC, expand=True)
    
    # Recalcular posición de ojos en la imagen rotada
    cx_orig, cy_orig = img.width / 2, img.height / 2
    rad = math.radians(-angle)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    
    def rotate_pt(pt):
        x, y = pt
        return (cos_a*(x-cx_orig) - sin_a*(y-cy_orig) + cx_orig,
                sin_a*(x-cx_orig) + cos_a*(y-cy_orig) + cy_orig)
        
    e1 = rotate_pt(eye1)
    e2 = rotate_pt(eye2)
    
    new_cx, new_cy = rotated.width / 2, rotated.height / 2
    e1 = (e1[0] + (new_cx - cx_orig), e1[1] + (new_cy - cy_orig))
    e2 = (e2[0] + (new_cx - cx_orig), e2[1] + (new_cy - cy_orig))
    
    # Recorte centrado en ojos
    cx = (e1[0] + e2[0]) / 2
    cy = (e1[1] + e2[1]) / 2
    dist = math.sqrt((e2[0]-e1[0])**2 + (e2[1]-e1[1])**2)
    half = (dist * 3.0) / 2
    
    x1 = max(0, int(cx - half))
    y1 = max(0, int(cy - half))
    x2 = min(rotated.width, int(cx + half))
    y2 = min(rotated.height, int(cy + half))
    
    face = rotated.crop((x1, y1, x2, y2)).resize((112, 112), Image.BILINEAR)
    return face

def preprocess(face_img):
    """Normalización estándar ArcFace (112x112, [-1, 1], CHW)."""
    arr = np.array(face_img).astype(np.float32)
    arr = (arr - 127.5) / 127.5
    arr = np.transpose(arr, (2, 0, 1))
    return np.expand_dims(arr, axis=0)

def get_embedding(session, face_img):
    input_name = session.get_inputs()[0].name
    img = preprocess(face_img)
    outputs = session.run(None, {input_name: img})
    emb = outputs[0][0]
    return emb / np.linalg.norm(emb)

def compare_faces(orig_path, gen_path, model_path="arcface.onnx"):
    print("[INFO] Cargando BlazeFace para alineación...")
    detector = TFLiteFaceDetector(open("blaze_face_short_range.tflite", "rb").read(), select="largest")
    
    print(f"[INFO] Alineando rostro de {orig_path}...")
    face1 = get_aligned_face(orig_path, detector)
    if face1 is None:
        print("❌ BLOCKED: No se detectó rostro en la imagen original.")
        sys.exit(1)
        
    print(f"[INFO] Alineando rostro de {gen_path}...")
    face2 = get_aligned_face(gen_path, detector)
    if face2 is None:
        print("❌ BLOCKED: No se detectó rostro en la imagen generada.")
        sys.exit(1)
        
    print("[INFO] Iniciando ONNX Runtime...")
    session = ort.InferenceSession(model_path)
    
    print("[INFO] Calculando embeddings...")
    emb1 = get_embedding(session, face1)
    emb2 = get_embedding(session, face2)
    
    cosine = np.dot(emb1, emb2)
    return float(cosine)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python src/onnx_arcface_validator.py <imagen1> <imagen2>")
        sys.exit(1)

    try:
        score = compare_faces(sys.argv[1], sys.argv[2])
        print(f"\n=== RESULTADO ARCFACE (ALINEADO) ===")
        print(f"Similitud de Coseno: {score:.4f}")

        if score > 0.68:
            print("✅ PASS: Identidad verificada por ArcFace.")
        elif score > 0.60:
            print("⚠️ HUMAN_REVIEW: Identidad probable.")
        else:
            print("❌ BLOCKED: Identidad no coincide.")
    except Exception as e:
        print(f"[ERROR] Fallo al procesar: {e}")

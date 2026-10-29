#!/usr/bin/env python3
"""
AGF v12.0 - ArcFace ONNX Validator (No OpenCV required)
Calcula la similitud de identidad usando el modelo de grado industrial ArcFace.
"""
import numpy as np
from PIL import Image
import onnxruntime as ort
import sys

def preprocess(image_path):
    """Preprocesa la imagen para ArcFace (112x112, norm [-1,1], CHW)."""
    img = Image.open(image_path).convert('RGB')
    # ArcFace espera imágenes de 112x112
    img = img.resize((112, 112), Image.BILINEAR)
    img_array = np.array(img).astype(np.float32)
    
    # Normalización estándar de ArcFace: (pixel - 127.5) / 127.5
    img_array = (img_array - 127.5) / 127.5
    
    # Transponer de HWC (Height, Width, Channels) a CHW (Channels, Height, Width)
    img_array = np.transpose(img_array, (2, 0, 1))
    
    # Añadir dimensión del batch: (1, 3, 112, 112)
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def get_embedding(session, image_path):
    input_name = session.get_inputs()[0].name
    img = preprocess(image_path)
    
    # Ejecutar inferencia en ONNX
    outputs = session.run(None, {input_name: img})
    embedding = outputs[0][0]
    
    # Normalizar el embedding (L2 norm) para calcular similitud de coseno
    embedding = embedding / np.linalg.norm(embedding)
    return embedding

def compare_faces(orig_path, gen_path, model_path="arcface.onnx"):
    # Iniciar sesión de ONNX Runtime
    session = ort.InferenceSession(model_path)
    
    print(f"Calculando embedding para: {orig_path}...")
    emb1 = get_embedding(session, orig_path)
    
    print(f"Calculando embedding para: {gen_path}...")
    emb2 = get_embedding(session, gen_path)
    
    # Similitud de Coseno
    cosine = np.dot(emb1, emb2)
    return float(cosine)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python src/onnx_arcface_validator.py <imagen1> <imagen2>")
        sys.exit(1)
    
    try:
        score = compare_faces(sys.argv[1], sys.argv[2])
        print(f"\n=== RESULTADO ARCFACE (ONNX) ===")
        print(f"Similitud de Coseno: {score:.4f}")
        
        # El umbral estándar de ArcFace para 1:1 es típicamente 0.65-0.68
        if score > 0.68:
            print("✅ PASS: Identidad verificada por ArcFace (Grado Industrial).")
        elif score > 0.60:
            print("⚠️ HUMAN_REVIEW: Identidad probable, pero con margen de error.")
        else:
            print("❌ BLOCKED: Identidad no coincide (ArcFace).")
    except Exception as e:
        print(f"[ERROR] Fallo al procesar: {e}")

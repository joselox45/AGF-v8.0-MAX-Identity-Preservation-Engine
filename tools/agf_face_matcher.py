#!/usr/bin/env python3
"""
AGF v12.3 - Face Matcher (Capa 0 de Emparejamiento)
Detecta todas las caras en ambas imágenes y encuentra la pareja más probable.
"""
import sys
import os
import numpy as np
from PIL import Image
import math
import onnxruntime as ort

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from face_detector import TFLiteFaceDetector

def find_all_faces_with_tiling(img, detector, grid_size=3):
    w, h = img.size
    tile_w, tile_h = w // grid_size, h // grid_size
    detections = []
    
    for y in range(grid_size):
        for x in range(grid_size):
            left, top = x * tile_w, y * tile_h
            right = min(w, left + tile_w + (tile_w // 4))
            bottom = min(h, top + tile_h + (tile_h // 4))
            
            tile = img.crop((left, top, right, bottom))
            res = detector.detect(np.asarray(tile).tolist())
            
            if res.detections:
                for d in res.detections:
                    box = (d.box[0] + left, d.box[1] + top, d.box[2] + left, d.box[3] + top)
                    keypoints = [(kp[0] + left, kp[1] + top) for kp in d.keypoints]
                    detections.append({"box": box, "keypoints": keypoints, "score": d.score})
    
    # Eliminar duplicados aproximados (NMS simple)
    final_detections = []
    for d in detections:
        duplicate = False
        for f in final_detections:
            # Si el centro de las cajas está muy cerca, es un duplicado
            cx1 = (d["box"][0] + d["box"][2]) / 2
            cy1 = (d["box"][1] + d["box"][3]) / 2
            cx2 = (f["box"][0] + f["box"][2]) / 2
            cy2 = (f["box"][1] + f["box"][3]) / 2
            if math.sqrt((cx1-cx2)**2 + (cy1-cy2)**2) < 50: # Umbral de 50px
                duplicate = True
                break
        if not duplicate:
            final_detections.append(d)
            
    return final_detections

def get_affine_face(img, keypoints):
    eye1, eye2 = keypoints[0], keypoints[1]
    scale_factor = 112 / 112.0
    t_eye1 = (38.2946, 51.6963)
    t_eye2 = (73.5318, 51.5014)
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
    return img.transform((112, 112), Image.AFFINE, (a, b, c, d, e, f), resample=Image.BICUBIC)

def get_embedding(session, face_img):
    arr = np.array(face_img).astype(np.float32)
    arr = (arr - 127.5) / 127.5
    arr = np.transpose(arr, (2, 0, 1))
    arr = np.expand_dims(arr, axis=0)
    out = session.run(None, {session.get_inputs()[0].name: arr})[0][0]
    return out / np.linalg.norm(out)

def match_faces(orig_path, gen_path):
    print("[1/3] Cargando modelos...")
    detector = TFLiteFaceDetector(open('blaze_face_short_range.tflite', 'rb').read(), select='largest')
    session = ort.InferenceSession('arcface.onnx')
    
    img_orig = Image.open(orig_path).convert("RGB")
    img_gen = Image.open(gen_path).convert("RGB")
    
    print("[2/3] Buscando todas las caras (Tiling)...")
    faces_orig = find_all_faces_with_tiling(img_orig, detector)
    faces_gen = find_all_faces_with_tiling(img_gen, detector)
    
    if not faces_orig or not faces_gen:
        print("❌ BLOCKED: No se encontraron caras en una o ambas imágenes.")
        return
        
    print(f"    Caras encontradas: {len(faces_orig)} en Original, {len(faces_gen)} en Generada.")
    
    print("[3/3] Emparejando caras con ArcFace (Cross-Matching)...")
    best_score = -1
    best_pair = None
    
    for i, f_orig in enumerate(faces_orig):
        face_orig_aligned = get_affine_face(img_orig, f_orig["keypoints"])
        emb_orig = get_embedding(session, face_orig_aligned)
        
        for j, f_gen in enumerate(faces_gen):
            face_gen_aligned = get_affine_face(img_gen, f_gen["keypoints"])
            emb_gen = get_embedding(session, face_gen_aligned)
            
            score = float(np.dot(emb_orig, emb_gen))
            if score > best_score:
                best_score = score
                best_pair = (f_orig, f_gen, face_orig_aligned, face_gen_aligned)
                
    print(f"\n✅ Mejor pareja encontrada (Score: {best_score:.4f})")
    
    # Guardar los recortes de la mejor pareja
    f_orig, f_gen, crop_orig, crop_gen = best_pair
    crop_orig.save("sandbox/matched_orig.jpg")
    crop_gen.save("sandbox/matched_gen.jpg")
    
    os.system("cp sandbox/matched_orig.jpg ~/storage/downloads/matched_orig.jpg")
    os.system("cp sandbox/matched_gen.jpg ~/storage/downloads/matched_gen.jpg")
    
    print("📸 Recortes guardados en Descargas (matched_orig.jpg y matched_gen.jpg).")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python tools/agf_face_matcher.py <orig> <gen>")
        sys.exit(1)
    match_faces(sys.argv[1], sys.argv[2])

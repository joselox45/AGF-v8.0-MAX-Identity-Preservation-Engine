#!/usr/bin/env python3
"""
AGF v12.3 - Capa 0: Tiling Detector (Detección de caras pequeñas)
Divide la imagen en mosaicos para detectar rostros en fotos de cuerpo entero.
"""
import numpy as np
from PIL import Image
import math

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
    
    # Non-Maximum Suppression (NMS) simple para eliminar duplicados
    if not detections:
        return []
        
    detections.sort(key=lambda d: d["score"], reverse=True)
    final_detections = []
    
    for d in detections:
        keep = True
        for f in final_detections:
            # Calcular IoU (Intersection over Union)
            x1 = max(d["box"][0], f["box"][0])
            y1 = max(d["box"][1], f["box"][1])
            x2 = min(d["box"][2], f["box"][2])
            y2 = min(d["box"][3], f["box"][3])
            
            if x2 > x1 and y2 > y1:
                intersection = (x2 - x1) * (y2 - y1)
                area_d = (d["box"][2] - d["box"][0]) * (d["box"][3] - d["box"][1])
                area_f = (f["box"][2] - f["box"][0]) * (f["box"][3] - f["box"][1])
                union = area_d + area_f - intersection
                iou = intersection / union
                
                if iou > 0.3: # Si se superponen más del 30%, es duplicado
                    keep = False
                    break
        if keep:
            final_detections.append(d)
            
    # Filtrar por calidad (Varianza) para descartar manchas
    valid_faces = []
    for d in final_detections:
        face_aligned = img.crop(d["box"]).resize((112, 112))
        arr = np.array(face_aligned, dtype=np.float32)
        if np.var(arr) > 300: # Umbral mínimo de detalle
            valid_faces.append(d)
            
    return valid_faces

def get_best_face(img, detector):
    """Intenta detección normal; si falla, usa Tiling."""
    # 1. Intento normal
    res = detector.detect(np.asarray(img).tolist())
    if res.detections:
        d = res.detections[0]
        return {"box": d.box, "keypoints": d.keypoints, "score": d.score, "method": "DIRECT"}
        
    # 2. Fallback a Tiling
    tiled_faces = find_all_faces_with_tiling(img, detector)
    if tiled_faces:
        best = tiled_faces[0]
        best["method"] = "TILING"
        return best
        
    return None

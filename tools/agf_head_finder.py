#!/usr/bin/env python3
"""
AGF v12.3 - Head Finder (Tiling approach for full-body photos)
Divide la imagen en mosaicos para que BlazeFace detecte caras pequeñas.
"""
import sys
import os
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from face_detector import TFLiteFaceDetector

def find_faces_with_tiling(image_path, detector, grid_size=3):
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    tile_w, tile_h = w // grid_size, h // grid_size
    
    detections = []
    
    # 1. Escanear cada mosaico
    for y in range(grid_size):
        for x in range(grid_size):
            left = x * tile_w
            top = y * tile_h
            right = min(w, left + tile_w + (tile_w // 4)) # Solapamiento del 25%
            bottom = min(h, top + tile_h + (tile_h // 4))
            
            tile = img.crop((left, top, right, bottom))
            res = detector.detect(np.asarray(tile).tolist())
            
            if res.detections:
                for d in res.detections:
                    # Mapear coordenadas del mosaico a la imagen original
                    box = (
                        d.box[0] + left, d.box[1] + top,
                        d.box[2] + left, d.box[3] + top
                    )
                    keypoints = [(kp[0] + left, kp[1] + top) for kp in d.keypoints]
                    detections.append({
                        "box": box,
                        "keypoints": keypoints,
                        "score": d.score
                    })
    
    # 2. Eliminar duplicados (NMS simple)
    if not detections:
        return None
        
    detections.sort(key=lambda d: d["score"], reverse=True)
    return detections[0] # Devolver la mejor cara detectada

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python tools/agf_head_finder.py <imagen> <blaze_face.tflite>")
        sys.exit(1)

    detector = TFLiteFaceDetector(open(sys.argv[2], "rb").read(), select="largest")
    best_face = find_faces_with_tiling(sys.argv[1], detector)
    
    if best_face:
        print(f"✅ Rostro detectado con Tiling")
        print(f"   Score: {best_face['score']:.2f}")
        print(f"   Box: {[int(x) for x in best_face['box']]}")
    else:
        print(f"❌ NO_FACE_FOUND (Ni siquiera con Tiling)")

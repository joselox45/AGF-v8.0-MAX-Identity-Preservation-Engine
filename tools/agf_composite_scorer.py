#!/usr/bin/env python3
"""
AGF v12.2 - Composite Scorer (4 Métricas)
Calcula Cosine, SSIM, Laplaciano y Luz, y devuelve una media ponderada.
"""
import sys, os, math
import numpy as np
from PIL import Image, ImageFilter, ImageOps
import onnxruntime as ort

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from face_detector import TFLiteFaceDetector
from onnx_arcface_validator import get_aligned_face, get_embedding
from auto_face_auditor import get_affine_aligned_face

def calc_ssim(arr1, arr2):
    mu1, mu2 = np.mean(arr1), np.mean(arr2)
    var1, var2 = np.var(arr1), np.var(arr2)
    cov = np.mean((arr1 - mu1) * (arr2 - mu2))
    C1, C2 = (0.01 * 255)**2, (0.03 * 255)**2
    return ((2 * mu1 * mu2 + C1) * (2 * cov + C2)) / ((mu1**2 + mu2**2 + C1) * (var1 + var2 + C2))

def calc_laplacian_var(img_gray):
    # Aproximación de varianza laplaciana (nitidez) sin OpenCV
    edges = img_gray.filter(ImageFilter.FIND_EDGES)
    return np.var(np.array(edges, dtype=np.float32))

def get_metrics(orig_path, gen_path, model_path="arcface.onnx"):
    detector = TFLiteFaceDetector(open("blaze_face_short_range.tflite", "rb").read(), select="largest")
    session = ort.InferenceSession(model_path)
    
    # 1. Cosine (ArcFace)
    face1_112 = get_aligned_face(orig_path, detector)
    face2_112 = get_aligned_face(gen_path, detector)
    if not face1_112 or not face2_112:
        return None
        
    emb1 = get_embedding(session, face1_112)
    emb2 = get_embedding(session, face2_112)
    cosine = float(np.dot(emb1, emb2))
    
    # 2. SSIM (Textura Alineada)
    img_orig = Image.open(orig_path).convert("RGB")
    img_gen = Image.open(gen_path).convert("RGB")
    res1 = detector.detect(np.asarray(img_orig).tolist())
    res2 = detector.detect(np.asarray(img_gen).tolist())
    
    aligned1 = get_affine_aligned_face(img_orig, res1.detections[0].keypoints).convert('L')
    aligned2 = get_affine_aligned_face(img_gen, res2.detections[0].keypoints).convert('L')
    
    arr1 = np.array(ImageOps.equalize(aligned1.filter(ImageFilter.GaussianBlur(3.0))), dtype=np.float32)
    arr2 = np.array(ImageOps.equalize(aligned2.filter(ImageFilter.GaussianBlur(3.0))), dtype=np.float32)
    ssim = calc_ssim(arr1, arr2)
    
    # 3. Laplaciano (Nitidez / Suavizado)
    lap1 = calc_laplacian_var(aligned1)
    lap2 = calc_laplacian_var(aligned2)
    # Ratio de nitidez (si la gen es muy suave, el ratio baja)
    lap_score = min(lap1, lap2) / max(lap1, lap2) if max(lap1, lap2) > 0 else 0
    
    # 4. Luz (Diferencia de media de luminancia)
    mu1, mu2 = np.mean(arr1), np.mean(arr2)
    light_score = 1.0 - (abs(mu1 - mu2) / 255.0)
    
    return cosine, ssim, lap_score, light_score

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python tools/agf_composite_scorer.py <orig> <gen>")
        sys.exit(1)
        
    metrics = get_metrics(sys.argv[1], sys.argv[2])
    if not metrics:
        print("❌ BLOCKED: Fallo en detección facial.")
        sys.exit(1)
        
    cosine, ssim, lap, light = metrics
    
    # Compuerta Dura: Si la identidad falla, no importa el resto.
    if cosine < 0.79:
        print(f"\n=== RESULTADO AGF (COMPOSITE) ===")
        print(f"❌ BLOCKED: Cosine {cosine:.4f} < 0.79 (Identidad no coincide).")
        sys.exit(1)
        
    # Media Ponderada (40% Cos, 40% SSIM, 10% Lap, 10% Light)
    composite = (cosine * 0.40) + (ssim * 0.40) + (lap * 0.10) + (light * 0.10)
    
    print(f"\n=== RESULTADO AGF (COMPOSITE) ===")
    print(f"Cosine (40%):      {cosine:.4f}")
    print(f"SSIM (40%):        {ssim:.4f}")
    print(f"Laplaciano (10%):  {lap:.4f}")
    print(f"Luz (10%):         {light:.4f}")
    print("-" * 34)
    print(f"SCORE FINAL:       {composite:.4f} (Umbral > 0.85 PASS)")
    
    if composite >= 0.85:
        print("✅ PASS: Identidad y textura preservadas.")
    elif composite >= 0.70:
        print("⚠️ HUMAN_REVIEW: Drift bajo, requiere validación humana.")
    else:
        print("❌ FAIL: Alteración agresiva detectada.")

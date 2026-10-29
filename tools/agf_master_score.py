#!/usr/bin/env python3
"""
AGF v12.2 - Master Score (Identity-First + Restoration Mode)
"""
import sys
import os
import warnings
import numpy as np
from PIL import Image, ImageFilter, ImageOps
import math
import argparse

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from face_detector import TFLiteFaceDetector
import onnxruntime as ort

def get_affine_aligned_face(img, keypoints, target_size=(256, 256)):
    eye1, eye2 = keypoints[0], keypoints[1]
    scale_factor = 256 / 112.0
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

def compute_metrics(orig_path, gen_path, detector, session):
    img1 = Image.open(orig_path).convert("RGB")
    img2 = Image.open(gen_path).convert("RGB")
    res1 = detector.detect(np.asarray(img1).tolist())
    res2 = detector.detect(np.asarray(img2).tolist())
    
    if res1.status != "PASS" or not res1.detections or res2.status != "PASS" or not res2.detections:
        return None, None

    face1_112 = get_affine_aligned_face(img1, res1.detections[0].keypoints, (112, 112))
    face2_112 = get_affine_aligned_face(img2, res2.detections[0].keypoints, (112, 112))
    
    def get_emb(face):
        arr = np.array(face).astype(np.float32)
        arr = (arr - 127.5) / 127.5
        arr = np.transpose(arr, (2, 0, 1))
        arr = np.expand_dims(arr, axis=0)
        out = session.run(None, {session.get_inputs()[0].name: arr})[0][0]
        return out / np.linalg.norm(out)
        
    cosine = float(np.dot(get_emb(face1_112), get_emb(face2_112)))

    face1_256 = get_affine_aligned_face(img1, res1.detections[0].keypoints, (256, 256))
    face2_256 = get_affine_aligned_face(img2, res2.detections[0].keypoints, (256, 256))
    
    def get_ssim_arr(face):
        gray = face.convert('L')
        eq = ImageOps.equalize(gray)
        blur = eq.filter(ImageFilter.GaussianBlur(radius=3.0))
        return np.array(blur, dtype=np.float32)

    arr1, arr2 = get_ssim_arr(face1_256), get_ssim_arr(face2_256)
    mu1, mu2 = np.mean(arr1), np.mean(arr2)
    var1, var2 = np.var(arr1), np.var(arr2)
    cov = np.mean((arr1 - mu1) * (arr2 - mu2))
    C1, C2 = (0.01 * 255)**2, (0.03 * 255)**2
    ssim = float(((2 * mu1 * mu2 + C1) * (2 * cov + C2)) / ((mu1**2 + mu2**2 + C1) * (var1 + var2 + C2)))
    
    return cosine, ssim

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("orig")
    parser.add_argument("gen")
    parser.add_argument("detector")
    parser.add_argument("--mode", choices=["preservation", "restoration"], default="preservation")
    args = parser.parse_args()

    detector = TFLiteFaceDetector(open(args.detector, "rb").read(), select="largest")
    session = ort.InferenceSession("arcface.onnx")
    
    cosine, ssim = compute_metrics(args.orig, args.gen, detector, session)
    
    if cosine is None or ssim is None:
        print("❌ BLOCKED: No se detectó rostro.")
        sys.exit(1)

    print(f"\n=== AGF MASTER SCORE [{args.mode.upper()}] ===")
    print(f"[Identidad] Cosine (ArcFace): {cosine:.4f}")
    print(f"[Textura]   SSIM (Estructural): {ssim:.4f}")
    print(f"----------------------------------------")

    if args.mode == "preservation":
        if cosine < 0.65:
            print("🚨 BLOCKED: Identidad no coincide. (Cosine < 0.65)")
        elif cosine >= 0.79 and ssim >= 0.90:
            print("✅ PASS: Identidad y textura preservadas perfectamente.")
        elif cosine >= 0.79 and ssim < 0.90:
            print("⚠️ HUMAN_REVIEW: Identidad confirmada, pero textura alterada.")
        else:
            print("⚠️ HUMAN_REVIEW: Identidad probable, requiere validación.")
            
    elif args.mode == "restoration":
        # En restauración, el umbral de bloqueo es más bajo (0.55)
        if cosine < 0.55:
            print("🚨 BLOCKED: La IA alucinó una identidad diferente. (Cosine < 0.55)")
        elif ssim >= 0.85 and cosine >= 0.65:
            print("✅ PASS (Restoration): Restauración excelente. Identidad clara.")
        else:
            print("⚠️ HUMAN_REVIEW: Restauración aceptable. Requiere validación visual humana.")

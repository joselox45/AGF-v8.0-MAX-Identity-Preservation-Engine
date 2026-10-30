#!/usr/bin/env python3
"""
AGF v12.2 - COMPOSITE SCORER (Weighted 4-Layer Engine)
Integra: ArcFace (40%) + Fourier (30%) + Edge Shazam (20%) + SSIM (10%)
"""
import sys
import os
import numpy as np
from PIL import Image, ImageFilter, ImageOps
import math
import json
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.dirname(__file__))

from face_detector import TFLiteFaceDetector
from agf_texture_shazam import get_aligned_edge_fingerprint
from agf_fourier_auditor import get_fft_spectrum
from agf_color_fingerprint import get_dominant_colors, compare_color_fingerprints
from agf_overlay_diff import generate_overlay_diff
import onnxruntime as ort

def get_affine_aligned_face(img, keypoints, target_size=(112, 112)):
    eye1, eye2 = keypoints[0], keypoints[1]
    scale_factor = 112 / 112.0
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

def compute_all_metrics(orig_path, gen_path, detector, session):
    img1 = Image.open(orig_path).convert("RGB")
    img2 = Image.open(gen_path).convert("RGB")
    
    res1 = detector.detect(np.asarray(img1).tolist())
    res2 = detector.detect(np.asarray(img2).tolist())
    
    if not res1.detections or not res2.detections:
        return None

    # --- 1. ARCFACE ---
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

    # --- 2. FOURIER 2D ---
    spec1 = get_fft_spectrum(orig_path, detector)
    spec2 = get_fft_spectrum(gen_path, detector)
    
    if spec1 is not None and spec2 is not None:
        c = 128; crop = 40
        s1 = spec1[c-crop:c+crop, c-crop:c+crop].astype(np.float32)
        s2 = spec2[c-crop:c+crop, c-crop:c+crop].astype(np.float32)
        dot = np.sum(s1 * s2); norm1 = np.linalg.norm(s1); norm2 = np.linalg.norm(s2)
        fourier = float(dot / (norm1 * norm2)) if norm1 > 0 and norm2 > 0 else 0.0
    else:
        fourier = 0.0

    # --- 3. EDGE SHAZAM ---
    arr_orig = get_aligned_edge_fingerprint(orig_path, detector)
    arr_gen = get_aligned_edge_fingerprint(gen_path, detector)
    
    if arr_orig is not None and arr_gen is not None:
        valid = (arr_orig > 0) | (arr_gen > 0)
        a1, a2 = arr_orig[valid], arr_gen[valid]
        mu1, mu2 = np.mean(a1), np.mean(a2)
        var1, var2 = np.var(a1), np.var(a2)
        cov = np.mean((a1 - mu1) * (a2 - mu2))
        C1, C2 = (0.01 * 255)**2, (0.03 * 255)**2
        shazam = float(((2 * mu1 * mu2 + C1) * (2 * cov + C2)) / ((mu1**2 + mu2**2 + C1) * (var1 + var2 + C2)))
    else:
        shazam = 0.0

    # --- 4. SSIM CLÁSICO ---
    f1 = get_affine_aligned_face(img1, res1.detections[0].keypoints, (256, 256)).convert('L')
    f2 = get_affine_aligned_face(img2, res2.detections[0].keypoints, (256, 256)).convert('L')
    arr1 = np.array(ImageOps.equalize(f1).filter(ImageFilter.GaussianBlur(3)), dtype=np.float32)
    arr2 = np.array(ImageOps.equalize(f2).filter(ImageFilter.GaussianBlur(3)), dtype=np.float32)
    
    mu1, mu2 = np.mean(arr1), np.mean(arr2)
    var1, var2 = np.var(arr1), np.var(arr2)
    cov = np.mean((arr1 - mu1) * (arr2 - mu2))
    ssim = float(((2 * mu1 * mu2 + C1) * (2 * cov + C2)) / ((mu1**2 + mu2**2 + C1) * (var1 + var2 + C2)))

    # --- 5. COLOR FINGERPRINT ---
    orig_colors = get_dominant_colors(orig_path)
    gen_colors = get_dominant_colors(gen_path)
    hue_diff = compare_color_fingerprints(orig_colors, gen_colors, "restoration")
    # Convertir diferencia de matiz a score (0-1): 0 grados = 1.0, 180 grados = 0.0
    color_score = max(0.0, 1.0 - (hue_diff / 180.0))
    
    # --- 6. FLATNESS ---

    # --- 7. OVERLAY DIFF (Visual) ---
    overlay_result = generate_overlay_diff(orig_path, gen_path, detector)
    if overlay_result is not None:
        drift_pct = overlay_result
    else:
        drift_pct = 0.0

    return {
        "cosine": cosine,
        "fourier": fourier,
        "shazam": shazam,
        "ssim": ssim,
        "color": color_score,
        "hue_diff": hue_diff,
        "overlay_drift": drift_pct
    }

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python tools/agf_composite_scorer.py <orig> <gen> <blaze_face.tflite> [--mode preservation|restoration]")
        sys.exit(1)

    mode = "preservation"
    if "--mode" in sys.argv:
        mode = sys.argv[sys.argv.index("--mode") + 1]

    print(f"[INFO] Cargando modelos para auditoría ponderada (Modo: {mode.upper()})...")
    detector = TFLiteFaceDetector(open(sys.argv[3], "rb").read(), select="largest")
    session = ort.InferenceSession("arcface.onnx")
    
    metrics = compute_all_metrics(sys.argv[1], sys.argv[2], detector, session)
    
    if not metrics:
        print("❌ BLOCKED: No se detectó rostro en una o ambas imágenes.")
        sys.exit(1)

    # --- PONDERACIÓN INDUSTRIAL ---
    W_IDENTITY = 0.40
    W_FOURIER  = 0.30
    W_SHAZAM   = 0.19
    W_SSIM     = 0.10
    W_COLOR    = 0.05

    # 1. Calcular Ponderación (Siempre se calcula)
    agf_score = (metrics['cosine'] * W_IDENTITY) + \
                (metrics['fourier'] * W_FOURIER) + \
                (metrics['shazam'] * W_SHAZAM) + \
                (metrics['ssim'] * W_SSIM) + \
                (metrics['color'] * W_COLOR) + \

    
    # 2. Hard Gates Extremos (Solo casos catastróficos)
    # Si ArcFace < 0.30 o Fourier < 0.40, la ponderación no puede salvar la imagen
    verdict = "PASS"
    reason = ""
    
    if metrics['cosine'] < 0.30:
        verdict = "BLOCKED"
        reason = f"Hard Gate Extremo: ArcFace {metrics['cosine']:.3f} < 0.30 (Cara no reconocible)"
    elif metrics['fourier'] < 0.40:
        verdict = "BLOCKED"
        reason = f"Hard Gate Extremo: Fourier {metrics['fourier']:.3f} < 0.40 (Alucinación total)"
    else:
        # La Ponderación decide el Veredicto Final
        if mode == 'preservation' and agf_score >= 0.7825 or mode == 'restoration' and agf_score >= 0.60:
            verdict = "PASS"
        elif mode == 'preservation' and agf_score >= 0.6325 or mode == 'restoration' and agf_score >= 0.45:
            verdict = "HUMAN_REVIEW"
            reason = "Score moderado: requiere validación humana"
        else:
            verdict = "BLOCKED"
            reason = f"Score ponderado muy bajo ({agf_score:.3f})"


    print("\n" + "="*55)
    print(" 🛡️  AGF v12.2 - WEIGHTED COMPOSITE AUDIT")
    print("="*55)
    print(f" [1] Identidad (ArcFace) [40%] : {metrics['cosine']:.4f}")
    print(f" [2] Firma de Frecuencia [30%] : {metrics['fourier']:.4f}")
    print(f" [3] Estructura (Shazam) [20%] : {metrics['shazam']:.4f}")
    print(f" [4] Píxeles (SSIM)      [10%] : {metrics['ssim']:.4f}")
    print(f" [5] Huella Cromática    [ 5%] : {metrics['color']:.4f} (ΔH={metrics['hue_diff']:.1f}°)")
    print(f" [7] Overlay Diff (Visual): {metrics['overlay_drift']:.2f}% de Deriva")
    print("-" * 55)
    print(f" 🏆 AGF SCORE PONDERADO        : {agf_score:.4f}")
    print("-" * 55)
    
    if verdict == "PASS":
        print(" ✅ VEREDICTO: PASS (Identidad y Textura Blindadas)")
    elif verdict == "HUMAN_REVIEW":
        print(f" ⚠️ VEREDICTO: HUMAN_REVIEW ({reason})")
    else:
        print(f" 🚨 VEREDICTO: BLOCKED ({reason})")
    
    print("="*55)
    
    # Guardar JSON de evidencia
    os.makedirs("termux_sealed", exist_ok=True)
    report = {
        "engine": "AGF-v12.2-Weighted-Composite",
        "timestamp": datetime.now().isoformat(),
        "mode": mode,
        "metrics": metrics,
        "weights": {"identity": 0.40, "fourier": 0.30, "shazam": 0.20, "ssim": 0.10},
        "agf_score": round(agf_score, 4),
        "verdict": verdict,
        "reason": reason
    }
    with open("termux_sealed/composite_audit.json", "w") as f:
        json.dump(report, f, indent=4)
    print(f"📄 Evidencia guardada en termux_sealed/composite_audit.json")

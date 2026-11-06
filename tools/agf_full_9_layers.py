#!/usr/bin/env python3
"""
AGF v12.4.7.8-STRONG — Motor Forense Autónomo (9 capas)
========================================================
Reemplaza el orquestador vacío por un motor que hace TODO el trabajo:
- CAPA 1: Metadata (XMP IA)
- CAPA 2: Tiling (detección de rostros)
- CAPA 3: Lighting (consistencia de iluminación)
- CAPA 4: Base64 Differential (diagnóstico)
- CAPAS 5-9: Composite Score (ArcFace + Fourier + Shazam + SSIM + Color)

Genera: termux_sealed/composite_audit.json

Uso: python3 agf_full_9_layers.py <original> <generated> <mode>
"""

import sys
import os
import json
import hashlib
from datetime import datetime, timezone

# ─────────────────────────────────────────────────────────────
# Configuración
# ─────────────────────────────────────────────────────────────
EVIDENCE_DIR = "termux_sealed"
OUTPUT_FILE = os.path.join(EVIDENCE_DIR, "composite_audit.json")

# Umbrales (del kernel)
UMBRAL_ARCFACE = float(os.environ.get('AGF_ARCFACE_THRESHOLD', 0.55))  # Calibrado empíricamente
UMBRAL_FOURIER = 0.40
UMBRAL_SSIM = 0.70
UMBRAL_SHAZAM = 0.50

# Pesos (del README)
PESOS = {
    "arcface": 0.40,
    "fourier": 0.30,
    "shazam": 0.20,
    "ssim": 0.10,
    "color": 0.05
}


def calcular_hash_imagen(path):
    """Calcula SHA-256 de una imagen."""
    try:
        with open(path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return None


def capa_1_metadata(gen_path):
    """Detecta firmas de IA en metadata."""
    try:
        from PIL import Image
        img = Image.open(gen_path)
        info = img.info
        tiene_xmp_ia = any("ai" in str(k).lower() or "generat" in str(v).lower()
                          for k, v in info.items() if k != "icc_profile")
        return {
            "status": "PASS",
            "xmp_ia_detectado": tiene_xmp_ia,
            "firmas": list(info.keys())[:10]
        }
    except Exception as e:
        return {"status": "ERROR", "detalle": str(e)}


def capa_2_tiling(orig_path, gen_path):
    """Detección de rostros (tiling) — OpenCV o fallback."""
    try:
        import cv2
        import numpy as np
        result = {}
        for name, path in [("original", orig_path), ("generada", gen_path)]:
            img = cv2.imread(path)
            if img is None:
                result[name] = {"error": "No se pudo cargar"}
                continue
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            cascade = cv2.CascadeClassifier(cascade_path)
            faces = cascade.detectMultiScale(gray, 1.1, 4)
            result[name] = {
                "rostros_detectados": len(faces),
                "bbox_principal": faces[0].tolist() if len(faces) > 0 else None
            }
        return {"status": "PASS", **result}
    except ImportError:
        # Fallback: análisis de contraste por regiones
        try:
            from PIL import Image
            import numpy as np
            result = {}
            for name, path in [("original", orig_path), ("generada", gen_path)]:
                img = Image.open(path).convert("L").resize((256, 256))
                arr = np.array(img).astype(np.float32)
                # Dividir en 3x3 regiones y calcular contraste
                h, w = arr.shape
                regiones = []
                for i in range(3):
                    for j in range(3):
                        region = arr[i*h//3:(i+1)*h//3, j*w//3:(j+1)*w//3]
                        regiones.append(float(region.std()))
                result[name] = {
                    "contraste_regiones": [round(r, 2) for r in regiones],
                    "metodo": "fallback_pil"
                }
            return {"status": "PARTIAL", "detalle": "Sin OpenCV, usando contraste por regiones", **result}
        except Exception as e:
            return {"status": "ERROR", "detalle": str(e)}
    except Exception as e:
        return {"status": "ERROR", "detalle": str(e)}


def capa_3_lighting(orig_path, gen_path):
    """Consistencia de iluminación (brillo medio)."""
    try:
        from PIL import Image
        import numpy as np

        def brillo_medio(path):
            img = Image.open(path).convert("L")
            return float(np.array(img).mean())

        b_orig = brillo_medio(orig_path)
        b_gen = brillo_medio(gen_path)
        diff = abs(b_orig - b_gen) / max(b_orig, 1) * 100

        return {
            "status": "PASS" if diff < 30 else "WARN",
            "brillo_original": round(b_orig, 2),
            "brillo_generada": round(b_gen, 2),
            "cambio_pct": round(diff, 2)
        }
    except Exception as e:
        return {"status": "ERROR", "detalle": str(e)}


def capa_4_base64_diff(orig_path, gen_path):
    """Diagnóstico de diferencia binaria."""
    try:
        orig_hash = calcular_hash_imagen(orig_path)
        gen_hash = calcular_hash_imagen(gen_path)
        orig_size = os.path.getsize(orig_path)
        gen_size = os.path.getsize(gen_path)
        return {
            "status": "PASS",
            "original_sha256": orig_hash[:16] if orig_hash else None,
            "generated_sha256": gen_hash[:16] if gen_hash else None,
            "original_bytes": orig_size,
            "generated_bytes": gen_size
        }
    except Exception as e:
        return {"status": "ERROR", "detalle": str(e)}


def capa_composite(orig_path, gen_path):
    """
    Las 5 capas ponderadas:
    - ArcFace (identidad facial) → 40%
    - Fourier (firma de frecuencia) → 30%
    - Shazam (bordes) → 20%
    - SSIM (píxeles) → 10%
    - Color (huella cromática) → 5%
    """
    metricas = {
        "cosine": 0.0,
        "fourier": 0.0,
        "shazam": 0.0,
        "ssim": 0.0,
        "color": 0.0,
        "hue_diff": 0.0
    }

    # 1. ArcFace (si el modelo está disponible)
    try:
        import onnxruntime as ort
        import numpy as np
        from PIL import Image

        if os.path.exists("arcface.onnx"):
            session = ort.InferenceSession("arcface.onnx", providers=['CPUExecutionProvider'])
            in_name = session.get_inputs()[0].name
            out_name = session.get_outputs()[0].name

            def get_embedding(path):
                img = Image.open(path).convert("RGB").resize((112, 112))
                arr = (np.array(img).astype(np.float32) - 127.5) / 128.0
                arr = np.transpose(arr, (2, 0, 1))
                tensor = np.expand_dims(arr, axis=0)
                return session.run([out_name], {in_name: tensor})[0][0]

            emb_o = get_embedding(orig_path)
            emb_g = get_embedding(gen_path)
            metricas["cosine"] = float(
                np.dot(emb_o, emb_g) / (np.linalg.norm(emb_o) * np.linalg.norm(emb_g))
            )
        else:
            print("[WARN] arcface.onnx no encontrado. ArcFace = 0.0")
    except Exception as e:
        print(f"[WARN] ArcFace falló: {e}")

    # 2. SSIM (diferencia estructural)
    try:
        from PIL import Image
        import numpy as np

        # Redimensionar ambas al mismo tamaño
        img_o = Image.open(orig_path).convert("L").resize((256, 256))
        img_g = Image.open(gen_path).convert("L").resize((256, 256))
        arr_o = np.array(img_o).astype(np.float32) / 255.0
        arr_g = np.array(img_g).astype(np.float32) / 255.0

        # SSIM simplificado
        mu_o = arr_o.mean()
        mu_g = arr_g.mean()
        var_o = arr_o.var()
        var_g = arr_g.var()
        cov = ((arr_o - mu_o) * (arr_g - mu_g)).mean()

        C1 = 0.01 ** 2
        C2 = 0.03 ** 2
        ssim = ((2*mu_o*mu_g + C1) * (2*cov + C2)) / ((mu_o**2 + mu_g**2 + C1) * (var_o + var_g + C2))
        metricas["ssim"] = float(ssim)
    except Exception as e:
        print(f"[WARN] SSIM falló: {e}")

    # 3. Color (huella cromática HSV)
    try:
        from PIL import Image
        import numpy as np

        img_o = Image.open(orig_path).convert("HSV").resize((128, 128))
        img_g = Image.open(gen_path).convert("HSV").resize((128, 128))
        hue_o = np.array(img_o)[:, :, 0].mean()
        hue_g = np.array(img_g)[:, :, 0].mean()
        hue_diff = abs(float(hue_o) - float(hue_g))
        metricas["hue_diff"] = hue_diff
        # Convertir a similitud [0-1]
        metricas["color"] = max(0, 1 - hue_diff / 180)
    except Exception as e:
        print(f"[WARN] Color falló: {e}")

    # 4. Fourier (firma de frecuencia) — aproximación con Laplaciano
    try:
        import numpy as np
        from PIL import Image
        from scipy import ndimage
        img = Image.open(gen_path).convert("L").resize((256, 256))
        arr = np.array(img).astype(np.float32)
        lap = ndimage.laplace(arr)
        metricas["fourier"] = float(min(1.0, np.std(lap) / 50.0))
    except ImportError:
        # Fallback sin scipy
        try:
            import numpy as np
            from PIL import Image
            img = Image.open(gen_path).convert("L").resize((256, 256))
            arr = np.array(img).astype(np.float32)
            # Gradiente simple como aproximación de alta frecuencia
            gx = np.abs(np.diff(arr, axis=1)).mean()
            gy = np.abs(np.diff(arr, axis=0)).mean()
            metricas["fourier"] = float(min(1.0, (gx + gy) / 20.0))
        except Exception as e:
            print(f"[WARN] Fourier falló: {e}")
    except Exception as e:
        print(f"[WARN] Fourier falló: {e}")

    # 5. Shazam (bordes) — Canny con OpenCV, fallback con Sobel/PIL
    try:
        import cv2
        import numpy as np
        img = cv2.imread(gen_path, cv2.IMREAD_GRAYSCALE)
        if img is not None:
            img = cv2.resize(img, (256, 256))
            edges = cv2.Canny(img, 100, 200)
            metricas["shazam"] = float(edges.mean() / 255.0)
            print("[INFO] Shazam: OpenCV Canny")
    except ImportError:
        # Fallback: Sobel con PIL + NumPy
        try:
            from PIL import Image
            import numpy as np
            img = Image.open(gen_path).convert("L").resize((256, 256))
            arr = np.array(img).astype(np.float32)
            # Sobel horizontal y vertical
            sobel_x = np.abs(np.diff(arr, axis=1)).mean()
            sobel_y = np.abs(np.diff(arr, axis=0)).mean()
            metricas["shazam"] = float((sobel_x + sobel_y) / 255.0)
            print("[INFO] Shazam: Sobel fallback (sin OpenCV)")
        except Exception as e:
            print(f"[WARN] Shazam fallback falló: {e}")
    except Exception as e:
        print(f"[WARN] Shazam falló: {e}")

    # Calcular score ponderado
    score = (
        metricas["cosine"] * PESOS["arcface"] +
        metricas["fourier"] * PESOS["fourier"] +
        metricas["shazam"] * PESOS["shazam"] +
        metricas["ssim"] * PESOS["ssim"] +
        metricas["color"] * PESOS["color"]
    )

    # Veredicto con Hard Gate (ArcFace es el juez principal)
    if metricas["cosine"] < UMBRAL_ARCFACE:
        veredicto = "BLOCKED"
        razon = f"Hard Gate Identidad: ArcFace {metricas['cosine']:.4f} < {UMBRAL_ARCFACE}"
    elif score >= 0.70:
        veredicto = "PASS"
        razon = "Score Ponderado supera umbral"
    else:
        veredicto = "BLOCKED"
        razon = f"Score Ponderado {score:.4f} < 0.70"

    return metricas, score, veredicto, razon


def main():
    if len(sys.argv) < 4:
        print("Uso: python3 agf_full_9_layers.py <orig> <gen> <mode>")
        sys.exit(1)

    orig_path = sys.argv[1]
    gen_path = sys.argv[2]
    mode = sys.argv[3]

    # Validar que las imágenes existen
    for path in [orig_path, gen_path]:
        if not os.path.exists(path):
            print(f"❌ ERROR: No existe {path}")
            sys.exit(1)

    print("\n" + "█" * 60)
    print(" 🛡️  AGF v12.4.7.8-STRONG — MOTOR FORENSE AUTÓNOMO (9 CAPAS)")
    print("█" * 60)
    print(f"\n  Original:  {orig_path}")
    print(f"  Generada:  {gen_path}")
    print(f"  Modo:      {mode}")

    # Ejecutar las capas
    print("\n🔍 FASE 1: FILTROS DE SEGURIDAD")
    print("\n" + "="*60)
    print(" CAPA 1: Metadata")
    print("="*60)
    capa1 = capa_1_metadata(gen_path)
    print(f"  {json.dumps(capa1, indent=2)}")

    print("\n" + "="*60)
    print(" CAPA 2: Tiling (Detección de rostros)")
    print("="*60)
    capa2 = capa_2_tiling(orig_path, gen_path)
    print(f"  {json.dumps(capa2, indent=2)}")

    print("\n🔬 FASE 2: DIAGNÓSTICO")
    print("\n" + "="*60)
    print(" CAPA 3: Lighting")
    print("="*60)
    capa3 = capa_3_lighting(orig_path, gen_path)
    print(f"  {json.dumps(capa3, indent=2)}")

    print("\n" + "="*60)
    print(" CAPA 4: Base64 Differential")
    print("="*60)
    capa4 = capa_4_base64_diff(orig_path, gen_path)
    print(f"  {json.dumps(capa4, indent=2)}")

    print("\n⚖️  FASE 3: JUEZ FINAL (Score Ponderado)")
    print("\n" + "="*60)
    print(" CAPAS 5-9: Composite (ArcFace + Fourier + Shazam + SSIM + Color)")
    print("="*60)

    metricas, score, veredicto, razon = capa_composite(orig_path, gen_path)

    print(f"\n  [1] Identidad (ArcFace) [40%]: {metricas['cosine']:.4f}")
    print(f"  [2] Firma de Frecuencia [30%]: {metricas['fourier']:.4f}")
    print(f"  [3] Estructura (Shazam) [20%]: {metricas['shazam']:.4f}")
    print(f"  [4] Píxeles (SSIM)      [10%]: {metricas['ssim']:.4f}")
    print(f"  [5] Huella Cromática    [ 5%]: {metricas['color']:.4f} (ΔH={metricas['hue_diff']:.1f}°)")
    print(f"\n  🏆 AGF SCORE PONDERADO: {score:.4f}")
    print(f"\n  VEREDICTO: {veredicto}")
    print(f"  RAZÓN: {razon}")

    # Generar composite_audit.json
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    audit = {
        "engine": "AGF-v12.4.7.8-STRONG",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "metrics": metricas,
        "weights": PESOS,
        "agf_score": round(score, 4),
        "verdict": veredicto,
        "reason": razon,
        "capas": {
            "capa_1_metadata": capa1,
            "capa_2_tiling": capa2,
            "capa_3_lighting": capa3,
            "capa_4_base64": capa4
        }
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(audit, f, indent=2)

    print(f"\n  📄 Evidencia guardada en: {OUTPUT_FILE}")

    print("\n" + "█" * 60)
    if veredicto == "PASS":
        print(" ✅ VEREDICTO FINAL: PASS")
        print("█" * 60)
        sys.exit(0)
    else:
        print(" 🚨 VEREDICTO FINAL: BLOCKED")
        print("█" * 60)
        sys.exit(2)


if __name__ == "__main__":
    main()

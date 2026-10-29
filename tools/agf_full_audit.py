#!/usr/bin/env python3
"""
AGF v12.2 - Full Audit Orchestrator (Zero-Trust & Full Lineage Archive)
Une el Pre-Seal con la Generación. Audita, sella y archiva TODO el linaje en termux_sealed/.
"""
import sys
import os
import json
import hashlib
import argparse
import warnings
import shutil
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
from agf_master_score import compute_metrics
from face_detector import TFLiteFaceDetector
import onnxruntime as ort

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings("ignore")

def get_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def apply_watermark(image_path, text, output_path):
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size
    txt_layer = Image.new('RGBA', img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)
    try:
        font_size = max(15, int(height * 0.03))
        font = ImageFont.truetype("/system/fonts/Roboto-Regular.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    x, y = width - (bbox[2] - bbox[0]) - 15, height - (bbox[3] - bbox[1]) - 15
    draw.text((x + 1, y + 1), text, font=font, fill=(0, 0, 0, 150))
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 200))
    watermarked = Image.alpha_composite(img, txt_layer)
    watermarked.convert("RGB").save(output_path, quality=95)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("sealed_orig", help="Imagen original _SEALED.jpg")
    parser.add_argument("gen", help="Imagen generada por el LLM")
    parser.add_argument("--mode", choices=["preservation", "restoration"], default="preservation")
    args = parser.parse_args()

    # 1. Buscar el certificado de origen
    cert_orig_path = os.path.splitext(args.sealed_orig)[0].replace("_SEALED", "_SEALED.agf") + ".json"
    if not os.path.exists(cert_orig_path):
        cert_orig_path = os.path.splitext(args.sealed_orig)[0] + ".agf.json"
        
    if not os.path.exists(cert_orig_path):
        print(f"❌ BLOCKED: No se encontró el certificado Pre-Seal para {args.sealed_orig}")
        sys.exit(1)
        
    with open(cert_orig_path, "r") as f:
        cert_orig = json.load(f)

    print(f"=== AGF FULL AUDIT [{args.mode.upper()}] ===")
    print(f"[🔗] Certificado de origen encontrado. Autor: {cert_orig.get('author', 'Desconocido')}")

    # 2. Ejecutar Auditoría
    print(f"[⚙️] Ejecutando Master Score...")
    detector = TFLiteFaceDetector(open("blaze_face_short_range.tflite", "rb").read(), select="largest")
    session = ort.InferenceSession("arcface.onnx")
    
    cosine, ssim = compute_metrics(args.sealed_orig, args.gen, detector, session)
    if cosine is None or ssim is None:
        print("❌ BLOCKED: No se detectó rostro en una o ambas imágenes.")
        sys.exit(1)

    print(f"[Identidad] Cosine (ArcFace): {cosine:.4f}")
    print(f"[Textura]   SSIM (Estructural): {ssim:.4f}")
    
    # 3. Lógica de Decisión
    verdict = "FAIL"
    if args.mode == "preservation":
        if cosine < 0.65: verdict = "BLOCKED"
        elif cosine >= 0.79 and ssim >= 0.90: verdict = "PASS"
        elif cosine >= 0.79 and ssim < 0.90: verdict = "HUMAN_REVIEW"
        else: verdict = "HUMAN_REVIEW"
    elif args.mode == "restoration":
        if cosine < 0.55: verdict = "BLOCKED"
        elif cosine >= 0.65 and ssim >= 0.85: verdict = "PASS"
        else: verdict = "HUMAN_REVIEW"

    print(f"----------------------------------------")
    print(f"🏆 VEREDICTO: {verdict}")
    print(f"----------------------------------------")

    if verdict == "BLOCKED":
        print("🚨 El proceso se detiene. La imagen no será sellada.")
        sys.exit(1)

    # 4. Preparar carpeta de archivo oficial (termux_sealed)
    archive_dir = "termux_sealed"
    os.makedirs(archive_dir, exist_ok=True)
    
    base_name = os.path.splitext(os.path.basename(args.gen))[0]
    final_img_path = os.path.join(archive_dir, f"{base_name}_AGF_SEALED.jpg")
    cert_final_path = os.path.join(archive_dir, f"{base_name}_AGF_SEALED.agf.json")

    # 5. Sellar imagen final
    author = cert_orig.get('author', 'AGF_USER')
    apply_watermark(args.gen, f"{author} | AGF", final_img_path)
    print(f"✅ Sello visual aplicado y archivado en: {final_img_path}")

    # 6. Mover los archivos de origen al archivo (Linaje Completo)
    lineage_orig_img = os.path.join(archive_dir, os.path.basename(args.sealed_orig))
    lineage_orig_cert = os.path.join(archive_dir, os.path.basename(cert_orig_path))
    shutil.copy2(args.sealed_orig, lineage_orig_img)
    shutil.copy2(cert_orig_path, lineage_orig_cert)
    print(f"✅ Linaje original archivado en: {archive_dir}/")

    hash_gen = get_sha256(args.gen)
    cert_final = {
        "agf_protocol": "AGF-LINKED-GENERATION-v1",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict,
        "metrics": {"cosine": round(cosine, 4), "ssim": round(ssim, 4)},
        "lineage": {
            "original_file": cert_orig.get("original_file"),
            "original_sha256": cert_orig.get("original_sha256"),
            "sealed_file": cert_orig.get("sealed_file"),
            "sealed_sha256": cert_orig.get("sealed_sha256"),
            "generated_file": os.path.basename(args.gen),
            "generated_sha256": hash_gen,
            "final_sealed_file": os.path.basename(final_img_path)
        }
    }
    
    with open(cert_final_path, "w") as f:
        json.dump(cert_final, f, indent=4)
        
    print(f"✅ Certificado de Linaje archivado en: {cert_final_path}")
    
    # 7. Limpieza total
    os.remove(args.gen)
    os.remove(args.sealed_orig)
    os.remove(cert_orig_path)
    print(f"🧹 Archivos temporales eliminados. Todo el linaje vive en {archive_dir}/.")
    
    print(f"\n🔗 Cadena de confianza completa:")
    print(f"   Original ({cert_orig.get('original_sha256')[:8]}...) -> Generada ({hash_gen[:8]}...)")

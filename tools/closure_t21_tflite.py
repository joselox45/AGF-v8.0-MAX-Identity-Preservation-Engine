#!/usr/bin/env python3
"""Cierre T21/T22 con detector + alineacion (T21-ALIGN).
uso: closure_t21_tflite.py REF TGT MODELO kind norm [DETECTOR.tflite]
Si DETECTOR se da: detecta rostro, alinea a 112x112 (ArcFace template),
y embedde el recorte alineado. Evidencia: evidence/t21.json|t22.json."""
import hashlib, json, os, sys, uuid
from datetime import datetime, timezone

def fail(msg):
    record = {
        "status": "BLOCKED",
        "reason": str(msg),
        "_meta": {
            "ts": datetime.now(timezone.utc).isoformat(),
            "fail_closed": True,
            "command": sys.argv[:],
        },
    }
    try:
        os.makedirs("evidence", exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        path = f"evidence/closure_blocked_{stamp}_{uuid.uuid4().hex[:8]}.json"
        with open(path, "x", encoding="utf-8") as f:
            json.dump(record, f, indent=2, ensure_ascii=False)
        record["_meta"]["evidence_path"] = path
    except Exception as exc:
        record["_meta"]["evidence_write_error"] = str(exc)
    print(json.dumps(record, indent=2, ensure_ascii=False))
    sys.exit(2)

if len(sys.argv) < 4:
    fail("uso: closure_t21_tflite.py REF.jpg TGT.jpg MODELO.tflite [arcface|facenet] [norm|raw|div255] [DETECTOR.tflite]")
ref_path, tgt_path, model_path = sys.argv[1:4]
kind = sys.argv[4] if len(sys.argv) > 4 else "arcface"
norm_mode = sys.argv[5] if len(sys.argv) > 5 else "norm"
det_path = sys.argv[6] if len(sys.argv) > 6 else None
normalize = {"norm": "arcface", "raw": "raw", "div255": "div255"}.get(norm_mode, "arcface")

try:
    from PIL import Image
except ImportError:
    fail("sin Pillow: pkg install python-pillow")

import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from tflite_embedder import TFLiteFaceEmbedder, VectorComparator

if kind not in TFLiteFaceEmbedder.MODEL_SPECS:
    fail(f"tipo de modelo no admitido: {kind}")
if norm_mode not in ("norm", "raw", "div255"):
    fail(f"modo de normalizacion no admitido: {norm_mode}")

model_bytes = open(model_path, "rb").read()
emb = TFLiteFaceEmbedder(kind, model_bytes, normalize=normalize)
if emb._interp is None:
    fail("sin interprete TFLite valido; pkg install python-tflite-runtime")

det = None
det_info = "sin_detector:imagen_completa"
if det_path:
    from face_detector import TFLiteFaceDetector
    from face_align import align_face
    det = TFLiteFaceDetector(open(det_path, "rb").read())
    if det._interp is None:
        fail("detector invalido; verifica el .tflite (BlazeFace short-range)")
    det_info = f"blazeface:alineado_{TFLiteFaceEmbedder.MODEL_SPECS[kind]['input_size'][0]}"

def prep(path):
    try:
        img = Image.open(path).convert("RGB")
    except Exception as exc:
        fail(f"imagen de entrada ilegible ({path}): {exc}")

    if det is None:
        return img

    try:
        r = det.detect(np.asarray(img).tolist())
    except Exception as exc:
        fail(f"error del detector ({path}): {exc}")

    if getattr(r, "status", None) != "PASS" or not getattr(r, "detections", None):
        fail(f"detector sin rostro valido en {path}; no se permite fallback a imagen completa")

    target_size = int(TFLiteFaceEmbedder.MODEL_SPECS[kind]["input_size"][0])
    try:
        aligned = align_face(
            img, r.detections[0].keypoints, out_size=target_size
        )
    except Exception as exc:
        fail(f"fallo de alineacion en {path}: {exc}")

    if aligned is None or getattr(aligned, "size", None) == (0, 0):
        fail(f"alineacion produjo imagen vacia en {path}")

    if aligned.size != (target_size, target_size):
        fail(
            f"tamano de alineacion inesperado en {path}: "
            f"{aligned.size}; esperado {(target_size, target_size)}"
        )
    return aligned

r = emb.embed(np.asarray(prep(ref_path)).tolist())
t = emb.embed(np.asarray(prep(tgt_path)).tolist())
verdict = VectorComparator(threshold=0.79).verify(r, t)

key = "T22" if kind == "facenet" else "T21"
other = "T21" if key == "T22" else "T22"
out = {
    key: {"status": r.status.value, "model_id": r.model_id,
          "evidence_hash": r.evidence_hash,
          "weights_sha256": hashlib.sha256(model_bytes).hexdigest(),
          "pipeline": det_info},
    other: {"status": "BLOCKED",
            "reason": f"correr con modelo {'arcface.tflite' if other == 'T21' else 'facenet.tflite'}"},
    "verification": verdict,
    "_meta": {"ts": datetime.now(timezone.utc).isoformat(), "kind": kind,
              "normalize_mode": normalize, "host": "termux", "fail_closed": True,
              "assurance_level": ("DETECTOR_ALIGNED" if det is not None else "FULL_FRAME_NO_DETECTOR"),
              "ref_sha256": hashlib.sha256(open(ref_path, "rb").read()).hexdigest(),
              "tgt_sha256": hashlib.sha256(open(tgt_path, "rb").read()).hexdigest()},
}
os.makedirs("evidence", exist_ok=True)
stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
path = f"evidence/{key.lower()}_{stamp}_{uuid.uuid4().hex[:8]}.json"
with open(path, "x", encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(json.dumps(out, indent=2, ensure_ascii=False))
print(f"\n[evidence] -> {path}")

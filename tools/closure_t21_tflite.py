#!/usr/bin/env python3
"""Cierre T21/T22 con detector + alineacion (T21-ALIGN).
uso: closure_t21_tflite.py REF TGT MODELO kind norm [DETECTOR.tflite]
Si DETECTOR se da: detecta rostro, alinea a 112x112 (ArcFace template),
y embedde el recorte alineado. Evidencia: evidence/t21.json|t22.json."""
import hashlib, json, os, sys
from datetime import datetime, timezone

def fail(msg):
    print(json.dumps({"status": "BLOCKED", "reason": msg}, ensure_ascii=False))
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
    det_info = "blazeface:alineado_112"

def prep(path):
    img = Image.open(path).convert("RGB")
    if det is not None:
        r = det.detect(np.asarray(img).tolist())
        if r.status == "PASS" and r.detections:
            return align_face(img, r.detections[0].keypoints, out_size=112)
    return img

r = emb.embed(np.asarray(prep(ref_path)).tolist())
t = emb.embed(np.asarray(prep(tgt_path)).tolist())
verdict = VectorComparator(threshold=0.65).verify(r, t)

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
              "ref_sha256": hashlib.sha256(open(ref_path, "rb").read()).hexdigest(),
              "tgt_sha256": hashlib.sha256(open(tgt_path, "rb").read()).hexdigest()},
}
os.makedirs("evidence", exist_ok=True)
path = f"evidence/{key.lower()}.json"
json.dump(out, open(path, "w"), indent=2, ensure_ascii=False)
print(json.dumps(out, indent=2, ensure_ascii=False))
print(f"\n[evidence] -> {path}")

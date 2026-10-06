#!/usr/bin/env python3
"""
Cierre T21/T22 con TFLite en Termux — imagenes REALES.
Uso:
  pkg install -y python-numpy python-pillow
  python tools/closure_t21_tflite.py ref.jpg tgt.jpg modelo.tflite [facenet]
Emite evidence/t21_tflite.json y veredicto para el mapping.
"""
import hashlib, json, os, sys
from datetime import datetime, timezone

def fail(msg):
    print(json.dumps({"status": "BLOCKED", "reason": msg}, ensure_ascii=False))
    sys.exit(2)

if len(sys.argv) < 4:
    fail("uso: closure_t21_tflite.py REF.jpg TGT.jpg MODELO.tflite [arcface|facenet]")

ref_path, tgt_path, model_path = sys.argv[1:4]
kind = sys.argv[4] if len(sys.argv) > 4 else "arcface"
norm_mode = sys.argv[5] if len(sys.argv) > 5 else "norm"
normalize = norm_mode != "raw"

try:
    from PIL import Image
except ImportError:
    fail("sin Pillow: pkg install python-pillow")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from tflite_embedder import TFLiteFaceEmbedder, VectorComparator

model_bytes = open(model_path, "rb").read()
emb = TFLiteFaceEmbedder(kind, model_bytes, normalize=normalize)
if emb._interp is None:
    fail(f"sin interprete TFLite valido ({getattr(emb,'reason','?')}); "
         "instala tflite-runtime o tensorflow-lite")

import numpy as np

def load_pixels(path):
    return np.asarray(Image.open(path).convert("RGB"))

r = emb.embed(load_pixels(ref_path).tolist())
t = emb.embed(load_pixels(tgt_path).tolist())

comp = VectorComparator(threshold=0.65)
verdict = comp.verify(r, t)

out = {
    "T21": {
        "status": r.status.value, "model_id": r.model_id,
        "evidence_hash": r.evidence_hash,
        "weights_sha256": hashlib.sha256(model_bytes).hexdigest(),
    },
    "T22": {"status": "BLOCKED",
            "reason": "mismo pipeline; correr con modelo facenet.tflite"},
    "verification": verdict,
    "_meta": {"ts": datetime.now(timezone.utc).isoformat(),
              "kind": kind, "normalize": normalize, "host": "termux", "fail_closed": True},
}
os.makedirs("evidence", exist_ok=True)
with open("evidence/t21_tflite.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(json.dumps(out, indent=2, ensure_ascii=False))
print("\n[evidence] -> evidence/t21_tflite.json")

#!/usr/bin/env python3
"""Cierre T21/T22 con TFLite en Termux. Evidencia por modelo: t21_arcface.json / t22_facenet.json"""
import hashlib, json, os, sys
from datetime import datetime, timezone

def fail(msg):
    print(json.dumps({"status": "BLOCKED", "reason": msg}, ensure_ascii=False))
    sys.exit(2)

if len(sys.argv) < 4:
    fail("uso: closure_t21_tflite.py REF.jpg TGT.jpg MODELO.tflite [arcface|facenet] [norm|raw|div255]")

ref_path, tgt_path, model_path = sys.argv[1:4]
kind = sys.argv[4] if len(sys.argv) > 4 else "arcface"
norm_mode = sys.argv[5] if len(sys.argv) > 5 else "norm"
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
    fail(f"sin interprete TFLite valido; instala tflite-runtime")

r = emb.embed(np.asarray(Image.open(ref_path).convert("RGB")).tolist())
t = emb.embed(np.asarray(Image.open(tgt_path).convert("RGB")).tolist())
verdict = VectorComparator(threshold=0.65).verify(r, t)

key = "T22" if kind == "facenet" else "T21"
other = "T21" if key == "T22" else "T22"
out = {
    key: {"status": r.status.value, "model_id": r.model_id,
          "evidence_hash": r.evidence_hash,
          "weights_sha256": hashlib.sha256(model_bytes).hexdigest()},
    other: {"status": "BLOCKED",
            "reason": f"correr este closure con modelo {'arcface.tflite' if other == 'T21' else 'facenet.tflite'}"},
    "verification": verdict,
    "_meta": {"ts": datetime.now(timezone.utc).isoformat(), "kind": kind,
              "normalize_mode": normalize, "host": "termux", "fail_closed": True},
}
os.makedirs("evidence", exist_ok=True)
path = f"evidence/{key.lower()}.json"
json.dump(out, open(path, "w"), indent=2, ensure_ascii=False)
print(json.dumps(out, indent=2, ensure_ascii=False))
print(f"\n[evidence] -> {path}")

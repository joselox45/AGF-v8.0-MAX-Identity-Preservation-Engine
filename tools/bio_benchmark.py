#!/usr/bin/env python3
"""
AGF T30 — Mini-benchmark de robustez biométrica.
Uso: benchmark --spec pares.json --embedder facenet.tflite [--detector blaze.tflite]
Spec: [{"a": "/ruta.jpg", "b": "/ruta2.jpg", "same": true}, ...]
Métricas: TAR (mismo, aceptado), FAR (distinto, aceptado por error) @ umbral.
Sin modelos -> BLOCKED honesto (fail-closed).
"""
import argparse, json, os, sys
from datetime import datetime, timezone

ap = argparse.ArgumentParser()
ap.add_argument("--spec", required=True)
ap.add_argument("--embedder", required=True)
ap.add_argument("--detector", default=None)
ap.add_argument("--kind", default="facenet")
ap.add_argument("--norm", default="raw", choices=["raw", "norm", "div255"])
ap.add_argument("--threshold", type=float, default=0.65)
a = ap.parse_args()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from PIL import Image
from tflite_embedder import TFLiteFaceEmbedder, VectorComparator

emb = TFLiteFaceEmbedder(a.kind, open(a.embedder, "rb").read(),
                         normalize={"raw":"raw","norm":"arcface","div255":"div255"}[a.norm])
if emb._interp is None:
    print(json.dumps({"status": "BLOCKED",
                      "reason": "sin embedder valido; fail-closed"})); sys.exit(2)

det = None
if a.detector:
    from face_detector import TFLiteFaceDetector
    det = TFLiteFaceDetector(open(a.detector, "rb").read())

def crop_face(path):
    px = np.asarray(Image.open(path).convert("RGB"))
    if det is not None and det._interp is not None:
        r = det.detect(px.tolist())
        if r.status == "PASS" and r.detections:
            d = r.detections[0]
            return px[d.y1:d.y2, d.x1:d.x2]
    return px  # sin detector: imagen completa (resultado menos robusto)

comp = VectorComparator(threshold=a.threshold)
spec = json.load(open(a.spec))
same_scores, diff_scores = [], []
for pair in spec:
    va = emb.embed(crop_face(pair["a"]).tolist())
    vb = emb.embed(crop_face(pair["b"]).tolist())
    if va.status.value != "PASS" or vb.status.value != "PASS":
        continue
    cos = comp.cosine(va.vector, vb.vector)
    (same_scores if pair["same"] else diff_scores).append(cos)

def rate(scores, cond):
    return round(sum(1 for s in scores if cond(s)) / len(scores), 4) if scores else None

out = {
    "status": "PASS",
    "n_pairs": len(spec),
    "threshold": a.threshold,
    "TAR_same_accepted": rate(same_scores, lambda s: s >= a.threshold),
    "FAR_diff_accepted": rate(diff_scores, lambda s: s >= a.threshold),
    "cos_same_min": round(min(same_scores), 4) if same_scores else None,
    "cos_diff_max": round(max(diff_scores), 4) if diff_scores else None,
    "note": "FAR>0 implica umbral insuficiente o detector ausente",
    "_meta": {"ts": datetime.now(timezone.utc).isoformat(), "host": "termux"},
}
print(json.dumps(out, indent=2, ensure_ascii=False))
os.makedirs("evidence", exist_ok=True)
json.dump(out, open("evidence/benchmark_t30.json", "w"), indent=2)
print("[evidence] -> evidence/benchmark_t30.json")

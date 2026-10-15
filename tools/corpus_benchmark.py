#!/usr/bin/env python3
"""
AGF Corpus Benchmark — TAR/FAR + IC 95% (Wilson) sobre el corpus.
Pares: (base, variante) mismo id -> same=True; (base_i, base_j) i!=j -> same=False.
"""
import argparse, hashlib, json, math, os, sys
from datetime import datetime, timezone

ap = argparse.ArgumentParser()
ap.add_argument("--corpus", default="data/corpus_v1")
ap.add_argument("--embedder", required=True)
ap.add_argument("--detector", default=None)
ap.add_argument("--kind", default="facenet")
ap.add_argument("--norm", default="raw")
ap.add_argument("--threshold", type=float, default=0.65)
a = ap.parse_args()

import numpy as np
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from tflite_embedder import TFLiteFaceEmbedder, VectorComparator

emb = TFLiteFaceEmbedder(a.kind, open(a.embedder, "rb").read(),
                         normalize={"raw": "raw", "norm": "arcface", "div255": "div255"}[a.norm])
if emb._interp is None:
    sys.exit(json.dumps({"status": "BLOCKED", "reason": "sin embedder"}))

det = None
if a.detector:
    from face_detector import TFLiteFaceDetector
    from face_align import align_face
    det = TFLiteFaceDetector(open(a.detector, "rb").read())
    if det._interp is None:
        sys.exit(json.dumps({"status": "BLOCKED", "reason": "detector invalido"}))

def embed(p):
    img = Image.open(p).convert("RGB")
    if det is not None:
        r = det.detect(np.asarray(img).tolist())
        if r.status == "PASS" and r.detections:
            img = align_face(img, r.detections[0].keypoints, 112)
    e = emb.embed(np.asarray(img).tolist())
    return e.vector if e.status.value == "PASS" else None

def wilson(k, n, z=1.96):
    if n == 0:
        return (None, None)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (round(max(0, c - m), 4), round(min(1, c + m), 4))

ids = sorted(d for d in os.listdir(a.corpus) if d.startswith("id_"))
comp = VectorComparator(threshold=a.threshold)
same_scores, diff_scores = [], []
for i in ids:
    b = embed(os.path.join(a.corpus, i, "base.png"))
    if b is None:
        continue
    for v in ("dano", "pose", "luz", "oclusion"):
        vv = embed(os.path.join(a.corpus, i, f"{v}.png"))
        if vv is not None:
            same_scores.append(comp.cosine(b, vv))
for x in range(0, len(ids), 3):                       # pares cruzados espaciados
    for y in range(x + 1, min(x + 3, len(ids))):
        bx = embed(os.path.join(a.corpus, ids[x], "base.png"))
        by = embed(os.path.join(a.corpus, ids[y], "base.png"))
        if bx is not None and by is not None:
            diff_scores.append(comp.cosine(bx, by))

tar = sum(1 for s in same_scores if s >= a.threshold)
far = sum(1 for s in diff_scores if s >= a.threshold)
out = {"status": "PASS", "threshold": a.threshold,
       "n_same": len(same_scores), "n_diff": len(diff_scores),
       "TAR": round(tar / len(same_scores), 4) if same_scores else None,
       "FAR": round(far / len(diff_scores), 4) if diff_scores else None,
       "TAR_IC95_wilson": wilson(tar, len(same_scores)),
       "FAR_IC95_wilson": wilson(far, len(diff_scores)),
       "cos_same_mean": round(sum(same_scores) / len(same_scores), 4) if same_scores else None,
       "cos_diff_max": round(max(diff_scores), 4) if diff_scores else None,
       "nota": ("corpus procedural => valida PIPELINE. Para claims biometricos,"
                " regenerar con --stylegan. IC95 = Wilson score interval."),
       "_meta": {"ts": datetime.now(timezone.utc).isoformat(), "host": "termux"}}
os.makedirs("evidence", exist_ok=True)
path = "evidence/benchmark_corpus.json"
json.dump(out, open(path, "w"), indent=2, ensure_ascii=False)
print(json.dumps(out, indent=2, ensure_ascii=False))
print(f"\n[evidence] -> {path}")

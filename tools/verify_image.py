#!/usr/bin/env python3
"""
AGF — verificacion de imagen en capas (reproducible).
Uso:
  python tools/verify_image.py REF.jpg CANDIDATE.jpg EMBEDDER.tflite \
      [facenet|arcface] [raw|norm|div255] [DETECTOR.tflite] \
      [--provenance-declared] [--cross-tested]

Emite evidence/verify_<ts>.json con L1/L2/L3 separados.
L1 formal se evalua sobre la evidencia del closure (hashes, pipeline).
"""
import argparse, hashlib, json, os, sys
from datetime import datetime, timezone

ap = argparse.ArgumentParser()
ap.add_argument("ref"); ap.add_argument("candidate")
ap.add_argument("embedder"); ap.add_argument("kind", nargs="?", default="facenet")
ap.add_argument("norm", nargs="?", default="raw")
ap.add_argument("detector", nargs="?", default=None)
ap.add_argument("--provenance-declared", action="store_true")
ap.add_argument("--cross-tested", action="store_true")
a = ap.parse_args()

import numpy as np
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from tflite_embedder import TFLiteFaceEmbedder, VectorComparator
from verdict_layers import VerdictLayers

norm = {"raw": "raw", "norm": "arcface", "div255": "div255"}[a.norm]
emb = TFLiteFaceEmbedder(a.kind, open(a.embedder, "rb").read(), normalize=norm)
if emb._interp is None:
    sys.exit(json.dumps({"status": "BLOCKED", "layer": "L2",
                         "reason": "sin interprete TFLite"}))

det = None
if a.detector:
    from face_detector import TFLiteFaceDetector
    from face_align import align_face
    det = TFLiteFaceDetector(open(a.detector, "rb").read())
    if det._interp is None:
        sys.exit(json.dumps({"status": "BLOCKED", "layer": "L2",
                             "reason": "detector invalido"}))

def prep(p):
    img = Image.open(p).convert("RGB")
    if det is not None:
        r = det.detect(np.asarray(img).tolist())
        if r.status == "PASS" and r.detections:
            return np.asarray(align_face(img, r.detections[0].keypoints, 112))
    return np.asarray(img)

r = emb.embed(prep(a.ref).tolist())
c = emb.embed(prep(a.candidate).tolist())
comp = VectorComparator(threshold=0.65)
v = comp.verify(r, c)

# L1 formal: evidencia presente + hashes de pesos verificables
w_bytes = open(a.embedder, "rb").read()
L1 = "PASS" if (r.evidence_hash and c.evidence_hash
                and v.get("evidence_hash")) else "BLOCKED"

anti_replay = v["status"] != "FAIL" or "replay" not in v.get("reason", "")
vl = VerdictLayers().evaluate(
    formal_status=L1,
    biometric_status=v["status"] if v["status"] in ("PASS", "FAIL") else "BLOCKED",
    cosine=v.get("cosine"), threshold=0.65,
    provenance_declared=a.provenance_declared,
    cross_person_tested=a.cross_tested,
    anti_replay_clean=anti_replay)

out = {"verdict": vl.to_dict(),
       "inputs": {"ref_sha256": hashlib.sha256(open(a.ref, "rb").read()).hexdigest(),
                  "candidate_sha256": hashlib.sha256(open(a.candidate, "rb").read()).hexdigest(),
                  "weights_sha256": hashlib.sha256(w_bytes).hexdigest(),
                  "model_id": r.model_id, "pipeline": "aligned" if det else "full_image"},
       "_meta": {"ts": datetime.now(timezone.utc).isoformat(), "host": "termux"}}
os.makedirs("evidence", exist_ok=True)
path = "evidence/verify_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + ".json"
json.dump(out, open(path, "w"), indent=2, ensure_ascii=False)
print(json.dumps(out, indent=2, ensure_ascii=False))
print(f"\n[evidence] -> {path}")

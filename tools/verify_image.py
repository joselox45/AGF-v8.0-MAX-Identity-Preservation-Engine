#!/usr/bin/env python3
"""
AGF — verificacion de imagen en capas (reproducible).
Uso:
  python tools/verify_image.py REF.jpg CANDIDATE.jpg EMBEDDER.tflite \
      [facenet|arcface] [raw|norm|div255] [DETECTOR.tflite] \
      [--provenance-declared] [--cross-tested] \
      [--subject-label same|diff|unknown] [--prompt-sha256 HASH]
Stability: detector select='largest' + mediana de N=3 embeddings (AGF_EMB_RUNS).
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
ap.add_argument("--subject-label", default=None,
                help="same|diff|unknown — etiqueta del par (auditoria 10)")
ap.add_argument("--prompt-sha256", default=None,
                help="hash del kernel/pegar usado en la corrida")
a = ap.parse_args()

import numpy as np
from PIL import Image
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from tflite_embedder import TFLiteFaceEmbedder, VectorComparator, EmbeddingStatus
from verdict_layers import VerdictLayers

norm = {"raw": "raw", "norm": "arcface", "div255": "div255"}[a.norm]
emb = TFLiteFaceEmbedder(a.kind, open(a.embedder, "rb").read(),
                         normalize=norm, threads=1)
if emb._interp is None:
    sys.exit(json.dumps({"status": "BLOCKED", "layer": "L2",
                         "reason": "sin interprete TFLite"}))

det = None
if a.detector:
    from face_detector import TFLiteFaceDetector
    from face_align import align_face
    det = TFLiteFaceDetector(open(a.detector, "rb").read(), select="largest")
    if det._interp is None:
        sys.exit(json.dumps({"status": "BLOCKED", "layer": "L2",
                             "reason": "detector invalido"}))

EMB_RUNS = int(os.environ.get("AGF_EMB_RUNS", "3"))

# H4 (2026-10-18): alinear al input_size del modelo (FaceNet 160 / ArcFace 112)
ALIGN = int(os.environ.get("AGF_ALIGN", "160"))  # 112=linea base v1; 160=nuevo. La calibracion corpus_v2 decide con datos.

def embed_stable(pixels):
    # Mediana de N=3 embeddings por imagen: suprime varianza del runtime.
    vecs = []
    for _ in range(EMB_RUNS):
        e = emb.embed(pixels)
        if e.status.value == "PASS" and e.vector:
            vecs.append(e.vector)
    if not vecs:
        return None
    if len(vecs) == 1:
        return vecs[0]
    return [sorted(v[i] for v in vecs)[len(vecs) // 2]
            for i in range(len(vecs[0]))]

def prep(path):
    # H3 (2026-10-18): FAIL-CLOSED - sin cara detectada NO hay fallback a
    # imagen completa (contaminaba embeddings). Devuelve None -> BLOCKED.
    img = Image.open(path).convert("RGB")
    if det is None:
        return np.asarray(img)
    r = det.detect(np.asarray(img).tolist())
    if r.status == "PASS" and r.detections:
        return np.asarray(align_face(img, r.detections[0].keypoints, ALIGN))
    return None

_pref, _pcand = prep(a.ref), prep(a.candidate)
if _pref is None or _pcand is None:
    sys.exit(json.dumps({"status": "BLOCKED", "layer": "L1",
                         "reason": "sin cara detectada; fail-closed: sin fallback a imagen completa"}))
vr = embed_stable(_pref.tolist())
vc = embed_stable(_pcand.tolist())
if vr is None or vc is None:
    sys.exit(json.dumps({"status": "BLOCKED", "layer": "L2",
                         "reason": "embedding no disponible (N=" + str(EMB_RUNS) + ")"}))
class _R: pass
_r, _c = _R(), _R()
_r.status = EmbeddingStatus.PASS; _r.vector = vr
_r.model_id = emb.model_id; _r.reason = "stable-median"
_c.status = EmbeddingStatus.PASS; _c.vector = vc; _c.model_id = emb.model_id; _c.reason = "stable-median"
comp = VectorComparator(threshold=0.79)
v = comp.verify(_r, _c)

L1 = "PASS" if v.get("evidence_hash") else "BLOCKED"
anti_replay = v["status"] != "FAIL" or "REQUIRES_REVIEW" not in v.get("reason", "")
vl = VerdictLayers().evaluate(
    formal_status=L1,
    biometric_status=v["status"] if v["status"] in ("PASS", "FAIL") else "BLOCKED",
    cosine=v.get("cosine"), threshold=0.65,
    provenance_declared=a.provenance_declared,
    cross_person_tested=a.cross_tested,
    anti_replay_clean=anti_replay)

out = {"verdict": vl.to_dict(),
       "inputs": {"subject_label": a.subject_label or "unknown",
                  "prompt_sha256": a.prompt_sha256,
                  "ref_sha256": hashlib.sha256(open(a.ref, "rb").read()).hexdigest(),
                  "candidate_sha256": hashlib.sha256(open(a.candidate, "rb").read()).hexdigest(),
                  "weights_sha256": hashlib.sha256(open(a.embedder, "rb").read()).hexdigest(),
                  "model_id": emb.model_id,
                  "pipeline": "aligned:stable-median-N" + str(EMB_RUNS)},
       "_meta": {"ts": datetime.now(timezone.utc).isoformat(), "host": "termux"}}
os.makedirs("evidence", exist_ok=True)
path = "evidence/verify_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + ".json"
json.dump(out, open(path, "w"), indent=2, ensure_ascii=False)
print(json.dumps(out, indent=2, ensure_ascii=False))
print(f"\n[evidence] -> {path}")

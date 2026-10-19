#!/usr/bin/env python3
"""
AGF — Calibracion empirica del umbral (cierre del gap ERRATA §3).
Mide TAR/FAR con IC 95% (Wilson) sobre corpus_v1 y deriva el umbral
por Youden J y por EER. Comparacion explicita contra el umbral actual 0.65.

LIMITACION DECLARADA: corpus_v1 es procedural-parametrico (manifest:
"pipeline-validation ONLY"). Estos numeros validan el PIPELINE y derivan
el umbral por primera vez; NO son TAR/FAR de mundo real. El corpus
fotorealista es roadmap item 5.

Uso (Termux):
  python tools/calibrate_threshold.py EMBEDDER.tflite [facenet|arcface] \
      [raw|norm|div255] [DETECTOR.tflite] [--out RUTA.json] [--vault]

Fail-closed: sin pesos/sin interprete -> BLOCKED, nunca PASS fabricado.
"""
import argparse, hashlib, json, math, os, sys
from datetime import datetime, timezone

ap = argparse.ArgumentParser()
ap.add_argument("embedder"); ap.add_argument("kind", nargs="?", default="facenet")
ap.add_argument("norm", nargs="?", default="raw")
ap.add_argument("detector", nargs="?", default=None)
ap.add_argument("--out", default=None)
ap.add_argument("--vault", action="store_true", help="anclar resultado al vault")
ap.add_argument("--corpus", default="v1", choices=["v1","v2"])
def get_args():
    return ap.parse_args()

REPO = os.path.join(os.path.dirname(__file__), "..")
CORPUS = os.path.join(REPO, "data", "corpus_v1")
VARIANTS = ["luz", "oclusion", "pose", "dano"]  # genuinas: base vs variante


def sha256_file(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def cosine(u, v):
    dot = sum(x * y for x, y in zip(u, v))
    nu = math.sqrt(sum(x * x for x in u))
    nv = math.sqrt(sum(x * x for x in v))
    if nu == 0 or nv == 0:
        return None
    return dot / (nu * nv)


def wilson_ci(k, n, z=1.959964):
    """IC 95% Wilson para proporcion k/n (robusto en n pequeno)."""
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    m = (z / d) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (round(c - m, 4), round(c + m, 4))


def sweep(genuine, impostor, lo=0.30, hi=0.95, step=0.01):
    """TAR/FAR por umbral + seleccion Youden J y EER."""
    rows, best_y, eer = [], None, None
    th = lo
    while th <= hi + 1e-9:
        tar = sum(1 for s in genuine if s >= th) / len(genuine)
        far = sum(1 for s in impostor if s >= th) / len(impostor)
        rows.append({"threshold": round(th, 4), "TAR": round(tar, 4), "FAR": round(far, 4)})
        j = tar - far
        if best_y is None or j > best_y["J"]:
            best_y = {"threshold": round(th, 4), "J": round(j, 4),
                      "TAR": round(tar, 4), "FAR": round(far, 4)}
        if eer is None or abs(far - (1 - tar)) < eer["dist"]:
            eer = {"threshold": round(th, 4), "TAR": round(tar, 4),
                   "FAR": round(far, 4), "dist": round(abs(far - (1 - tar)), 4)}
        th += step
    return rows, best_y, eer


def at_threshold(rows, t):
    for r in rows:
        if abs(r["threshold"] - t) < 1e-9:
            return r
    return None


def main(a):
    import numpy as np
    from PIL import Image
    sys.path.insert(0, os.path.join(REPO, "src"))
    from tflite_embedder import TFLiteFaceEmbedder
    from face_detector import TFLiteFaceDetector
    from face_align import align_face

    norm = {"raw": "raw", "norm": "arcface", "div255": "div255"}[a.norm]
    emb = TFLiteFaceEmbedder(a.kind, open(a.embedder, "rb").read(),
                             normalize=norm, threads=1)
    if emb._interp is None:
        out = {"status": "BLOCKED", "layer": "L2",
               "reason": "sin interprete TFLite o pesos invalidos; fail-closed"}
        print(json.dumps(out)); sys.exit(2)
    det = None
    if a.detector:
        det = TFLiteFaceDetector(open(a.detector, "rb").read(), select="largest")
        if det._interp is None:
            out = {"status": "BLOCKED", "layer": "L2", "reason": "detector invalido"}
            print(json.dumps(out)); sys.exit(2)

    EMB_RUNS = int(os.environ.get("AGF_EMB_RUNS", "3"))

    def embed_stable(pixels):
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
        img = Image.open(path).convert("RGB")
        if det is not None:
            r = det.detect(np.asarray(img).tolist())
            if r.status == "PASS" and r.detections:
                return np.asarray(align_face(img, r.detections[0].keypoints, int(os.environ.get("AGF_ALIGN", "160"))))
        return np.asarray(img)

    corpus_dir = os.path.join(REPO, "data", f"corpus_{a.corpus}")
    man = json.load(open(os.path.join(corpus_dir, "manifest.json")))
    ids = sorted({k.split("/")[0] for k in man["files"]})

    # custodia: verificamos sha256 de cada imagen contra el manifest
    custody_fail = []
    for rel, meta in man["files"].items():
        p = os.path.join(corpus_dir, rel)
        if not os.path.exists(p) or sha256_file(p) != meta["sha256"]:
            custody_fail.append(rel)

    cache = {}
    def emb_of(rel):
        if rel not in cache:
            v = embed_stable(prep(os.path.join(corpus_dir, rel)).tolist())
            if v is None:
                out = {"status": "BLOCKED", "layer": "L2",
                       "reason": f"embedding fallo para {rel} (N={EMB_RUNS})"}
                print(json.dumps(out)); sys.exit(3)
            cache[rel] = v
        return cache[rel]

    genuine_scores, impostor_scores = [], []
    pairs = []
    for i in ids:
        vb = emb_of(f"{i}/base.png")
        for var in VARIANTS:
            rel = f"{i}/{var}.png"
            if rel not in man["files"]:
                continue
            s = cosine(vb, emb_of(rel))
            genuine_scores.append(s)
            pairs.append({"pair": f"{i}/base vs {i}/{var}", "label": "genuine", "cosine": round(s, 6)})
    for x in range(len(ids)):
        for y in range(x + 1, len(ids)):
            s = cosine(emb_of(f"{ids[x]}/base.png"), emb_of(f"{ids[y]}/base.png"))
            impostor_scores.append(s)
            pairs.append({"pair": f"{ids[x]}/base vs {ids[y]}/base", "label": "impostor", "cosine": round(s, 6)})

    rows, best_y, eer = sweep(genuine_scores, impostor_scores)
    cur = at_threshold(rows, 0.65) or {}
    ng, ni = len(genuine_scores), len(impostor_scores)

    def metric_at(r):
        if not r:
            return None
        kg = round(r["TAR"] * ng); ki = round(r["FAR"] * ni)
        return {**r, "n_genuine": ng, "n_impostor": ni,
                "TAR_ci95": wilson_ci(kg, ng), "FAR_ci95": wilson_ci(ki, ni)}

    summary = {
        "corpus": {"name": man["corpus"], "n_ids": len(ids),
                   "modelo_base": man.get("modelo_base", "fotorealista-multi-generador"),
                   "limitacion": "procedural-parametrico: pipeline-validation ONLY, no fotorealista",
                   "custodia_sha256": "VERIFIED" if not custody_fail else f"FALLA: {custody_fail}"},
        "modelo": {"embedder": emb.model_id, "kind": a.kind, "normalize": a.norm,
                   "detector_sha256": sha256_file(a.detector) if a.detector else None,
                   "emb_runs_mediana": EMB_RUNS, "threads": 1},
        "n_genuine": ng, "n_impostor": ni,
        "umbral_actual_0.65": metric_at(cur),
        "umbral_youden": metric_at(best_y),
        "umbral_eer": metric_at(eer),
        "recomendacion": None,
    }
    rec = best_y if best_y and best_y["J"] > 0 else eer
    summary["recomendacion"] = {
        "threshold": rec["threshold"],
        "criterio": "youden_j" if rec is best_y else "eer",
        "NOTA": "valido solo para este corpus; recalibrar con corpus fotorealista (roadmap #5)"}

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = a.out or os.path.join(REPO, "evidence", f"calibration_{man['corpus']}_{ts}.json")
    out = {"status": "PASS", "tipo": "CALIBRACION_UMBRAL", "created_utc": ts,
           "summary": summary, "scores": pairs}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(json.dumps({"status": "PASS", "out": out_path,
                      "umbral_actual_0.65": summary["umbral_actual_0.65"],
                      "umbral_youden": summary["umbral_youden"],
                      "umbral_eer": summary["umbral_eer"],
                      "recomendacion": summary["recomendacion"]}, ensure_ascii=False, indent=2))
    if a.vault:
        sys.path.insert(0, os.path.join(REPO, "src"))
        from evidence_vault import EvidenceVault
        v = EvidenceVault(os.environ.get("AGF_VAULT", os.path.join(REPO, "evidence", "vault_v2.jsonl")))
        rec_ = v.append(out_path, subject_label="calibration")
        print(json.dumps({"vault": "anchored", "seq": rec_.seq, "head": rec_.head}))


if __name__ == "__main__":
    main(get_args())

import copy
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

import face_detector as fdmod
from blazeface_decoder import decode, nms, weighted_nms

ROOT = Path.cwd()
MODEL = ROOT / "blaze_face_short_range.tflite"
CORPUS = ROOT / "data" / "corpus_v1"
THRESHOLD = 0.7
IOU_THRESHOLD = 0.3
SIZE = fdmod.TFLiteFaceDetector.INPUT_SIZE


def box_iou(a, b):
    y1, x1 = max(a[0], b[0]), max(a[1], b[1])
    y2, x2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0.0, y2-y1) * max(0.0, x2-x1)
    aa = max(0.0, a[2]-a[0]) * max(0.0, a[3]-a[1])
    ab = max(0.0, b[2]-b[0]) * max(0.0, b[3]-b[1])
    union = aa + ab - inter
    return inter / union if union > 0 else 0.0


def pack(dets):
    return [
        {"score": float(d.score), "box": [float(v) for v in d.box]}
        for d in dets
    ]


def main():
    if not MODEL.is_file():
        raise FileNotFoundError(f"Falta el modelo: {MODEL}")
    if not CORPUS.is_dir():
        raise FileNotFoundError(f"Falta el corpus: {CORPUS}")

    paths = sorted(CORPUS.glob("id_*/base.png"))
    if not paths:
        raise RuntimeError("No se encontraron imágenes id_*/base.png")

    detector = fdmod.TFLiteFaceDetector(
        model_bytes=MODEL.read_bytes(), select="score"
    )
    if detector._interp is None:
        raise RuntimeError(
            "No se pudo cargar el intérprete TFLite; "
            "revisa que tflite_runtime o TensorFlow estén instalados."
        )

    rows = []
    for i, path in enumerate(paths, 1):
        arr = np.asarray(Image.open(path).convert("RGB"))
        arr = np.clip(arr.astype(np.float32), 0, 255).astype(np.uint8)
        orig_h, orig_w = arr.shape[:2]

        # Mismo letterbox y normalización que face_detector.py
        scale = SIZE / float(max(orig_w, orig_h))
        nw = max(1, int(round(orig_w * scale)))
        nh = max(1, int(round(orig_h * scale)))
        resized = np.asarray(
            Image.fromarray(arr).resize((nw, nh), Image.BILINEAR),
            dtype=np.float32,
        )
        pad_x = (SIZE - nw) // 2
        pad_y = (SIZE - nh) // 2
        canvas = np.zeros((SIZE, SIZE, 3), dtype=np.float32)
        canvas[pad_y:pad_y+nh, pad_x:pad_x+nw] = resized
        inp = canvas / 127.5 - 1.0

        # Una inferencia compartida por ambos algoritmos
        detector._interp.set_tensor(
            detector._in_idx, np.expand_dims(inp, 0)
        )
        detector._interp.invoke()
        reg = detector._interp.get_tensor(
            detector._reg_idx
        ).reshape(896, 16)
        cls = detector._interp.get_tensor(
            detector._cls_idx
        ).reshape(896, 1)

        candidates = decode(
            reg, cls, detector.anchors,
            input_size=SIZE, score_thresh=THRESHOLD
        )

        # Copias independientes para evitar contaminación entre métodos
        greedy = nms(copy.deepcopy(candidates), iou_thresh=IOU_THRESHOLD)
        weighted = weighted_nms(
            copy.deepcopy(candidates), iou_thresh=IOU_THRESHOLD
        )

        gtop = max(greedy, key=lambda d: d.score) if greedy else None
        wtop = max(weighted, key=lambda d: d.score) if weighted else None
        overlap = (
            box_iou(gtop.box, wtop.box)
            if gtop is not None and wtop is not None else None
        )

        rows.append({
            "image": str(path.relative_to(ROOT)),
            "candidate_count": len(candidates),
            "greedy_count": len(greedy),
            "weighted_count": len(weighted),
            "greedy_top_score": float(gtop.score) if gtop else None,
            "weighted_top_score": float(wtop.score) if wtop else None,
            "top_box_iou": overlap,
            "greedy": pack(greedy),
            "weighted": pack(weighted),
        })
        print(
            f"[{i}/{len(paths)}] {path.parent.name}: "
            f"candidatos={len(candidates)}, "
            f"greedy={len(greedy)}, weighted={len(weighted)}, "
            f"IoU_top={overlap if overlap is not None else 'N/A'}"
        )

    comparable = [
        r["top_box_iou"] for r in rows
        if r["top_box_iou"] is not None
    ]
    summary = {
        "images": len(rows),
        "images_with_greedy_detection": sum(
            r["greedy_count"] > 0 for r in rows
        ),
        "images_with_weighted_detection": sum(
            r["weighted_count"] > 0 for r in rows
        ),
        "total_candidates": sum(r["candidate_count"] for r in rows),
        "total_greedy_detections": sum(r["greedy_count"] for r in rows),
        "total_weighted_detections": sum(
            r["weighted_count"] for r in rows
        ),
        "mean_top_box_iou": (
            sum(comparable) / len(comparable) if comparable else None
        ),
    }
    report = {
        "experiment": "greedy_vs_weighted_nms",
        "model": MODEL.name,
        "corpus": str(CORPUS.relative_to(ROOT)),
        "score_threshold": THRESHOLD,
        "iou_threshold": IOU_THRESHOLD,
        "anchors": len(detector.anchors),
        "summary": summary,
        "results": rows,
        "note": (
            "Corpus procedural: compara postprocesamiento, no demuestra "
            "precisión en rostros reales ni equivalencia exacta con MediaPipe."
        ),
    }

    print("\n=== RESUMEN A/B ===")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print("Anchors:", len(detector.anchors))

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = ROOT / f"nms_ab_corpus_v1_{stamp}.json"
    try:
        output.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print("Informe guardado:", output)
    except OSError as exc:
        print("No se pudo guardar el JSON:", exc)


if __name__ == "__main__":
    main()

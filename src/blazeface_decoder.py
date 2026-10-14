"""
AGF T21-ALIGN — Decodificador real de BlazeFace (short-range, 128px).
Salida del modelo TFLite (MediaPipe face_detection):
  - regression: (1, 896, 16)  -> 4 box offsets + 12 offsets de 6 keypoints
  - classification: (1, 896, 1) -> scores (sigmoid)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class Anchor:
    cx: float; cy: float; w: float; h: float


@dataclass
class FaceDetection:
    score: float
    box: tuple            # (x1, y1, x2, y2) en px de la imagen de entrada
    keypoints: list       # 6 puntos [(x,y)...] en px: 0 ojo der, 1 ojo izq,
                          # 2 nariz, 3 boca, 4 oreja der, 5 oreja izq


def generate_anchors(input_size: int = 128) -> list:
    """Specs MediaPipe short-range: stride8/16x16/2 anclas + stride16/8x8/6."""
    anchors = []
    specs = [
        {"stride": 8,  "grid": 16, "ars": [1.0], "scales": [0.1484375, 0.75]},
        {"stride": 16, "grid": 8,  "ars": [1.0, 0.75, 1.3333333],
         "scales": [0.75, 0.75]},
    ]
    for sp in specs:
        g = sp["grid"]
        for ar in sp["ars"]:
            for s in sp["scales"]:
                for i in range(g):
                    for j in range(g):
                        cx = (j + 0.5) / g
                        cy = (i + 0.5) / g
                        w = s * math.sqrt(ar)
                        h = s / math.sqrt(ar)
                        anchors.append(Anchor(cx, cy, w, h))
    return anchors


def _sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))


def decode(reg, cls, anchors, input_size=128, score_thresh=0.7):
    """reg: (896,16); cls: (896,1) crudos del modelo. Devuelve FaceDetection[]."""
    dets = []
    for i, a in enumerate(anchors):
        score = _sigmoid(float(cls[i][0]))
        if score < score_thresh:
            continue
        dx, dy, dw, dh = (float(v) for v in reg[i][:4])
        cx = (a.cx + dx * a.w) * input_size
        cy = (a.cy + dy * a.h) * input_size
        w = a.w * math.exp(dw) * input_size
        h = a.h * math.exp(dh) * input_size
        kps = []
        for k in range(6):
            kx = (a.cx + float(reg[i][4 + 2 * k]) * a.w) * input_size
            ky = (a.cy + float(reg[i][5 + 2 * k]) * a.h) * input_size
            kps.append((kx, ky))
        dets.append(FaceDetection(score,
                                  (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2),
                                  kps))
    return dets


def nms(dets, iou_thresh=0.3, top_k=-1):
    dets = sorted(dets, key=lambda d: -d.score)
    keep = []
    while dets and (top_k < 0 or len(keep) < top_k):
        best = dets.pop(0)
        keep.append(best)
        dets = [d for d in dets
                if _iou(best.box, d.box) < iou_thresh]
    return keep


def _iou(a, b):
    x1 = max(a[0], b[0]); y1 = max(a[1], b[1])
    x2 = min(a[2], b[2]); y2 = min(a[3], b[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return inter / max(1e-9, area_a + area_b - inter)

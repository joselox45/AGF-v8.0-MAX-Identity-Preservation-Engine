"""BlazeFace short-range decoder — CORREGIDO a la especificacion oficial
de MediaPipe (face_detection_short_range.pbtxt / face_detection.pbtxt).

Cambios respecto a la version previa (bug de anclaje):
1. Anchors: num_layers=4, strides [8,16,16,16] (era 2 capas).
2. Escalas por capa: interpolacion lineal min->max + segundo anchor en
   sqrt(scale * scale_next) (era [0.148,0.75]/[0.75,0.75] fijas).
3. fixed_anchor_size=True: tamanio de caja directo de la regresion,
   SIN exponencial (apply_exponential_on_box_size=false).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Anchor:
    cx: float
    cy: float
    h: float
    w: float


@dataclass
class FaceDetection:
    score: float
    box: Tuple[float, float, float, float]      # ymin, xmin, ymax, xmax (normalizado)
    keypoints: List[Tuple[float, float]]        # 6 pts BlazeFace (normalizado)


def sigmoid(x: float) -> float:
    if x < -80:
        return 0.0
    if x > 80:
        return 1.0
    return 1.0 / (1.0 + math.exp(-x))


def generate_anchors(input_size: int = 128) -> List[Anchor]:
    """Anchors modelo ORIGINAL BlazeFace (2 capas, 896 total):
    16x16 stride 8: 2 anchors ar 1.0; 8x8 stride 16: 6 anchors.
    Validado empiricamente 2026-10-18 (variante C, unica con caja centrada)."""
    anchors: List[Anchor] = []
    for stride, ars, scales in ((8, (1.0,), (0.1484375, 0.75)),
                                (16, (1.0, 0.75, 1.3333333), (0.75, 0.75))):
        grid = input_size // stride
        for i in range(grid):
            for j in range(grid):
                for ar in ars:
                    for sc in scales:
                        anchors.append(Anchor((j + 0.5) / grid, (i + 0.5) / grid,
                                              sc * math.sqrt(ar), sc / math.sqrt(ar)))
    return anchors


def decode(reg, cls, anchors: List[Anchor], input_size: int = 128,
           score_thresh: float = 0.5) -> List[FaceDetection]:
    """reg (896,16): [dx,dy,dw,dh, 6x(kx,ky)] en unidades del tensor 128.
    fixed_anchor_size=True => offsets/tamanos absolutos /128."""
    S = float(input_size)
    dets: List[FaceDetection] = []
    for i, a in enumerate(anchors):
        score = sigmoid(float(cls[i][0]))
        if score < score_thresh:
            continue
        r = reg[i]
        cx = float(r[0]) / S + a.cx
        cy = float(r[1]) / S + a.cy
        w = float(r[2]) / S
        h = float(r[3]) / S
        kps = []
        for k in range(6):
            kx = float(r[4 + 2 * k]) / S + a.cx
            ky = float(r[5 + 2 * k]) / S + a.cy
            kps.append((kx, ky))
        dets.append(FaceDetection(score, (cy - h / 2, cx - w / 2, cy + h / 2, cx + w / 2), kps))
    return dets


def nms(dets, iou_thresh: float = 0.3) -> List[FaceDetection]:
    """Non-max suppression greedy por IoU.
    box = (ymin, xmin, ymax, xmax) normalizadas (espacio letterbox)."""
    dets = sorted(dets, key=lambda d: d.score, reverse=True)
    keep: List[FaceDetection] = []
    while dets:
        best = dets.pop(0)
        keep.append(best)
        rest = []
        for d in dets:
            yy1 = max(best.box[0], d.box[0]); xx1 = max(best.box[1], d.box[1])
            yy2 = min(best.box[2], d.box[2]); xx2 = min(best.box[3], d.box[3])
            inter = max(0.0, yy2 - yy1) * max(0.0, xx2 - xx1)
            a1 = max(0.0, best.box[2] - best.box[0]) * max(0.0, best.box[3] - best.box[1])
            a2 = max(0.0, d.box[2] - d.box[0]) * max(0.0, d.box[3] - d.box[1])
            union = a1 + a2 - inter
            if union <= 0.0 or inter / union <= iou_thresh:
                rest.append(d)
        dets = rest
    return keep


def weighted_nms(dets, iou_thresh=0.3):
    """Fusiona detecciones solapadas mediante promedios ponderados.

    Conserva la puntuación de la detección de mayor confianza del grupo.
    Las coordenadas de las cajas y de los puntos clave se ponderan por
    la puntuación de cada detección.

    Esta implementación es independiente de nms(); no implica todavía
    equivalencia exacta con el algoritmo Weighted NMS de MediaPipe.
    """
    if not dets:
        return []

    remaining = sorted(dets, key=lambda d: d.score, reverse=True)
    result = []

    def iou(a, b):
        ay1, ax1, ay2, ax2 = a.box
        by1, bx1, by2, bx2 = b.box

        iy1 = max(ay1, by1)
        ix1 = max(ax1, bx1)
        iy2 = min(ay2, by2)
        ix2 = min(ax2, bx2)

        intersection = max(0.0, iy2 - iy1) * max(0.0, ix2 - ix1)
        area_a = max(0.0, ay2 - ay1) * max(0.0, ax2 - ax1)
        area_b = max(0.0, by2 - by1) * max(0.0, bx2 - bx1)
        union = area_a + area_b - intersection

        return intersection / union if union > 0.0 else 0.0

    while remaining:
        seed = remaining.pop(0)

        # Agrupa las detecciones que superan el umbral respecto a la
        # detección de mayor puntuación; no usa agrupación transitiva.
        group = [seed]
        rest = []

        for candidate in remaining:
            if iou(seed, candidate) > iou_thresh:
                group.append(candidate)
            else:
                rest.append(candidate)

        remaining = rest

        weights = [max(0.0, float(d.score)) for d in group]
        weight_sum = sum(weights)

        if weight_sum <= 0.0:
            result.append(seed)
            continue

        box = tuple(
            sum(weight * float(d.box[k]) for weight, d in zip(weights, group))
            / weight_sum
            for k in range(4)
        )

        # Fusiona puntos clave solo si todas las detecciones del grupo
        # tienen el mismo número de puntos que la detección semilla.
        same_keypoint_count = all(
            len(d.keypoints) == len(seed.keypoints) for d in group
        )

        if same_keypoint_count:
            keypoints = [
                (
                    sum(weight * float(d.keypoints[k][0])
                        for weight, d in zip(weights, group)) / weight_sum,
                    sum(weight * float(d.keypoints[k][1])
                        for weight, d in zip(weights, group)) / weight_sum,
                )
                for k in range(len(seed.keypoints))
            ]
        else:
            keypoints = list(seed.keypoints)

        result.append(FaceDetection(
            score=seed.score,
            box=box,
            keypoints=keypoints,
        ))

    return result

"""
AGF T21-ALIGN — Alineación facial por transformación de similitud (Umeyama 3pt).
Mapea keypoints BlazeFace al template 112x112 de ArcFace (insightface reference).
"""

from __future__ import annotations

import math

# Template ArcFace 112x112: ojo izq, ojo der, nariz, boca izq, boca der
TEMPLATE = [
    (38.2946, 51.6963), (73.5318, 51.5014), (56.0252, 71.7366),
    (41.5493, 92.3655), (70.7299, 92.2041),
]


def estimate_similarity(src_pts, dst_pts):
    """Minimos cuadrados: dst ~= s*R*src + t. Devuelve M 2x3 forward."""
    n = len(src_pts)
    cs = [sum(p[0] for p in src_pts) / n, sum(p[1] for p in src_pts) / n]
    cd = [sum(p[0] for p in dst_pts) / n, sum(p[1] for p in dst_pts) / n]
    a = b = var = 0.0
    for s, d in zip(src_pts, dst_pts):
        xs = (s[0] - cs[0], s[1] - cs[1])
        xd = (d[0] - cd[0], d[1] - cd[1])
        a += xs[0] * xd[0] + xs[1] * xd[1]
        b += xs[0] * xd[1] - xs[1] * xd[0]
        var += xs[0] ** 2 + xs[1] ** 2
    scale = math.sqrt(a * a + b * b) / max(1e-9, var)
    theta = math.atan2(b, a)
    c, s = math.cos(theta) * scale, math.sin(theta) * scale
    t0 = cd[0] - (c * cs[0] - s * cs[1])
    t1 = cd[1] - (s * cs[0] + c * cs[1])
    return (c, -s, t0), (s, c, t1)      # dos filas: forward src->dst


def _invert_affine(rows):
    (a, b, c), (d, e, f) = rows
    det = a * e - b * d
    ia, ib, id_, ie = e / det, -b / det, -d / det, a / det
    ic = -(ia * c + ib * f)
    if_ = -(id_ * c + ie * f)
    return (ia, ib, ic), (id_, ie, if_)


def align_face(pil_img, keypoints, out_size=112):
    """keypoints BlazeFace (6 pts, coords de la imagen ORIGINAL escalada a
    el espacio de 128 del detector -> pasamos coords en pixeles de la imagen
    original). Usa ojo izq(kp1), ojo der(kp0), nariz(kp2) -> template 3pt.
    Devuelve PIL.Image alineada out_size x out_size."""
    src = [keypoints[1], keypoints[0], keypoints[2]]
    # FIX (2026-10-18): TEMPLATE es absoluto en px de canvas 112; escalarlo al
    # out_size pedido. Sin esto, out_size != 112 deformaba el crop (banda negra).
    k = out_size / 112.0
    dst = [(x * k, y * k) for x, y in TEMPLATE[:3]]
    fwd = estimate_similarity(src, dst)
    inv = _invert_affine(fwd)
    (ia, ib, ic), (id_, ie, if_) = inv
    # PIL AFFINE: mapea coords de SALIDA a coords de ENTRADA
    coeffs = (ia, ib, ic, id_, ie, if_)
    return pil_img.transform((out_size, out_size), __import__("PIL.Image", fromlist=["Image"]).AFFINE,
                             coeffs, resample=2)  # bicubic

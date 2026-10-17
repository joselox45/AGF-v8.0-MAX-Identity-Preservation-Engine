"""
AGF T36a — SSIM metrico informativo (stdlib puro, sin scipy).
Mide similitud estructural en ventanas; va como metrica CRUZADA junto al
cosine del embedding. SSIM mide estructura, NO identidad — no sustituye L2.
Uso: ssim_gray(a2d, b2d) con matrices de grises (listas anidadas).
"""

from __future__ import annotations


def _to_gray(pixels):
    """[[[r,g,b]...]...] -> [[gris...]...]"""
    return [[(p[0] * 299 + p[1] * 587 + p[2] * 114) // 1000 for p in row]
            for row in pixels]


def ssim_gray(a, b, win: int = 8) -> float:
    """SSIM promedio por ventanas win x en imagenes de grises (stdlib puro).
    Devuelve float en [-1, 1] (valores tipicos 0..1 para imagenes similares).
    Imagenes de distinto tamano -> ValueError."""
    if len(a) != len(b) or (a and len(a[0]) != len(b[0])):
        raise ValueError("dimensiones incompatibles")
    h, w = len(a), len(a[0])
    if h < win or w < win:
        raise ValueError(f"imagen menor que la ventana ({win})")
    c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    total, n = 0.0, 0
    for y in range(0, h - win + 1, win):
        for x in range(0, w - win + 1, win):
            va = [a[y + dy][x + dx] for dy in range(win) for dx in range(win)]
            vb = [b[y + dy][x + dx] for dy in range(win) for dx in range(win)]
            n2 = win * win
            ma = sum(va) / n2
            mb = sum(vb) / n2
            va_ = [v - ma for v in va]
            vb_ = [v - mb for v in vb]
            saa = sum(v * v for v in va_) / n2
            sbb = sum(v * v for v in vb_) / n2
            sab = sum(x * y for x, y in zip(va_, vb_)) / n2
            num = (2 * ma * mb + c1) * (2 * sab + c2)
            den = (ma * ma + mb * mb + c1) * (saa + sbb + c2)
            total += num / den if den else 0.0
            n += 1
    return round(total / n, 6) if n else 0.0

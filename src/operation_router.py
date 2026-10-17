"""
AGF T33 — OperationRouter: objetivo en lenguaje natural (ES/EN)
-> operacion AGF. Fail-closed: sin match unico -> BLOCKED (no adivinar).
El ruteo alimenta el pipeline medible (kernel -> ventana -> RECIBO ->
medicion -> vault); nunca salta la verificacion.
"""

from __future__ import annotations

OPERATIONS = {
    "REPAIR": ["reparar", "fix", "arreglar", "arregla",
               "danada", "dañada", "danado", "dañado", "rasguño",
               "rasgadura", "mancha", "pixeles corruptos", "artefacto"],
    "RESTORE": ["restore", "restaurar", "old photo", "foto antigua",
                "antigua", "recuperar", "degradada", "descolorida"],
    "RECONSTRUCT": ["reconstruir", "parte faltante", "rebuild",
                    "missing part", "region faltante", "falta una parte"],
    "SEGMENT": ["quitar fondo", "remove background", "recortar", "aislar",
                "background removal", "transparente", "cutout"],
    "VARIANT": ["cambiar ropa", "cambiar atuendo", "fondo nuevo",
                "nuevo fondo", "cambiar fondo", "cambiar el fondo",
                "cambiar pose", "otro lugar", "cambiar escena"],
}


def route(objective: str) -> str:
    """Objetivo (cualquier idioma) -> operacion AGF.
    Fail-closed: 0 coincidencias o >1 -> BLOCKED (ambiguedad no se adivina,
    coherente con R5/R7 del kernel v3 y G1 del governor)."""
    if not objective or not objective.strip():
        return "BLOCKED"
    o = objective.lower()
    hits = [op for op, kws in OPERATIONS.items()
            if any(k in o for k in kws)]
    return hits[0] if len(hits) == 1 else "BLOCKED"

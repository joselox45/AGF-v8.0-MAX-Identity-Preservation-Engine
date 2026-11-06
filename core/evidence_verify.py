"""Verificación de integridad del ledger: contenido + cadena.

- event_sha256 vs recálculo: atrapa edición de bytes.
- prev_hash vs hash de línea anterior: atrapa reordenamiento
  y borrado de líneas.

NO protege contra quien reescribe el archivo entero y recalcula
toda la cadena: para eso se necesita anclaje externo del head hash.
"""
from __future__ import annotations

import json
import os
import sys

# Añadir el directorio actual al path para importar evidence_ledger
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from evidence_ledger import digest_text, canonical_json


def verify_ledger(path: str) -> dict:
    total, valid = 0, 0
    tampered, chain_breaks = [], []
    prev_line_hash = None

    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            total += 1
            try:
                wrapper = json.loads(line)
            except json.JSONDecodeError:
                tampered.append({"line": lineno, "reason": "JSON inválido"})
                continue

            # 1. Verificar hash del evento (contenido)
            event = wrapper.get("event", {})
            event_sha = wrapper.get("event_sha256", "")
            recalculated = digest_text(canonical_json(event))

            if recalculated != event_sha:
                tampered.append({"line": lineno, "reason": "event_sha256 no coincide"})
                continue

            # 2. Verificar hash de cadena (prev_hash)
            prev = wrapper.get("prev_hash", "")
            if prev_line_hash is None:
                if prev != "GENESIS":
                    chain_breaks.append({"line": lineno, "reason": "primer evento no es GENESIS"})
                    continue
            else:
                if prev != prev_line_hash:
                    chain_breaks.append({"line": lineno, "reason": "prev_hash no coincide"})
                    continue

            valid += 1
            prev_line_hash = event_sha

    return {
        "total": total,
        "valid": valid,
        "tampered": tampered,
        "chain_breaks": chain_breaks,
    }

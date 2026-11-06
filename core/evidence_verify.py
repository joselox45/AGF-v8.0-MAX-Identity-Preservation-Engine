"""Verificacion de integridad del ledger: contenido + cadena.

- event_sha256 vs recalculo: atrapa edicion de bytes.
- prev_hash vs hash de linea anterior: atrapa reordenamiento
  y borrado de lineas.

NO protege contra quien reescribe el archivo entero y recalcula
toda la cadena (ver REJECTED.md R1): para eso se necesita anclaje
externo del head hash.
"""
from __future__ import annotations

import json

from .evidence_ledger import digest_text, canonical_json


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
                event = wrapper["event"]
                recorded = wrapper["event_sha256"]
            except (json.JSONDecodeError, KeyError):
                tampered.append((lineno, "formato_invalido"))
                prev_line_hash = digest_text(line)
                continue

            if digest_text(canonical_json(event)) != recorded:
                tampered.append((lineno, "hash_no_coincide"))

            expected_prev = prev_line_hash if prev_line_hash else "GENESIS"
            if wrapper.get("prev_hash") != expected_prev:
                chain_breaks.append(
                    (lineno, "cadena_rota: prev_hash no coincide"))

            prev_line_hash = digest_text(line)
            if not any(t[0] == lineno for t in tampered) and \
               not any(c[0] == lineno for c in chain_breaks):
                valid += 1

    return {"total": total, "valid": valid,
            "tampered_count": len(tampered), "tampered": tampered,
            "chain_breaks": chain_breaks,
            "chain_ok": len(chain_breaks) == 0,
            "head_hash": prev_line_hash}

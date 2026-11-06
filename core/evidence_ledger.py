"""Ledger de evidencia JSONL con SHA-256 encadenado (hash-chain).

Cada evento lleva:
- event_sha256: hash del evento (atrapa edicion de contenido)
- prev_hash: hash de la linea anterior (atrapa reordenamiento y borrado)

Genesis: el primer evento usa prev_hash = "GENESIS".
El hash encadenado cubre la linea wrapper completa: nadie puede
alterar, mover o eliminar lineas sin romper la cadena.
"""
from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path


def digest_text(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def canonical_json(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"))


class EvidenceLedger:
    """Ledger JSONL append-only con hash-chain. Modificable solo
    reescribiendo el archivo entero, lo que la verificacion detecta."""

    GENESIS = "GENESIS"

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._prev = self._last_hash()

    def _last_hash(self) -> str | None:
        if not self.path.exists():
            return None
        last = None
        with self.path.open("r", encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    last = line.rstrip("\n")
        return digest_text(last) if last else None

    def append(self, event: dict) -> str:
        line = canonical_json(event)
        event_hash = digest_text(line)
        wrapper = {"event": event, "event_sha256": event_hash,
                   "prev_hash": self._prev or self.GENESIS}
        wrapper_line = canonical_json(wrapper)
        wrapper_hash = digest_text(wrapper_line)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(wrapper_line + "\n")
        self._prev = wrapper_hash
        return event_hash

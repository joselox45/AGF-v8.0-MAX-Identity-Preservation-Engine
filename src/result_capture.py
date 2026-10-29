"""
AGF Chat Runtime v0.1 — RESULT CAPTURE
======================================
Registro del resultado devuelto por la ventana de chat. Exige que el
operador/LLM declare la procedencia: RECOVERED | RECONSTRUCTED | GENERATED.
Procedencia no declarada -> UNVERIFIED (nunca PASS).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, asdict
from typing import Optional

PROVENANCE_TAGS = ("RECOVERED", "RECONSTRUCTED", "GENERATED")


@dataclass
class OutputRecord:
    output_id: str
    origin: str                    # OPERATOR (pegado humano)
    declared_provenance: Optional[str]
    status: str                    # PASS | UNVERIFIED | FAIL
    reason: str = ""

    def to_dict(self):
        return asdict(self)


class ResultCapture:
    def capture(self, output_bytes: Optional[bytes],
                declared_provenance: Optional[str]) -> OutputRecord:
        if not output_bytes:
            return OutputRecord("", "OPERATOR", None, "FAIL",
                                "sin resultado recibido")
        output_id = hashlib.sha512(output_bytes).hexdigest()
        if declared_provenance not in PROVENANCE_TAGS:
            return OutputRecord(output_id, "OPERATOR", None, "UNVERIFIED",
                                "procedencia no declarada; RECOVERED/"
                                "RECONSTRUCTED/GENERATED son distintos")
        return OutputRecord(output_id, "OPERATOR", declared_provenance,
                            "PASS", "procedencia declarada explícitamente")

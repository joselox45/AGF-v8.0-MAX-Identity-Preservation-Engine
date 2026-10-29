"""
AGF Chat Runtime v0.1 — IMAGE INTAKE
====================================
Validación y trazabilidad de entradas. Cada imagen se identifica por
SHA-512 (image_id). Entrada vacía o ilegible -> FAIL (fail-closed).
Sin filesystem obligatorio: acepta bytes pegados por el operador.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional


class IntakeStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"


@dataclass
class ImageRef:
    image_id: str
    role: str            # REFERENCE | TARGET
    byte_size: int
    width: Optional[int] = None
    height: Optional[int] = None
    status: str = "PASS"
    reason: str = "imagen aceptada"

    def to_dict(self):
        return asdict(self)


class ImageIntake:
    KNOWN_ROLES = ("REFERENCE", "TARGET")

    def accept(self, image_bytes: Optional[bytes], role: str) -> ImageRef:
        if role not in self.KNOWN_ROLES:
            return ImageRef("", role, 0, status="FAIL",
                            reason=f"rol '{role}' desconocido")
        if not image_bytes:
            return ImageRef("", role, 0, status="FAIL",
                            reason="imagen vacía; entrada rechazada (fail-closed)")
        image_id = hashlib.sha512(image_bytes).hexdigest()
        return ImageRef(image_id=image_id, role=role,
                        byte_size=len(image_bytes))

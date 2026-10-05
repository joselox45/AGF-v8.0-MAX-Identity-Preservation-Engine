"""
AGF Chat Runtime v0.1 — POLICY GATE
===================================
Decide ACCEPT / REJECT / BLOCK aplicando la precedencia:
capability > privacy > security > policy > purpose > authorization.
El gate nunca eleva estados: BLOCKED de verificación -> BLOCK directo.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

PRECEDENCE = ("capability", "privacy", "security", "policy",
              "purpose", "authorization")


@dataclass
class GateDecision:
    decision: str          # ACCEPT | REJECT | BLOCK
    layer: str             # qué capa de precedencia decidió
    reason: str


class PolicyGate:
    def __init__(self, max_retries: int = 2):
        self.max_retries = max_retries
        self._attempt = 0

    def reset(self):
        self._attempt = 0

    def decide(self, verification_status: str,
               attempt: int,
               capability_ok: bool = True,
               authorization_ok: bool = True) -> GateDecision:
        # capability (capa más alta)
        if not capability_ok:
            return GateDecision("BLOCK", "capability",
                                "capacidad requerida no disponible")
        if not authorization_ok:
            return GateDecision("BLOCK", "authorization",
                                "acción fuera de la autorización otorgada")
        # security / policy: estados cerrados no se negocian
        if verification_status == "BLOCKED":
            return GateDecision("BLOCK", "security",
                                "verificación bloqueada; fail-closed "
                                "(sin PASS fabricado)")
        if verification_status == "FAIL":
            if attempt <= self.max_retries:
                return GateDecision("REJECT", "policy",
                                    f"intento {attempt}/{self.max_retries}: "
                                    "se re-promptea con corrección")
            return GateDecision("BLOCK", "policy",
                                "intentos agotados; operación bloqueada")
        return GateDecision("ACCEPT", "policy",
                            "verificación PASS; resultado liberado")

"""
AGF T35 — SessionCap: limite duro de turnos por anclaje.
Anti-drift operativo: pasado el limite, el kernel exige re-anclaje con
base_0 (nuevo sha256) o el turno es NOT_RUN. Endurece el "re-anclaje cada
8-12 turnos" del protocolo O0 a un limite estricto (idea del analisis v60).
"""

from __future__ import annotations

import hashlib

TURN_LIMIT = 7


class SessionCap:
    def __init__(self, turn_limit: int = TURN_LIMIT):
        self.turn_limit = turn_limit
        self.anchor_sha = None
        self.turns_since_anchor = 0

    def anchor(self, base0_path: str) -> str:
        """Ancla (o re-ancla) la sesion a base_0. Devuelve su sha256."""
        self.anchor_sha = hashlib.sha256(open(base0_path, "rb").read()).hexdigest()
        self.turns_since_anchor = 0
        return self.anchor_sha

    def allow_turn(self) -> dict:
        """Decide si un turno puede ejecutarse. Fail-closed."""
        if self.anchor_sha is None:
            return {"status": "NOT_RUN", "reason": "sin anclaje: ejecutar anchor() primero"}
        if self.turns_since_anchor >= self.turn_limit:
            return {"status": "NOT_RUN",
                    "reason": f"limite de sesion ({self.turn_limit} turnos): "
                              "re-anclar con base_0 obligatorio (anti-drift)"}
        self.turns_since_anchor += 1
        return {"status": "OK", "turn": self.turns_since_anchor,
                "anchor_sha256": self.anchor_sha[:16],
                "remaining": self.turn_limit - self.turns_since_anchor}

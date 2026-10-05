"""
APCEGovernor v1.0 — AGF como Verification Evaluator bajo autoridad APCE.
=======================================================================
APCE v8.1.0 = control plane canónico. AGF = evaluation plane.
Este módulo es la ÚNICA puerta por la cual un veredicto técnico de AGF
puede convertirse en decisión asegurada. Aplica reglas G1–G6 del contrato.
Stdlib puro, fail-closed, salida JSON portátil (chat-window contract).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from typing import Optional

APCE_VERSION = "8.1.0-CANONICAL"
GOVERNOR_VERSION = "1.0"

PRECEDENCE = ("capability", "privacy", "security", "policy",
              "purpose", "authorization")
APCE_BLOCKING_STATES = ("EVIDENCE_GAP", "VERSION_GAP", "CONFLICT",
                        "FAILED", "EXECUTED_NOT_VERIFIED",
                        "IMPLEMENTABILITY_GAP")


@dataclass
class AGFVerdict:
    """Veredicto técnico emitido por cualquier componente AGF."""
    component: str          # MTE | EMBEDDING | EVIDENCE | IDENTITY | CHAT_RUNTIME
    verdict: str            # PASS | FAIL | BLOCKED | UNVERIFIED | NOT_RUN
    evidence_hash: Optional[str] = None
    detail: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass
class GovernedDecision:
    """Decisión final tras revisión APCE."""
    outcome: str            # CONFIRMED | DOWNGRADED | VETOED
    agf_verdict: str
    final_state: str        # PASS | FAIL | BLOCKED
    rule: str               # G1..G6 | OK
    apce_version: str
    evidence_hash: Optional[str]
    reason: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


class APCEGovernor:
    def __init__(self, apce_state: str = "OPERATIVE",
                 capability_ok: bool = True,
                 authorization_ok: bool = True):
        # apce_state: OPERATIVE | cualquier APCE_BLOCKING_STATES
        self.apce_state = apce_state
        self.capability_ok = capability_ok
        self.authorization_ok = authorization_ok

    # ------------------------------------------------------------------
    def review(self, v: AGFVerdict) -> GovernedDecision:
        # G3: bloqueos de precedencia APCE (capability es la capa más alta)
        if not self.capability_ok:
            return self._govern("DOWNGRADED", "BLOCKED", "G3",
                                "capability no disponible; capa APCE más alta")
        if not self.authorization_ok:
            return self._govern("DOWNGRADED", "BLOCKED", "G3",
                                "autorización insuficiente")
        # G2 + bloqueos APCE: estado canónico no operativo => fail-closed
        if self.apce_state != "OPERATIVE":
            return self._govern("VETOED", "BLOCKED", "G4",
                                f"estado APCE bloqueante: {self.apce_state}")
        # G1: PASS sin evidencia = fabricación
        if v.verdict == "PASS" and not v.evidence_hash:
            return self._govern("DOWNGRADED", "BLOCKED", "G1",
                                "PASS AGF sin evidence_hash; no fabrication")
        # G2: estados cerrados se propagan, nunca se promueven
        if v.verdict in ("BLOCKED", "UNVERIFIED", "NOT_RUN"):
            return self._govern("DOWNGRADED", "BLOCKED", "G2",
                                f"veredicto AGF '{v.verdict}' no promovible")
        # G5: PASS/FAIL con evidencia -> CONFIRMED, sellado
        return self._govern("CONFIRMED", v.verdict, "G5",
                            "veredicto AGF confirmado bajo autoridad APCE",
                            evidence=v.evidence_hash)

    # ------------------------------------------------------------------
    def _govern(self, outcome, final, rule, reason,
                evidence: Optional[str] = None) -> GovernedDecision:
        return GovernedDecision(outcome=outcome, agf_verdict=final,
                                final_state=final, rule=rule,
                                apce_version=APCE_VERSION,
                                evidence_hash=evidence, reason=reason)

    def assurance_gate(self, agf_tests_ok: bool,
                       independent_evidence: bool) -> str:
        """G6: AGF alimenta, APCE transiciona. Solo APCE promueve estados."""
        if not agf_tests_ok:
            return "TESTED-BLOCKED"
        if independent_evidence:
            return "ELIGIBLE_FOR_INDEPENDENT_ATTESTATION"
        return "ELIGIBLE_FOR_TESTED"   # nunca OPERATING_EFFECTIVE sin evidencia operacional

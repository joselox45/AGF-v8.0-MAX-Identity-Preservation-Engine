"""
APCEGovernor v1.1 — AGF como Verification Evaluator bajo autoridad APCE.
F-01/F-04 (auditoria 13): evidence_hash valido exigido para PASS y FAIL;
precedencia G3 completa (privacy/security/purpose verificables).
Stdlib puro, fail-closed.
"""

from __future__ import annotations

import hashlib
import json
import re as _re
from dataclasses import dataclass, asdict
from typing import Optional

APCE_VERSION = "8.1.0-CANONICAL"
GOVERNOR_VERSION = "1.1"

PRECEDENCE = ("capability", "privacy", "security", "policy",
              "purpose", "authorization")
APCE_BLOCKING_STATES = ("EVIDENCE_GAP", "VERSION_GAP", "CONFLICT",
                        "FAILED", "EXECUTED_NOT_VERIFIED",
                        "IMPLEMENTABILITY_GAP")


@dataclass
class AGFVerdict:
    component: str
    verdict: str            # PASS | FAIL | BLOCKED | UNVERIFIED | NOT_RUN
    evidence_hash: Optional[str] = None
    detail: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass
class GovernedDecision:
    outcome: str            # CONFIRMED | DOWNGRADED | VETOED
    agf_verdict: str
    final_state: str
    rule: str               # G1..G6 | OK
    apce_version: str
    evidence_hash: Optional[str]
    reason: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


class APCEGovernor:
    def __init__(self, apce_state: str = "OPERATIVE",
                 capability_ok: bool = True,
                 authorization_ok: bool = True,
                 privacy_ok: bool = True,     # F-04: precedencia completa
                 security_ok: bool = True,
                 purpose_ok: bool = True):
        self.apce_state = apce_state
        self.capability_ok = capability_ok
        self.authorization_ok = authorization_ok
        self.privacy_ok = privacy_ok
        self.security_ok = security_ok
        self.purpose_ok = purpose_ok

    def review(self, v: AGFVerdict) -> GovernedDecision:
        # G3: precedencia completa (auditoria 13, F-04)
        for name, ok in (("capability", self.capability_ok),
                         ("authorization", self.authorization_ok),
                         ("privacy", self.privacy_ok),
                         ("security", self.security_ok),
                         ("purpose", self.purpose_ok)):
            if not ok:
                return self._govern("DOWNGRADED", "BLOCKED", "G3",
                                    f"{name}: control material no satisfecho")
        # G2 + bloqueos APCE
        if self.apce_state != "OPERATIVE":
            return self._govern("VETOED", "BLOCKED", "G4",
                                f"estado APCE bloqueante: {self.apce_state}")
        # G1: PASS sin evidencia = fabricacion
        if v.verdict == "PASS" and not v.evidence_hash:
            return self._govern("DOWNGRADED", "BLOCKED", "G1",
                                "PASS AGF sin evidence_hash; no fabrication")
        # G2: estados cerrados se propagan
        if v.verdict in ("BLOCKED", "UNVERIFIED", "NOT_RUN"):
            return self._govern("DOWNGRADED", "BLOCKED", "G2",
                                f"veredicto AGF '{v.verdict}' no promovible")
        # G5 + F-01: CONFIRMED exige evidence_hash con formato valido
        # para PASS *y* FAIL — un FAIL sin evidencia no se confirma.
        if not v.evidence_hash or not _re.fullmatch(r"[0-9a-f]{64,128}",
                                                    v.evidence_hash):
            return self._govern("DOWNGRADED", "BLOCKED", "G1",
                                "veredicto sin evidence_hash valido "
                                "(aplica a PASS y FAIL)")
        return self._govern("CONFIRMED", v.verdict, "G5",
                            "veredicto AGF confirmado bajo autoridad APCE",
                            evidence=v.evidence_hash)

    def _govern(self, outcome, final, rule, reason,
                evidence: Optional[str] = None) -> GovernedDecision:
        return GovernedDecision(outcome=outcome, agf_verdict=final,
                                final_state=final, rule=rule,
                                apce_version=APCE_VERSION,
                                evidence_hash=evidence, reason=reason)

    def assurance_gate(self, agf_tests_ok: bool,
                       independent_evidence: bool) -> str:
        if not agf_tests_ok:
            return "TESTED-BLOCKED"
        if independent_evidence:
            return "ELIGIBLE_FOR_INDEPENDENT_ATTESTATION"
        return "ELIGIBLE_FOR_TESTED"


def verify_governor_smoke():
    """F-01/F-04 self-check: FAIL sin evidence -> BLOCKED; privacy_ok=False -> G3."""
    g = APCEGovernor()
    r1 = g.review(AGFVerdict("MTE", "FAIL", None, ""))
    r2 = APCEGovernor(privacy_ok=False).review(AGFVerdict("MTE", "PASS", "ab" * 32))
    ok = (r1.final_state == "BLOCKED" and r2.rule == "G3"
          and r2.rule == "G3")
    print(json.dumps({"smoke_F01_F04": "PASS" if ok else "FAIL",
                      "r1": r1.final_state, "r2_rule": r2.rule}))


if __name__ == "__main__":
    verify_governor_smoke()

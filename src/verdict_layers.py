"""
AGF — Veredictos en capas (objetivo 2026-10-14):
"integracion de pruebas + verificacion de imagenes reproducible,
SIN confundir un resultado formal PASS con una identidad facial preservada".

Tres capas estrictamente separadas:
  L1 FORMAL   -> checks estructurales (hashes, cobertura, evidencia presente)
  L2 BIOMETRIC-> cosine de embedding >= umbral (y NO anti-replay)
  L3 IDENTITY -> "identidad preservada" = afirmacion SEMANTICA.
                 NUNCA se deduce de L1 o L2 solos. Requiere:
                 L2 PASS + procedencia declarada + discriminacion
                 cruzada (mismo sujeto acepta / distinto rechaza).
                 Default fail-closed: NOT_DETERMINED.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from enum import Enum
from typing import Optional


class Layer(str, Enum):
    L1_FORMAL = "L1_FORMAL"
    L2_BIOMETRIC = "L2_BIOMETRIC"
    L3_IDENTITY = "L3_IDENTITY"


FORMAL_STATES = ("PASS", "FAIL", "BLOCKED", "UNVERIFIED", "NOT_RUN")
BIOMETRIC_STATES = ("PASS", "FAIL", "BLOCKED")
IDENTITY_STATES = ("SUPPORTED", "NOT_DETERMINED", "REFUTED")


@dataclass
class LayeredVerdict:
    L1_formal: str
    L2_biometric: str
    L3_identity: str
    cosine: Optional[float] = None
    threshold: Optional[float] = None
    reasons: list = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


class VerdictLayers:
    """Combina resultados ya obtenidos; nunca inventa ninguno."""

    def evaluate(self, *,
                 formal_status: str,          # de mte_runner_v2 / governor
                 biometric_status: str,       # de closure / comparator
                 cosine: Optional[float],
                 threshold: Optional[float],
                 provenance_declared: bool,   # del report [AGF_VERIFICATION_REPORT]
                 cross_person_tested: bool,   # existe evidencia distinto-sujeto (FAR)
                 anti_replay_clean: bool = True) -> LayeredVerdict:
        reasons = []

        # ---- L1: formal tal cual
        if formal_status not in FORMAL_STATES:
            formal_status = "BLOCKED"
            reasons.append("L1: estado formal invalido -> BLOCKED")

        # ---- L2: biometria tal cual + anti-replay es condicion
        if not anti_replay_clean:
            biometric_status = "BLOCKED"
            reasons.append(
                "L2: revisión anti-replay requerida -> BLOCKED; "
                "no constituye por sí sola prueba de fraude"
            )
        if biometric_status not in BIOMETRIC_STATES:
            biometric_status = "BLOCKED"
            reasons.append("L2: estado biometrico invalido -> BLOCKED")

        # ---- L3: identidad preservada (fail-closed por construccion)
        if biometric_status == "FAIL":
            identity = "REFUTED"
            reasons.append("L3: biometria FAIL -> identidad REFUTED "
                           "(la salida no corresponde al sujeto)")
        elif (biometric_status == "PASS"
              and formal_status == "PASS"
              and provenance_declared
              and cross_person_tested):
            identity = "SUPPORTED"
            reasons.append("L3: L1 PASS + L2 PASS + procedencia declarada + "
                           "discriminacion cruzada -> identidad SUPPORTED")
        else:
            identity = "NOT_DETERMINED"
            missing = []
            if biometric_status != "PASS":
                missing.append("L2 PASS")
            if formal_status != "PASS":
                missing.append("L1 PASS")
            if not provenance_declared:
                missing.append("procedencia declarada")
            if not cross_person_tested:
                missing.append("discriminacion cruzada (par distinto-sujeto)")
            reasons.append("L3: identidad NO DETERMINADA; falta: "
                           + ", ".join(missing))

        return LayeredVerdict(L1_formal=formal_status,
                              L2_biometric=biometric_status,
                              L3_identity=identity,
                              cosine=cosine, threshold=threshold,
                              reasons=reasons)


RULES_DOC = """
REGLA CENTRAL (no negociable):
  Un PASS en L1 (formal) o L2 (biometrico) NUNCA implica L3 SUPPORTED.
  L3 solo se soporta con: L1 PASS + L2 PASS + procedencia declarada +
  discriminacion cruzada. Default: NOT_DETERMINED.
  Un L2 FAIL implica L3 REFUTED (la salida no es el sujeto).
"""

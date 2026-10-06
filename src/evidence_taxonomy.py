"""
AGF v9.0 — T29: Taxonomía de estados de evidencia.
==================================================
Ampliación del modelo de evidencia (auditoría externa §6):
NO_EVIDENCE | EVIDENCE_UNAVAILABLE | EVIDENCE_INVALID |
EVIDENCE_INSUFFICIENT | EVIDENCE_VALID | EVIDENCE_INDEPENDENT

Regla MTE: solo EVIDENCE_VALID o EVIDENCE_INDEPENDENT computan conformidad.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional


class EvidenceState(str, Enum):
    NO_EVIDENCE = "NO_EVIDENCE"
    EVIDENCE_UNAVAILABLE = "EVIDENCE_UNAVAILABLE"
    EVIDENCE_INVALID = "EVIDENCE_INVALID"
    EVIDENCE_INSUFFICIENT = "EVIDENCE_INSUFFICIENT"
    EVIDENCE_VALID = "EVIDENCE_VALID"
    EVIDENCE_INDEPENDENT = "EVIDENCE_INDEPENDENT"


CONFORMANT_STATES = (EvidenceState.EVIDENCE_VALID,
                     EvidenceState.EVIDENCE_INDEPENDENT)


@dataclass
class EvidenceClassification:
    state: EvidenceState
    conformant: bool
    reason: str

    def to_dict(self):
        return asdict(self)


class EvidenceClassifier:
    """Clasificador determinista y fail-closed."""

    def classify(self, present: bool,
                 hash_format_ok: Optional[bool] = None,
                 verified: Optional[bool] = None,
                 independent: Optional[bool] = None,
                 unavailable_reason: bool = False) -> EvidenceClassification:
        if not present:
            if unavailable_reason:
                return EvidenceClassification(
                    EvidenceState.EVIDENCE_UNAVAILABLE, False,
                    "evidencia requerida no producible en este entorno")
            return EvidenceClassification(
                EvidenceState.NO_EVIDENCE, False,
                "sin evidencia presentada")
        if hash_format_ok is False:
            return EvidenceClassification(
                EvidenceState.EVIDENCE_INVALID, False,
                "hash/estructura de evidencia inválida")
        if not verified:
            return EvidenceClassification(
                EvidenceState.EVIDENCE_INSUFFICIENT, False,
                "evidencia presente pero no verificada")
        if independent:
            return EvidenceClassification(
                EvidenceState.EVIDENCE_INDEPENDENT, True,
                "evidencia verificada por tercero independiente")
        return EvidenceClassification(
            EvidenceState.EVIDENCE_VALID, True,
            "evidencia verificada internamente")

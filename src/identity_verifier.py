"""
AGF Chat Runtime v0.1 — IDENTITY VERIFIER
=========================================
Verificación de preservación de identidad sobre el resultado.
FAIL-CLOSED: sin embedder biométrico real (v9.0 face_embedding) la
verificación devuelve BLOCKED; jamás un PASS fabricado. La distinción
RECOVERED/RECONSTRUCTED/GENERATED se propaga a la decisión: GENERATED
no puede producir ACCEPT en la ruta de restauración.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol


class Embedder(Protocol):
    """Contrato compatible con v9.0 OnnxFaceEmbedder."""

    def embed(self, rgb_pixels, bbox=None):
        ...


@dataclass
class VerificationResult:
    status: str            # PASS | FAIL | BLOCKED
    identity_preserved: Optional[bool]
    provenance: Optional[str]
    detail: str
    evidence_hash: Optional[str] = None


class IdentityVerifier:
    RESTORE_ACCEPTABLE = ("RECOVERED", "RECONSTRUCTED")

    def __init__(self, embedder: Optional[Embedder] = None,
                 threshold: float = 0.65):
        self.embedder = embedder
        self.threshold = threshold

    def verify(self, reference_rgb, output_rgb,
               declared_provenance: Optional[str]) -> VerificationResult:
        # Regla de procedencia primero: GENERATED no es restauración.
        if declared_provenance == "GENERATED":
            return VerificationResult(
                "FAIL", False, declared_provenance,
                "GENERATED ≠ restauración; viola el objetivo de la operación")
        # Sin canal biométrico real: BLOCKED (fail-closed).
        if self.embedder is None:
            return VerificationResult(
                "BLOCKED", None, declared_provenance,
                "sin embedder ArcFace/FaceNet; identidad NO verificable")
        ref = self.embedder.embed(reference_rgb)
        out = self.embedder.embed(output_rgb)
        for r in (ref, out):
            if getattr(r, "status", None) and r.status.value != "PASS":
                return VerificationResult(
                    "BLOCKED", None, declared_provenance,
                    f"embedding no disponible: {getattr(r, 'reason', r.status)}")
        import math
        a, b = ref.vector, out.vector
        cos = sum(x * y for x, y in zip(a, b)) / (
            math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))
        ok = cos >= self.threshold
        import hashlib, json
        ev = hashlib.sha512(json.dumps(
            {"cos": cos, "prov": declared_provenance},
            sort_keys=True).encode()).hexdigest()
        return VerificationResult(
            "PASS" if ok else "FAIL", ok, declared_provenance,
            f"cosine {cos:.4f} vs umbral {self.threshold}", ev)

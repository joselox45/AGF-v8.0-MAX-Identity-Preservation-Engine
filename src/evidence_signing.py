"""
AGF v9.0 — Firmas criptográficas de evidencia
=============================================
Cadena de custodia append-only con hash encadenado (SHA-512) y firma
Ed25519 cuando `cryptography` está disponible. En entorno de chat sin
dependencias, la cadena de hashes pura sigue siendo verificable, pero
la ausencia de firma asimétrica degrada el registro a UNVERIFIED en
lugar de PASS (fail-closed, coherente con la MTE v1.0).

Contrato de ventana de chat: stdlib-first, salida JSON, sin red.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass, asdict, field
from typing import Optional


def sha512(b: bytes) -> str:
    return hashlib.sha512(b).hexdigest()


# ------------------------------------------------------------------
# Firmantes
# ------------------------------------------------------------------
class Ed25519Signer:
    """Disponible solo si el paquete `cryptography` existe en el host."""
    def __init__(self, seed: Optional[bytes] = None):
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import (
                Ed25519PrivateKey)
        except ImportError:
            self._sk = None
            return
        self._sk = Ed25519PrivateKey.generate() if seed is None \
            else Ed25519PrivateKey.from_private_bytes(seed)

    @property
    def available(self) -> bool:
        return self._sk is not None

    @property
    def public_key_hex(self) -> Optional[str]:
        if not self.available:
            return None
        return self._sk.public_key().public_bytes_raw().hex()

    def sign(self, payload_bytes: bytes) -> Optional[str]:
        if not self.available:
            return None
        return self._sk.sign(payload_bytes).hex()


class HMACFallbackSigner:
    """Último recurso. Marca el registro como UNVERIFIED (no PASS)."""
    def __init__(self, secret: bytes):
        self._secret = secret

    @property
    def available(self):
        return True

    @property
    def public_key_hex(self):
        return "hmac:" + sha512(self._secret)[:32]

    def sign(self, payload_bytes: bytes) -> str:
        return hmac.new(self._secret, payload_bytes, hashlib.sha512).hexdigest()


# ------------------------------------------------------------------
# Registro y cadena de custodia
# ------------------------------------------------------------------
@dataclass
class EvidenceRecord:
    seq: int
    payload: dict
    prev_hash: str
    record_hash: str
    signer_public: Optional[str]
    signature: Optional[str]
    status: str  # PASS | UNVERIFIED
    reason: str = ""


class EvidenceChain:
    GENESIS_PREV = "0" * 128

    def __init__(self, signer):
        self.signer = signer
        self.records: list[EvidenceRecord] = []

    def _canonical(self, payload: dict, prev_hash: str, seq: int) -> bytes:
        return json.dumps({"seq": seq, "payload": payload,
                           "prev_hash": prev_hash},
                          sort_keys=True, ensure_ascii=False).encode()

    def append(self, payload: dict) -> EvidenceRecord:
        seq = len(self.records) + 1
        prev = self.records[-1].record_hash if self.records else self.GENESIS_PREV
        body = self._canonical(payload, prev, seq)
        record_hash = sha512(body)
        signature = self.signer.sign(body)
        asymmetric = not str(getattr(self.signer, "public_key_hex", "")) \
            .startswith("hmac:")
        rec = EvidenceRecord(
            seq=seq, payload=payload, prev_hash=prev,
            record_hash=record_hash,
            signer_public=getattr(self.signer, "public_key_hex", None),
            signature=signature,
            status="PASS" if (signature and asymmetric) else "UNVERIFIED",
            reason="firma Ed25519 válida" if (signature and asymmetric)
                   else "firmante HMAC o sin firma; requiere verificación externa")
        self.records.append(rec)
        return rec

    def verify(self) -> dict:
        """Recorre la cadena completa; cualquier ruptura → FAIL."""
        prev = self.GENESIS_PREV
        for r in self.records:
            body = self._canonical(r.payload, r.prev_hash, r.seq)
            if r.prev_hash != prev or r.record_hash != sha512(body):
                return {"status": "FAIL", "seq": r.seq,
                        "reason": "cadena de hashes rota (alteración detectada)"}
            prev = r.record_hash
        statuses = {r.status for r in self.records}
        final = "PASS" if statuses == {"PASS"} else "UNVERIFIED"
        if not self.records:
            final = "NOT_RUN"
        return {"status": final, "records": len(self.records),
                "tip": "UNVERIFIED no equivale a conformidad (MTE v1.0)"}

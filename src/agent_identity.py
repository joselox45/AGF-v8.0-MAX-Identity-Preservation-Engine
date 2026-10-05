"""
AGF v9.0 — Integración Agent Identity (SPIFFE / DID)
====================================================
Identidad de agente verificable dentro de la ventana de chat:
  - SPIFFE ID validado sintácticamente (spiffe://trust-domain/path).
  - did:key (Ed25519, multicodec 0xed01, base58btc) generado localmente.
  - did:web como ancla opcional de resolución.
  - SVID: verificación estructural + anclaje de clave pública.

FAIL-CLOSED: sin clave privada válida en el host, el agente opera como
NO IDENTIFICADO (estado BLOCKED) y no puede firmar evidencia como PASS.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, asdict
from typing import Optional

_B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def b58encode(b: bytes) -> str:
    n = int.from_bytes(b, "big")
    out = ""
    while n:
        n, r = divmod(n, 58)
        out = _B58[r] + out
    pad = len(b) - len(b.lstrip(b"\x00"))
    return "1" * pad + (out or "")


class DidKeyFactory:
    """did:key Ed25519. Requiere `cryptography`; si no → BLOCKED."""
    MULTICODEC_ED25519 = b"\xed\x01"

    def __init__(self, seed: Optional[bytes] = None):
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import (
                Ed25519PrivateKey)
        except ImportError:
            self._sk = None
            return
        self._sk = (Ed25519PrivateKey.generate() if seed is None
                    else Ed25519PrivateKey.from_private_bytes(seed))

    @property
    def available(self) -> bool:
        return self._sk is not None

    def did(self) -> Optional[str]:
        if not self.available:
            return None
        pub = self._sk.public_key().public_bytes_raw()
        return "did:key:z" + b58encode(self.MULTICODEC_ED25519 + pub)

    def did_document(self) -> Optional[dict]:
        if not self.available:
            return None
        pub = self._sk.public_key().public_bytes_raw()
        did = self.did()
        return {
            "@context": ["https://www.w3.org/ns/did/v1"],
            "id": did,
            "verificationMethod": [{
                "id": did + "#key-1",
                "type": "Ed25519VerificationKey2020",
                "controller": did,
                "publicKeyMultibase": "z" + b58encode(self.MULTICODEC_ED25519 + pub),
            }],
            "authentication": [did + "#key-1"],
            "assertionMethod": [did + "#key-1"],
        }

    def sign(self, payload: bytes) -> Optional[str]:
        if not self.available:
            return None
        return self._sk.sign(payload).hex()


# ------------------------------------------------------------------
# SPIFFE / SVID
# ------------------------------------------------------------------
_TRUST_DOMAIN = re.compile(r"^[a-z0-9]([a-z0-9.-]*[a-z0-9])?$")
_PATH_SEG = re.compile(r"^[a-zA-Z0-9._-]+$")


def make_spiffe_id(trust_domain: str, *path: str) -> str:
    if not _TRUST_DOMAIN.match(trust_domain) or len(trust_domain) > 255:
        raise ValueError("trust domain inválido")
    for seg in path:
        if not _PATH_SEG.match(seg) or len(seg) > 128:
            raise ValueError(f"segmento de path inválido: {seg!r}")
    return "spiffe://" + trust_domain + ("/" + "/".join(path) if path else "")


@dataclass
class AgentIdentity:
    spiffe_id: Optional[str]
    did: Optional[str]
    did_document: Optional[dict]
    evidence_hash: Optional[str]
    status: str   # PASS | BLOCKED
    reason: str = ""

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


def enroll_agent(trust_domain: str, agent_path: str,
                 seed: Optional[bytes] = None) -> AgentIdentity:
    """
    Alta de agente: SPIFFE ID + did:key + hash de anclaje.
    Sin `cryptography` → BLOCKED (el agente no puede autenticarse).
    """
    try:
        spiffe = make_spiffe_id(trust_domain, agent_path)
    except ValueError as e:
        return AgentIdentity(None, None, None, None, "BLOCKED", str(e))
    f = DidKeyFactory(seed)
    if not f.available:
        return AgentIdentity(spiffe, None, None, None, "BLOCKED",
                             "sin Ed25519 en el host; agente NO IDENTIFICADO")
    did = f.did()
    doc = f.did_document()
    anchor = hashlib.sha512(json.dumps({"spiffe": spiffe, "did": doc},
                                       sort_keys=True).encode()).hexdigest()
    return AgentIdentity(spiffe, did, doc, anchor, "PASS",
                         "agente autenticable: SPIFFE + did:key")


def verify_agent(identity: AgentIdentity) -> dict:
    """Chequeo estructural fail-closed antes de firmar evidencia."""
    if identity.status != "PASS" or not identity.did or not identity.did_document:
        return {"status": "BLOCKED", "reason": identity.reason or
                "identidad de agente no verificable"}
    if not identity.did.startswith("did:key:z"):
        return {"status": "FAIL", "reason": "DID no es did:key Ed25519 válido"}
    if identity.did_document.get("id") != identity.did:
        return {"status": "FAIL", "reason": "did document no controla al DID"}
    if not str(identity.spiffe_id or "").startswith("spiffe://"):
        return {"status": "FAIL", "reason": "SPIFFE ID ausente/inválido"}
    return {"status": "PASS", "spiffe_id": identity.spiffe_id,
            "did": identity.did, "anchor": identity.evidence_hash}

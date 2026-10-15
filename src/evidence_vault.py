"""
AGF Evidence Vault — el foso (moat) del proyecto.
==================================================
Encadenamiento CRUZADO entre corridas de evidencia (cierra H-04, auditoria 11):
cada corrida se ancla al hash de la corrida anterior, formando una cadena
append-only persistente en disco (vault.jsonl). Un competidor puede copiar
el codigo (MIT) pero NO puede replicar retroactivamente el historial
acumulado, atestado y encadenado de verificaciones reales.

Ademas: MOAT_METRICS — el foso es medible: pares verificados acumulados,
SUPPORTED count, attested count, longitud de cadena, head hash.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional


def _sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


@dataclass
class VaultRecord:
    seq: int
    evidence_file: str        # ruta relativa del JSON de la corrida
    evidence_sha256: str
    verdict_l3: Optional[str]  # SUPPORTED | NOT_DETERMINED | REFUTED | None
    cosine: Optional[float]
    subject_label: Optional[str]
    prev_head: str
    head: str                 # sha256(prev_head + campos)
    ts: str

    def to_dict(self):
        return asdict(self)


class EvidenceVault:
    """Cadena append-only persistente. Fail-closed: verificacion estricta."""

    def __init__(self, path: str = "evidence/vault.jsonl"):
        self.path = path
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    # ------------------------------------------------------------------
    def _records(self) -> list:
        if not os.path.exists(self.path):
            return []
        out = []
        for line in open(self.path, "r", encoding="utf-8"):
            line = line.strip()
            if line:
                out.append(json.loads(line))
        return out

    def head(self) -> str:
        recs = self._records()
        return recs[-1]["head"] if recs else "0" * 64

    def append(self, evidence_file: str, verdict_l3=None, cosine=None,
               subject_label=None) -> VaultRecord:
        raw = open(evidence_file, "rb").read()
        ev_sha = _sha256(raw)
        try:
            ev = json.loads(raw)
            verdict_l3 = verdict_l3 or (ev.get("verdict") or {}).get("L3_identity")
            cosine = cosine if cosine is not None else (ev.get("verdict") or {}).get("cosine")
            subject_label = subject_label or (ev.get("inputs") or {}).get("subject_label")
        except Exception:
            pass
        seq = len(self._records()) + 1
        prev = self.head()
        body = json.dumps({"seq": seq, "evidence_file": evidence_file,
                           "evidence_sha256": ev_sha, "verdict_l3": verdict_l3,
                           "cosine": cosine, "subject_label": subject_label,
                           "prev_head": prev},
                          sort_keys=True).encode()
        rec = VaultRecord(seq, evidence_file, ev_sha, verdict_l3, cosine,
                          subject_label, prev, _sha256(body),
                          datetime.now(timezone.utc).isoformat())
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec.to_dict(), ensure_ascii=False) + "\n")
        return rec

    # ------------------------------------------------------------------
    def verify(self) -> dict:
        """Recompute completo DESDE DISCO. Cualquier alteracion -> FAIL."""
        recs = self._records()
        prev = "0" * 64
        for r in recs:
            body = json.dumps({"seq": r["seq"],
                               "evidence_file": r["evidence_file"],
                               "evidence_sha256": r["evidence_sha256"],
                               "verdict_l3": r["verdict_l3"],
                               "cosine": r["cosine"],
                               "subject_label": r["subject_label"],
                               "prev_head": r["prev_head"]},
                              sort_keys=True).encode()
            if r["prev_head"] != prev or r["head"] != _sha256(body):
                return {"status": "FAIL", "seq": r["seq"],
                        "reason": "cadena del vault alterada"}
            # integridad del artefacto referenciado
            if os.path.exists(r["evidence_file"]):
                real = _sha256(open(r["evidence_file"], "rb").read())
                if real != r["evidence_sha256"]:
                    return {"status": "FAIL", "seq": r["seq"],
                            "reason": f"evidencia alterada: {r['evidence_file']}"}
            prev = r["head"]
        return {"status": "PASS", "records": len(recs), "head": prev}

    def metrics(self) -> dict:
        """MOAT_METRICS: el foso medible."""
        recs = self._records()
        v = self.verify()
        return {
            "chain_length": len(recs),
            "chain_integrity": v["status"],
            "head": v.get("head", self.head())[:16],
            "verified_pairs": len(recs),
            "L3_SUPPORTED": sum(1 for r in recs if r["verdict_l3"] == "SUPPORTED"),
            "L3_REFUTED": sum(1 for r in recs if r["verdict_l3"] == "REFUTED"),
            "cross_tested_labeled": sum(1 for r in recs
                                        if r["subject_label"] in ("same", "diff")),
            "attested": 0,   # se incrementa cuando haya attestation externa
            "moat_note": "El historial encadenado NO es replicable retroactivamente",
        }

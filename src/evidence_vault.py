"""
AGF Evidence Vault — v1.1 (eslabon: metricas de turno encadenadas).
Retrocompatible: los registros existentes (sin campo metrics) verifican
igual — el cuerpo hash solo incluye campos presentes.
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
    evidence_file: str
    evidence_sha256: str
    verdict_l3: Optional[str]
    cosine: Optional[float]
    subject_label: Optional[str]
    prev_head: str
    head: str
    ts: str
    metrics: Optional[dict] = None      # v1.1: tasas de turno

    def to_dict(self):
        return asdict(self)


BODY_KEYS = ("seq", "evidence_file", "evidence_sha256", "verdict_l3",
             "cosine", "subject_label", "prev_head", "metrics")


def _body(rec: dict) -> bytes:
    """Cuerpo hash: solo campos presentes y no-None (retrocompatible)."""
    d = {k: rec[k] for k in BODY_KEYS
         if k in rec and rec[k] is not None}
    return json.dumps(d, sort_keys=True).encode()


class EvidenceVault:
    def __init__(self, path: str = "evidence/vault.jsonl"):
        self.path = path
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    def _records(self) -> list:
        if not os.path.exists(self.path):
            return []
        return [json.loads(l) for l in open(self.path, encoding="utf-8")
                if l.strip()]

    def head(self) -> str:
        recs = self._records()
        return recs[-1]["head"] if recs else "0" * 64

    def append(self, evidence_file: str, verdict_l3=None, cosine=None,
               subject_label=None, metrics: Optional[dict] = None) -> VaultRecord:
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
        rec = VaultRecord(seq, evidence_file, ev_sha, verdict_l3, cosine,
                          subject_label, prev,
                          _sha256(_body({"seq": seq, "evidence_file": evidence_file,
                                          "evidence_sha256": ev_sha,
                                          "verdict_l3": verdict_l3, "cosine": cosine,
                                          "subject_label": subject_label,
                                          "prev_head": prev, "metrics": metrics})),
                          datetime.now(timezone.utc).isoformat(), metrics)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec.to_dict(), ensure_ascii=False) + "\n")
        return rec

    def append_metrics(self, rates: dict, source: str = "kernel_v3") -> VaultRecord:
        """Ancla un snapshot de MetricasTurno.rates() como registro encadenado."""
        payload = dict(rates); payload["_source"] = source
        tmp = f"{self.path}.metrics_tmp.json"
        json.dump(payload, open(tmp, "w"))
        rec = self.append(tmp, metrics=payload)
        os.unlink(tmp)
        return rec

    def verify(self) -> dict:
        recs = self._records()
        prev = "0" * 64
        for r in recs:
            if r["prev_head"] != prev or r["head"] != _sha256(_body(r)):
                return {"status": "FAIL", "seq": r["seq"],
                        "reason": "cadena del vault alterada"}
            if r["evidence_file"].endswith(".json") and os.path.exists(r["evidence_file"]):
                real = _sha256(open(r["evidence_file"], "rb").read())
                if real != r["evidence_sha256"]:
                    return {"status": "FAIL", "seq": r["seq"],
                            "reason": f"evidencia alterada: {r['evidence_file']}"}
            prev = r["head"]
        return {"status": "PASS", "records": len(recs), "head": prev}

    def metrics(self) -> dict:
        recs = self._records()
        v = self.verify()
        snaps = [r for r in recs if r.get("metrics")]
        return {
            "chain_length": len(recs),
            "chain_integrity": v["status"],
            "head": (v.get("head") or self.head())[:16],
            "verified_pairs": sum(1 for r in recs if not r.get("metrics")),
            "metric_snapshots": len(snaps),
            "L3_SUPPORTED": sum(1 for r in recs if r["verdict_l3"] == "SUPPORTED"),
            "L3_REFUTED": sum(1 for r in recs if r["verdict_l3"] == "REFUTED"),
            "cross_tested_labeled": sum(1 for r in recs
                                        if r["subject_label"] in ("same", "diff")),
            "attested": 0,
            "moat_note": "El historial encadenado NO es replicable retroactivamente",
        }

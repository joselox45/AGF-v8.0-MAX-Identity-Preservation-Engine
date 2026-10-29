"""
AGF Chat Runtime v0.1 — EVIDENCE WRITER
=======================================
Cadena de custodia append-only (SHA-512 encadenado) del ciclo completo:
intake -> kernel -> dispatch -> capture -> verification -> decision.
Compatible en formato con v9.0 evidence_signing (campo canonical idéntico).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from typing import Optional

GENESIS = "0" * 128


@dataclass
class RuntimeEvidence:
    seq: int
    event: str                 # INTAKE | KERNEL | DISPATCH | CAPTURE |
                               # VERIFY | DECISION | BLOCK | ACCEPT
    payload: dict
    prev_hash: str
    record_hash: str
    status: str                # PASS | UNVERIFIED | FAIL | BLOCKED

    def to_dict(self):
        return asdict(self)


class EvidenceWriter:
    def __init__(self):
        self.records: list[RuntimeEvidence] = []

    def record(self, event: str, payload: dict,
               status: str = "PASS") -> RuntimeEvidence:
        seq = len(self.records) + 1
        prev = self.records[-1].record_hash if self.records else GENESIS
        body = json.dumps({"seq": seq, "event": event, "payload": payload,
                           "prev_hash": prev},
                          sort_keys=True, ensure_ascii=False).encode()
        rec = RuntimeEvidence(seq, event, payload, prev,
                              hashlib.sha512(body).hexdigest(), status)
        self.records.append(rec)
        return rec

    def verify(self) -> dict:
        prev = GENESIS
        for r in self.records:
            body = json.dumps({"seq": r.seq, "event": r.event,
                               "payload": r.payload, "prev_hash": r.prev_hash},
                              sort_keys=True, ensure_ascii=False).encode()
            if r.prev_hash != prev or r.record_hash != hashlib.sha512(body).hexdigest():
                return {"status": "FAIL", "seq": r.seq,
                        "reason": "cadena de evidencia alterada"}
            prev = r.record_hash
        return {"status": "PASS" if self.records else "NOT_RUN",
                "records": len(self.records)}

    def dump(self) -> str:
        return json.dumps([r.to_dict() for r in self.records],
                          indent=2, ensure_ascii=False)
